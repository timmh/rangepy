from importlib import metadata as importlib_metadata

from .core import get_species_range, list_available_sources, search_species

try:
    __version__ = importlib_metadata.version(__name__)
except importlib_metadata.PackageNotFoundError:
    __version__ = "0.0.0"

__all__ = ["get_species_range", "list_available_sources", "search_species", "__version__"]
