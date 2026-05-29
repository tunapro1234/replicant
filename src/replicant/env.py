"""
Tiny .env loader (no dependency).

Explicit by design — scripts call load_dotenv() at startup; the library itself
never auto-loads on import. Existing environment variables win (setdefault), so
an explicitly exported value always overrides the file.
"""

import os
from pathlib import Path


def load_dotenv(path: str = None) -> bool:
    """Load KEY=VALUE lines from a .env into os.environ.

    If path is None, search the current working directory and its parents for
    a .env file. Returns True if a file was found and read.
    """
    if path is None:
        for d in [Path.cwd(), *Path.cwd().parents]:
            cand = d / ".env"
            if cand.exists():
                path = cand
                break
    if not path or not Path(path).exists():
        return False

    for line in Path(path).read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        os.environ.setdefault(key.strip(), val.strip().strip('"').strip("'"))
    return True
