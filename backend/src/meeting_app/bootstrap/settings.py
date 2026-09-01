import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class Settings:
    data_directory: Path
    static_directory: Path | None = None

    @classmethod
    def from_environment(cls) -> "Settings":
        value = os.environ.get("MEETING_APP_DATA_DIR", "./data")
        static_value = os.environ.get("MEETING_APP_STATIC_DIR")
        static_directory = (
            Path(static_value).expanduser().resolve() if static_value is not None else None
        )
        return cls(
            data_directory=Path(value).expanduser().resolve(),
            static_directory=static_directory,
        )
