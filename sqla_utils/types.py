"""Type definitions for sqla-utils."""

from typing import TypeAlias, TypeVarTuple

from sqlalchemy.engine.row import Row

_Ts = TypeVarTuple("_Ts")

RowType: TypeAlias = Row[*_Ts]
