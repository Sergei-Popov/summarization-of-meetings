import ast
from pathlib import Path

import pytest

SOURCE_ROOT = Path(__file__).resolve().parents[1] / "src" / "meeting_app"

FORBIDDEN_IMPORTS = {
    "domain": frozenset({"application", "ports", "platform", "entrypoints", "bootstrap"}),
    "ports": frozenset({"application", "platform", "entrypoints", "bootstrap"}),
    "application": frozenset({"platform", "entrypoints", "bootstrap"}),
    "platform": frozenset({"application", "entrypoints", "bootstrap"}),
    "entrypoints": frozenset({"platform", "bootstrap"}),
}


def _layer(path: Path, source_root: Path = SOURCE_ROOT) -> str | None:
    parts = path.relative_to(source_root).parts
    return next((name for name in FORBIDDEN_IMPORTS if name in parts), None)


def _package(path: Path, source_root: Path) -> tuple[str, ...]:
    relative = path.relative_to(source_root)
    directories = relative.parts[:-1]
    return ("meeting_app", *directories)


def _resolve_import_from(node: ast.ImportFrom, package: tuple[str, ...]) -> str:
    if node.level == 0:
        return node.module or ""
    keep = len(package) - (node.level - 1)
    if keep < 1:
        return ""
    parts = (*package[:keep], *((node.module or "").split(".") if node.module else ()))
    return ".".join(parts)


def _imports(path: Path, source_root: Path = SOURCE_ROOT) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    package = _package(path, source_root)
    imports: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            base = _resolve_import_from(node, package)
            if base:
                imports.append(base)
                imports.extend(
                    f"{base}.{alias.name}" for alias in node.names if alias.name != "*"
                )
    return [name for name in imports if name == "meeting_app" or name.startswith("meeting_app.")]


def _violations(source_root: Path) -> list[str]:
    violations: list[str] = []
    for path in source_root.rglob("*.py"):
        layer = _layer(path, source_root)
        if layer is None:
            continue
        for imported in _imports(path, source_root):
            imported_parts = frozenset(imported.split("."))
            if imported_parts & FORBIDDEN_IMPORTS[layer]:
                violations.append(f"{path.relative_to(source_root)} -> {imported}")
    return violations


def test_hexagonal_dependencies_point_inward() -> None:
    assert _violations(SOURCE_ROOT) == []


@pytest.mark.parametrize(
    ("relative_file", "source", "forbidden_target"),
    [
        (
            "modules/fixture/domain/model.py",
            "from .. import application\n",
            "meeting_app.modules.fixture.application",
        ),
        (
            "modules/fixture/domain/model.py",
            "from .... import platform as adapters\n",
            "meeting_app.platform",
        ),
        (
            "modules/fixture/ports/gateway.py",
            "from meeting_app import entrypoints\n",
            "meeting_app.entrypoints",
        ),
        (
            "modules/fixture/application/service.py",
            "from meeting_app.platform import storage\n",
            "meeting_app.platform",
        ),
    ],
)
def test_gate_rejects_relative_and_package_alias_imports(
    tmp_path: Path,
    relative_file: str,
    source: str,
    forbidden_target: str,
) -> None:
    source_root = tmp_path / "meeting_app"
    fixture = source_root / relative_file
    fixture.parent.mkdir(parents=True)
    fixture.write_text(source, encoding="utf-8")

    violations = _violations(source_root)

    assert violations
    assert any(forbidden_target in violation for violation in violations)


def test_required_seed_boundaries_exist() -> None:
    for directory in ("modules", "platform", "entrypoints", "bootstrap"):
        assert (SOURCE_ROOT / directory).is_dir(), directory
