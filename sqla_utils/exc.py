from __future__ import annotations

from typing import Any


class DataError(Exception):
    """Base class for sqla-utils exceptions."""


class UnknownItemError(DataError):
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
        value: Any = None,
        *,
        msg: str | None = None,
    ) -> None:
        if msg is None:
            msg = f"unknown '{item_type}' item"
            if field:
                msg += f", no {field} with value '{value!r}'"
        super().__init__(msg)
        self.item_type = item_type
        self.field = field
        self.value = value
