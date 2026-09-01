from pathlib import Path

import pytest
from verify_release import _scan_bundle, verify_release


def _bundle(tmp_path: Path, *, nested_name: str, nested_content: str) -> Path:
    dist = tmp_path / "dist"
    assets = dist / "assets" / "nested"
    assets.mkdir(parents=True)
    (dist / "index.html").write_text(
        '<!doctype html><script type="module" src="/assets/nested/app.js"></script>',
        encoding="utf-8",
    )
    (assets / "app.js").write_text("window.appReady=true", encoding="utf-8")
    (assets / nested_name).write_text(nested_content, encoding="utf-8")
    return dist


def test_release_contracts() -> None:
    verify_release()


def test_bundle_gate_requires_generated_dist(tmp_path: Path) -> None:
    with pytest.raises(AssertionError, match="must exist"):
        _scan_bundle(tmp_path / "missing")


@pytest.mark.parametrize(
    ("name", "content", "message"),
    [
        ("remote.js", 'fetch("https://remote.example/api")', "remote URL"),
        ("protocol.js", 'const asset = "//cdn.example/app.js"', "remote URL"),
        ("url.css", ".hero{background:url(//cdn.example/image.png)}", "remote URL"),
        ("import.css", '@import "https://cdn.example/theme.css";', "remote URL"),
        ("telemetry.js", "const telemetry = true", "telemetry marker"),
    ],
)
def test_bundle_gate_rejects_nested_remote_and_telemetry_fixtures(
    tmp_path: Path, name: str, content: str, message: str
) -> None:
    with pytest.raises(AssertionError, match=message):
        _scan_bundle(_bundle(tmp_path, nested_name=name, nested_content=content))


def test_bundle_gate_accepts_recursive_local_assets(tmp_path: Path) -> None:
    dist = _bundle(
        tmp_path,
        nested_name="local.css",
        nested_content=".hero{background:url(../image.png)}",
    )
    _scan_bundle(dist)
