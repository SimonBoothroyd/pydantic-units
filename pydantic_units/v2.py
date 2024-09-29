"""OpenMM Quantity type for Pydantic v2."""

from functools import partial
from typing import TYPE_CHECKING, Annotated, Any

from openmm.unit import Quantity, Unit
from pydantic import BeforeValidator, GetCoreSchemaHandler, GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import CoreSchema
from pydantic_core.core_schema import (
    json_or_python_schema,
    no_info_plain_validator_function,
    plain_serializer_function_ser_schema,
    str_schema,
)

from pydantic_units._common import quantity_serializer, quantity_validator


class _OpenMMQuantityAnnotation:
    @classmethod
    def __get_pydantic_core_schema__(
        cls,
        _source_type: Any,
        _handler: GetCoreSchemaHandler,
    ) -> CoreSchema:
        from_value_schema = no_info_plain_validator_function(lambda x: x)

        return json_or_python_schema(
            json_schema=from_value_schema,
            python_schema=from_value_schema,
            serialization=plain_serializer_function_ser_schema(quantity_serializer),
        )

    @classmethod
    def __get_pydantic_json_schema__(
        cls, _core_schema: CoreSchema, handler: GetJsonSchemaHandler
    ) -> JsonSchemaValue:
        return handler(str_schema())


class _OpenMMQuantityMeta(type):
    def __getitem__(cls, item: Unit):
        validator = partial(quantity_validator, expected_units=item)

        return Annotated[
            Quantity, _OpenMMQuantityAnnotation, BeforeValidator(validator)
        ]


class OpenMMQuantity(Quantity, metaclass=_OpenMMQuantityMeta):
    """A pydantic safe OpenMM quantity type that validates unit compatibility."""


if TYPE_CHECKING:
    OpenMMQuantity = Quantity  # noqa: F811

__all__ = ["OpenMMQuantity"]
