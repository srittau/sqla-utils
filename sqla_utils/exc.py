"""Exception classes for sqla-utils."""

from __future__ import annotations

from typing import Generic
from typing_extensions import TypeVar

_V = TypeVar("_V", default=object)


class DataError(Exception):
    """Base class for sqla-utils exceptions."""


class DataItemError(DataError, Generic[_V]):
    """Base class for sqla-utils exceptions related to a specific item."""

    def __init__(
        self,
        item_type: str,
        field: str | None,
        value: _V,
        *,
        msg: str,
    ) -> None:
        """Create a new data item error."""
        super().__init__(msg)
        self.item_type = item_type
        self.field = field
        self.value = value


class UnknownItemError(DataItemError[_V | None], Generic[_V]):
    """An unknown item was queried.

    By default, a message a is generated from the supplied attributes, but
    a custom message can be provided.

    Arguments and fields:
    item_type -- the kind item that failed to query, often the table name
    field -- the field the query failed on, often a column name
    value -- the value queried
    """

    def __init__(
        self,
        item_type: str,
        field: str | None = None,
        value: _V | None = None,
        *,
        msg: str | None = None,
    ) -> None:
        """Create a new unknown item error."""
        if msg is None:
            msg = f"unknown '{item_type}' item"
            if field:
                msg += f", no {field} with value '{value!r}'"
        super().__init__(item_type, field, value, msg=msg)


class DuplicateItemError(DataItemError[_V | None], Generic[_V]):
    """A item can't be created because it already exists.

    By default, a message a is generated from the supplied attributes, but
    a custom message can be provided.

    Arguments and fields:
    item_type -- the kind item that failed to query, often the table name
    field -- the field the query failed on, often a column name
    value -- the value queried
    """

    def __init__(
        self,
        item_type: str,
        field: str | None = None,
        value: _V | None = None,
        *,
        msg: str | None = None,
    ) -> None:
        """Create a new duplicate item error."""
        if msg is None:
            msg = f"duplicate '{item_type}' item"
            if field:
                msg += f" with value '{value!r}' for {field}"
        super().__init__(item_type, field, value, msg=msg)
