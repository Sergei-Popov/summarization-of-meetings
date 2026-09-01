from __future__ import annotations

import json
import re
import sys
import tomllib
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from deploy.release.generate_inventory import (  # noqa: E402
    _python_runtime_components,
    build_documents,
    locked_node_runtime_identities,
)

EXPECTED_TOOLCHAIN = {
    "python": "3.13.15",
    "uv": "0.11.21",
    "node": "24.20.0",
    "pnpm": "11.1.3",
    "sqlite": "3.53.4",
    "fastapi": "0.141.1",
    "sqlalchemy": "2.0.52",
    "alembic": "1.19.1",
    "react": "19.2.7",
    "antd": "6.6.2",
    "typescript": "6.0.3",
    "vite": "8.2.2",
    "compose": "5.4.0",
}

ALLOWED_INERT_BUNDLE_URLS = (
    "http://www.w3.org/",
    "https://react.dev/errors/",
)
REMOTE_URL = re.compile(r"https?://[^\s\"'`)<]+|(?<!:)//[A-Za-z0-9][^\s\"'`)<]+")
TELEMETRY = re.compile(
    r"\b(?:analytics|telemetry|sentry|googletagmanager|mixpanel|amplitude|newrelic|datadog)\b",
    re.IGNORECASE,
)
EXACT_PYTHON_PIN = re.compile(r"^[A-Za-z0-9_.-]+(?:\[[^]]+\])?==[^*~^,<>=\s]+$")
EXACT_NPM_PIN = re.compile(r"^\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?$")


def _read(path: str) -> str:
    return (PROJECT_ROOT / path).read_text(encoding="utf-8")


def _scan_bundle(bundle_root: Path) -> None:
    if not bundle_root.is_dir():
        raise AssertionError("frontend/dist must exist before release verification")
    emitted = sorted(
        path for path in bundle_root.rglob("*") if path.suffix.lower() in {".html", ".js", ".css"}
    )
    if not emitted or not (bundle_root / "index.html").is_file():
        raise AssertionError("frontend/dist must contain emitted index.html and local assets")
    for path in emitted:
        content = path.read_text(encoding="utf-8")
        telemetry = TELEMETRY.search(content)
        if telemetry is not None:
            raise AssertionError(
                f"telemetry marker in emitted bundle: {path.name}:{telemetry.group(0)}"
            )
        for match in REMOTE_URL.finditer(content):
            url = match.group(0)
            if not url.startswith(ALLOWED_INERT_BUNDLE_URLS):
                raise AssertionError(f"remote URL in emitted bundle: {path.name}:{url}")
        if path.suffix.lower() == ".css":
            remote_css = re.search(
                r"(?:@import\s+(?:url\()?|url\()[\s\"']*(?:https?:)?//",
                content,
                flags=re.IGNORECASE,
            )
            if remote_css is not None:
                raise AssertionError(f"remote CSS dependency in emitted bundle: {path.name}")

    index = (bundle_root / "index.html").read_text(encoding="utf-8")
    asset_paths = re.findall(r"(?:src|href)=[\"'](/[^\"']+)[\"']", index)
    if not asset_paths:
        raise AssertionError("emitted index.html must reference a local asset")
    for asset in asset_paths:
        if not (bundle_root / asset.lstrip("/")).is_file():
            raise AssertionError(f"referenced local asset is missing: {asset}")


def _verify_inventory(manifest: dict[str, Any]) -> None:
    for inventory_path in manifest["inventory"].values():
        inventory = PROJECT_ROOT / inventory_path
        assert inventory.is_file() and inventory.stat().st_size > 0
        json.loads(inventory.read_text(encoding="utf-8"))

    licenses = json.loads(_read(manifest["inventory"]["thirdPartyLicenses"]))
    components = licenses["components"]
    assert components == sorted(
        components,
        key=lambda item: (item["ecosystem"], item["name"], item["version"]),
    )
    component_identities = {
        (item["ecosystem"], item["name"], item["version"]) for item in components
    }
    expected_identities = {
        ("source", "SQLite", EXPECTED_TOOLCHAIN["sqlite"]),
        *{
            ("PyPI", item["name"], item["version"])
            for item in _python_runtime_components()
        },
        *{
            ("npm", name, version) for name, version in locked_node_runtime_identities()
        },
    }
    assert component_identities == expected_identities
    assert all(item["license"] and item["license"] != "NOASSERTION" for item in components)

    sbom = json.loads(_read(manifest["inventory"]["sbom"]))
    assert sbom["documentNamespace"].startswith("urn:uuid:")
    assert "example.invalid" not in json.dumps(sbom)
    sbom_components = {
        (package["name"], package["versionInfo"], package["licenseDeclared"])
        for package in sbom["packages"]
        if package["name"] != "meeting-app"
    }
    assert sbom_components == {
        (item["name"], item["version"], item["license"]) for item in components
    }
    dependencies = {
        relationship["relatedSpdxElement"]
        for relationship in sbom["relationships"]
        if relationship["relationshipType"] == "DEPENDS_ON"
    }
    package_ids = {
        package["SPDXID"] for package in sbom["packages"] if package["name"] != "meeting-app"
    }
    assert dependencies == package_ids

    if (PROJECT_ROOT / "frontend/node_modules").is_dir():
        generated_licenses, generated_sbom = build_documents()
        assert licenses == generated_licenses
        assert sbom == generated_sbom


def _verify_exact_pins() -> None:
    pyproject = tomllib.loads(_read("backend/pyproject.toml"))
    assert pyproject["project"]["requires-python"] == "==3.13.15"
    python_pins = [
        *pyproject["project"]["dependencies"],
        *[
            dependency
            for group in pyproject["dependency-groups"].values()
            for dependency in group
        ],
        *pyproject["build-system"]["requires"],
    ]
    assert python_pins and all(EXACT_PYTHON_PIN.fullmatch(pin) for pin in python_pins)
    lock = tomllib.loads(_read("backend/uv.lock"))
    assert lock["requires-python"] == "==3.13.15"
    assert _read(".python-version").strip() == EXPECTED_TOOLCHAIN["python"]

    package = json.loads(_read("frontend/package.json"))
    assert package["packageManager"] == f"pnpm@{EXPECTED_TOOLCHAIN['pnpm']}"
    assert package["engines"] == {
        "node": EXPECTED_TOOLCHAIN["node"],
        "pnpm": EXPECTED_TOOLCHAIN["pnpm"],
    }
    frontend_pins = package["dependencies"] | package["devDependencies"]
    assert frontend_pins and all(EXACT_NPM_PIN.fullmatch(pin) for pin in frontend_pins.values())


def _verify_ci_and_docs() -> None:
    workflow = _read(".github/workflows/ci.yml")
    assert re.search(r"uses:\s+[^\s]+@(?![0-9a-f]{40}(?:\s|$))", workflow) is None
    assert all(platform in workflow for platform in ("ubuntu-24.04", "macos-15", "windows-2025"))
    assert "docker-compose-linux-x86_64" in workflow
    assert "837fd1d35bf6a494f41b5b5988269a7be79de337cf1a1a6ff0e45ab51bb4e9be" in workflow
    assert 'test "$(docker compose version --short)" = "5.4.0"' in workflow
    assert "docker compose up --build --wait" in workflow
    assert "docker build --target backend-verify --file deploy/app.Dockerfile ." in workflow
    assert "http://127.0.0.1:8000/api/v1/health" in workflow
    assert "http://127.0.0.1:8000/" in workflow
    assert "if: always()" in workflow
    assert "docker compose down --volumes --remove-orphans" in workflow
    assert "pytest -c backend/pyproject.toml backend/tests tests/release" in workflow
    assert "mypy --config-file backend/pyproject.toml backend/src" in workflow

    readme = _read("README.md")
    assert "docker volume inspect" not in readme
    assert "docker compose cp app:/var/lib/meeting-app/meeting-app.sqlite3" in readme
    assert "--cap-add CHOWN --entrypoint chown" in readme
    assert "docker build --target backend-verify --file deploy/app.Dockerfile ." in readme
    assert "не считается доказательством exact Python" in readme


def verify_release() -> None:
    manifest = json.loads(_read("deploy/release/manifest.json"))
    assert manifest["toolchain"] == EXPECTED_TOOLCHAIN
    assert manifest["application"]["license"] == "Apache-2.0"
    assert manifest["application"]["imageReferenceTemplate"] == (
        "meeting-app@sha256:<64-hex-digest>"
    )
    baseline = manifest["application"]["implementationBaselineRevision"]
    assert re.fullmatch(r"[0-9a-f]{40}", baseline)
    spec = _read(
        "_bmad-output/implementation-artifacts/"
        "spec-1-1-zapusk-lokalnogo-prilozheniya-iz-vosproizvodimogo-karkasa.md"
    )
    assert f"baseline_commit: '{baseline}'" in spec

    dockerfile = _read("deploy/app.Dockerfile")
    docker_base_images = set(
        re.findall(r"^ARG [A-Z]+_IMAGE=(.+@sha256:[0-9a-f]{64})$", dockerfile, re.MULTILINE)
    )
    assert docker_base_images
    assert set(manifest["baseImages"]) == docker_base_images
    assert all(re.search(r"@sha256:[0-9a-f]{64}$", image) for image in manifest["baseImages"])
    assert "example.invalid" not in dockerfile
    assert "SQLITE_VERSION=3.53.4" in dockerfile
    sqlite_sha256 = "0e9483900e92cd5de8fd48d16bf9200145a61f7fd5be542a5ac81d8a9516eb9c"
    assert f"SQLITE_SHA256={sqlite_sha256}" in dockerfile
    assert "uv==0.11.21" in dockerfile and "pnpm@11.1.3" in dockerfile
    assert "--frozen" in dockerfile and "--frozen-lockfile" in dockerfile
    assert "/models" not in dockerfile

    _verify_exact_pins()
    _verify_inventory(manifest)
    _verify_ci_and_docs()

    compose = _read("compose.yaml")
    assert '"127.0.0.1:${MEETING_APP_PORT:-8000}:8000"' in compose
    assert "0.0.0.0:" not in compose
    assert "meeting-data:/var/lib/meeting-app" in compose
    assert 'restart: "no"' in compose
    assert "local-worker" not in compose and "model-fetch" not in compose

    license_text = _read("LICENSE")
    assert "Apache License" in license_text and "Version 2.0, January 2004" in license_text
    assert (PROJECT_ROOT / "NOTICE").stat().st_size > 0

    example_lines = [
        line.strip()
        for line in _read(".env.example").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    allowed_keys = {"MEETING_APP_PORT", "MEETING_APP_IMAGE"}
    assert all(line.split("=", 1)[0] in allowed_keys for line in example_lines)
    assert all(
        "secret" not in line.lower() and "token" not in line.lower() for line in example_lines
    )
    dockerignore = _read(".dockerignore")
    assert all(candidate in dockerignore for candidate in ("*.pem", "*.key", "*secret*"))
    for ignored in (".env", "data/", "models/", "frontend/dist/"):
        assert ignored in _read(".gitignore")

    generated_schema = _read("frontend/src/api/generated/schema.ts")
    assert '"application/problem+json": components["schemas"]["ProblemDetails"]' in (
        generated_schema
    )
    _scan_bundle(PROJECT_ROOT / "frontend/dist")


if __name__ == "__main__":
    verify_release()
    print("release verification: ok")
