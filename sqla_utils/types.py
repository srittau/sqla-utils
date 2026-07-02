"""Type definitions for sqla-utils."""

from typing import Any, TypeAlias, TypeVar

from sqlalchemy.engine.row import Row

_TP = TypeVar("_TP", bound=tuple[Any, ...])

RowType: TypeAlias = Row[_TP]
