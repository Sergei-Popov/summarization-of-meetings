from __future__ import annotations

import json
import re
import shutil
import subprocess
import tomllib
import uuid
from pathlib import Path
from typing import Any
from urllib.parse import quote

PROJECT_ROOT = Path(__file__).resolve().parents[2]

PYTHON_LICENSES = {
    "alembic": "MIT",
    "annotated-doc": "MIT",
    "annotated-types": "MIT",
    "anyio": "MIT",
    "click": "BSD-3-Clause",
    "fastapi": "MIT",
    "greenlet": "MIT AND PSF-2.0",
    "h11": "MIT",
    "idna": "BSD-3-Clause",
    "mako": "MIT",
    "markupsafe": "BSD-3-Clause",
    "pydantic": "MIT",
    "pydantic-core": "MIT",
    "sqlalchemy": "MIT",
    "starlette": "BSD-3-Clause",
    "typing-extensions": "PSF-2.0",
    "typing-inspection": "MIT",
    "uvicorn": "BSD-3-Clause",
}

Component = dict[str, str]


def _unquote_yaml(value: str) -> str:
    value = value.strip()
    if len(value) > 1 and value[0] == value[-1] == "'":
        return value[1:-1].replace("''", "'")
    if len(value) > 1 and value[0] == value[-1] == '"':
        return value[1:-1]
    return value


def locked_node_runtime_identities() -> set[tuple[str, str]]:
    lock_lines = (PROJECT_ROOT / "frontend/pnpm-lock.yaml").read_text(
        encoding="utf-8"
    ).splitlines()
    snapshots: dict[str, list[tuple[str, str]]] = {}
    current: str | None = None
    section = ""
    in_snapshots = False
    for line in lock_lines:
        if line == "snapshots:":
            in_snapshots = True
            continue
        if not in_snapshots:
            continue
        indentation = len(line) - len(line.lstrip())
        stripped = line.strip()
        if indentation == 2 and stripped:
            if stripped.startswith("'") and "':" in stripped:
                current = stripped[1 : stripped.index("':")]
            else:
                current = _unquote_yaml(stripped.split(":", 1)[0])
            snapshots[current] = []
            section = ""
        elif indentation == 4 and stripped.endswith(":"):
            section = stripped[:-1]
        elif (
            indentation == 6
            and current is not None
            and ":" in stripped
            and section in {"dependencies", "optionalDependencies"}
        ):
            name, version = stripped.split(":", 1)
            snapshots[current].append((_unquote_yaml(name), _unquote_yaml(version)))

    package = json.loads((PROJECT_ROOT / "frontend/package.json").read_text(encoding="utf-8"))
    pending: list[str] = []

    def matching_snapshots(name: str, version: str) -> list[str]:
        exact = f"{name}@{version}"
        matches = [key for key in snapshots if key == exact or key.startswith(f"{exact}(")]
        if matches:
            return matches
        base_version = version.split("(", 1)[0]
        base = f"{name}@{base_version}"
        return [key for key in snapshots if key == base or key.startswith(f"{base}(")]

    for name, version in package["dependencies"].items():
        pending.extend(matching_snapshots(name, version))

    closure: set[str] = set()
    while pending:
        key = pending.pop()
        if key in closure:
            continue
        closure.add(key)
        for name, version in snapshots[key]:
            pending.extend(matching_snapshots(name, version))

    identities: set[tuple[str, str]] = set()
    for key in closure:
        match = re.match(r"^(@[^/]+/[^@]+|[^@]+)@([^()]+)", key)
        if match is None:
            raise RuntimeError(f"cannot parse pnpm snapshot identity: {key}")
        identities.add((match.group(1), match.group(2)))
    if not identities:
        raise RuntimeError("pnpm lock contains an empty runtime dependency closure")
    return identities


def _python_runtime_components() -> list[Component]:
    lock = tomllib.loads((PROJECT_ROOT / "backend/uv.lock").read_text(encoding="utf-8"))
    packages = {package["name"]: package for package in lock["package"]}
    pending = [item["name"] for item in packages["meeting-app"]["dependencies"]]
    runtime: set[str] = set()
    while pending:
        name = pending.pop()
        if name in runtime:
            continue
        runtime.add(name)
        pending.extend(item["name"] for item in packages[name].get("dependencies", []))
    if runtime != PYTHON_LICENSES.keys():
        missing = sorted(runtime - PYTHON_LICENSES.keys())
        stale = sorted(PYTHON_LICENSES.keys() - runtime)
        raise RuntimeError(f"python license map mismatch: missing={missing}, stale={stale}")
    return [
        {
            "ecosystem": "PyPI",
            "name": name,
            "version": packages[name]["version"],
            "license": PYTHON_LICENSES[name],
        }
        for name in sorted(runtime)
    ]


def _license_expression(package: dict[str, Any]) -> str:
    license_value = package.get("license") or package.get("licenses")
    if isinstance(license_value, str) and license_value.strip():
        return license_value.strip()
    if isinstance(license_value, dict):
        value = license_value.get("type")
        if isinstance(value, str) and value.strip():
            return value.strip()
    if isinstance(license_value, list):
        values = [
            item if isinstance(item, str) else item.get("type", "")
            for item in license_value
            if isinstance(item, (str, dict))
        ]
        normalized = sorted({value.strip() for value in values if value.strip()})
        if normalized:
            return " OR ".join(normalized)
    raise RuntimeError(f"missing npm license metadata for {package.get('name')}")


def _node_runtime_components() -> list[Component]:
    pnpm = shutil.which("pnpm")
    if pnpm is None:
        raise RuntimeError("pnpm is required to generate the shipped frontend inventory")
    result = subprocess.run(
        [pnpm, "--dir", "frontend", "list", "--prod", "--depth", "Infinity", "--json"],
        cwd=PROJECT_ROOT,
        check=True,
        capture_output=True,
        text=True,
        timeout=30,
    )
    roots = json.loads(result.stdout)
    if len(roots) != 1:
        raise RuntimeError("unexpected pnpm list output")
    identities: dict[tuple[str, str], Path] = {}

    def walk(dependencies: dict[str, Any]) -> None:
        for name, metadata in dependencies.items():
            version = metadata.get("version")
            path = metadata.get("path")
            if isinstance(version, str) and isinstance(path, str):
                identities[(name, version)] = Path(path)
            nested = metadata.get("dependencies", {})
            if isinstance(nested, dict):
                walk(nested)

    walk(roots[0].get("dependencies", {}))
    if not identities:
        raise RuntimeError("pnpm produced an empty runtime dependency closure")
    locked_identities = locked_node_runtime_identities()
    if identities.keys() != locked_identities:
        missing = sorted(locked_identities - identities.keys())
        extra = sorted(identities.keys() - locked_identities)
        raise RuntimeError(f"installed npm closure mismatch: missing={missing}, extra={extra}")
    components: list[Component] = []
    for (name, version), package_path in sorted(identities.items()):
        package = json.loads((package_path / "package.json").read_text(encoding="utf-8"))
        components.append(
            {
                "ecosystem": "npm",
                "name": name,
                "version": version,
                "license": _license_expression(package),
            }
        )
    return components


def runtime_components() -> list[Component]:
    manifest = json.loads(
        (PROJECT_ROOT / "deploy/release/manifest.json").read_text(encoding="utf-8")
    )
    components = [
        {
            "ecosystem": "source",
            "name": "SQLite",
            "version": manifest["toolchain"]["sqlite"],
            "license": "blessing",
        },
        *_python_runtime_components(),
        *_node_runtime_components(),
    ]
    return sorted(components, key=lambda item: (item["ecosystem"], item["name"], item["version"]))


def _spdx_id(component: Component) -> str:
    raw = f"{component['ecosystem']}-{component['name']}-{component['version']}"
    return "SPDXRef-Package-" + re.sub(r"[^A-Za-z0-9.-]", "-", raw)


def _purl(component: Component) -> str:
    ecosystem = (
        "generic" if component["ecosystem"] == "source" else component["ecosystem"].lower()
    )
    name = quote(component["name"], safe="/")
    version = quote(component["version"], safe=".")
    return f"pkg:{ecosystem}/{name}@{version}"


def build_documents() -> tuple[dict[str, Any], dict[str, Any]]:
    components = runtime_components()
    licenses = {"schemaVersion": 1, "components": components}
    application_id = "SPDXRef-Package-meeting-app"
    namespace = uuid.uuid5(
        uuid.NAMESPACE_URL,
        "meeting-app/0.1.0/" + ",".join(_spdx_id(component) for component in components),
    )
    packages = [
        {
            "name": "meeting-app",
            "SPDXID": application_id,
            "versionInfo": "0.1.0",
            "downloadLocation": "NOASSERTION",
            "filesAnalyzed": False,
            "licenseConcluded": "Apache-2.0",
            "licenseDeclared": "Apache-2.0",
            "copyrightText": "NOASSERTION",
        },
        *[
            {
                "name": component["name"],
                "SPDXID": _spdx_id(component),
                "versionInfo": component["version"],
                "downloadLocation": "NOASSERTION",
                "filesAnalyzed": False,
                "licenseConcluded": component["license"],
                "licenseDeclared": component["license"],
                "copyrightText": "NOASSERTION",
                "externalRefs": [
                    {
                        "referenceCategory": "PACKAGE-MANAGER",
                        "referenceType": "purl",
                        "referenceLocator": _purl(component),
                    }
                ],
            }
            for component in components
        ],
    ]
    relationships = [
        {
            "spdxElementId": "SPDXRef-DOCUMENT",
            "relationshipType": "DESCRIBES",
            "relatedSpdxElement": application_id,
        },
        *[
            {
                "spdxElementId": application_id,
                "relationshipType": "DEPENDS_ON",
                "relatedSpdxElement": _spdx_id(component),
            }
            for component in components
        ],
    ]
    sbom = {
        "spdxVersion": "SPDX-2.3",
        "dataLicense": "CC0-1.0",
        "SPDXID": "SPDXRef-DOCUMENT",
        "name": "meeting-app-0.1.0",
        "documentNamespace": f"urn:uuid:{namespace}",
        "creationInfo": {
            "created": "2026-09-01T00:00:00Z",
            "creators": ["Tool: deploy/release/generate_inventory.py"],
        },
        "packages": packages,
        "relationships": relationships,
    }
    return licenses, sbom


def _write_json(path: Path, document: dict[str, Any]) -> None:
    path.write_text(
        json.dumps(document, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def main() -> None:
    licenses, sbom = build_documents()
    _write_json(PROJECT_ROOT / "deploy/release/third-party-licenses.json", licenses)
    _write_json(PROJECT_ROOT / "deploy/release/sbom.spdx.json", sbom)


if __name__ == "__main__":
    main()
