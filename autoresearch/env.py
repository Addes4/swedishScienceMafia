"""Load KEY=VALUE pairs from the repo's .env into os.environ (existing variables win)."""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLACEHOLDER_PREFIX = "your-"


def load_env(path: Path = ROOT / ".env") -> None:
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key, value = key.strip(), value.strip().strip('"').strip("'")
        if value and not value.startswith(PLACEHOLDER_PREFIX):
            os.environ.setdefault(key, value)


def require(key: str, why: str) -> None:
    if not os.environ.get(key):
        raise SystemExit(f"{key} is not set ({why}). Put it in .env (see .env.example).")
