"""Stock retrieval package scaffolding."""

from importlib.metadata import PackageNotFoundError, version

try:  # pragma: no cover - package metadata optional during development
    __version__ = version("stock_retrieval")
except PackageNotFoundError:  # pragma: no cover - fallback for source usage
    __version__ = "0.0.0"

__all__ = ["__version__"]
