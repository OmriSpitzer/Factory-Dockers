import os
from pathlib import Path

def load_env(path: Path) -> None:
    if not path.exists():
        return

    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))

def get_env(key: str, default: str | int | None = None) -> str | int | None:
    return os.environ.get(key, default)