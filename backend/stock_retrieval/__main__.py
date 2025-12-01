"""Module entrypoint for `python -m stock_retrieval`."""

from __future__ import annotations

import sys

from .cli import main


if __name__ == "__main__":  # pragma: no cover - module execution guard
    sys.exit(main())
