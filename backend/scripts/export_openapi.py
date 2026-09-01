import json
from pathlib import Path

from meeting_app.bootstrap.app import create_app


def main() -> None:
    output = Path(__file__).resolve().parents[2] / "openapi" / "openapi.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(create_app().openapi(), ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
