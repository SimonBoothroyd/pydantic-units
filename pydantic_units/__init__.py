"""Support for OpenMM units as pydantic fields"""

import importlib.metadata

import pydantic

from ._common import quantity_serializer, quantity_validator

if pydantic.__version__.startswith("1."):
    from .v1 import OpenMMQuantity
else:
    from .v2 import OpenMMQuantity

try:
    __version__ = importlib.metadata.version("pydantic-units")
except importlib.metadata.PackageNotFoundError:  # pragma: no cover
    __version__ = "0+unknown"

__all__ = ["OpenMMQuantity", "__version__", "quantity_serializer", "quantity_validator"]
