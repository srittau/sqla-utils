"""Transaction management utilities for SQLAlchemy."""

from __future__ import annotations

from types import TracebackType
from typing import TYPE_CHECKING, Any, Self, TypeVar, TypeVarTuple, overload

from sqlalchemy import text

if TYPE_CHECKING:
    from sqlalchemy.engine import Connection, Result
    from sqlalchemy.engine.interfaces import (
        _CoreAnyExecuteParams,
        _CoreSingleExecuteParams,
    )
    from sqlalchemy.orm import Query, Session
    from sqlalchemy.orm._typing import _EntityType
    from sqlalchemy.orm.query import RowReturningQuery
    from sqlalchemy.sql._typing import (
        _ColumnsClauseArgument,
        _TypedColumnClauseArgument,
    )
    from sqlalchemy.sql.base import Executable
    from sqlalchemy.sql.roles import TypedColumnsClauseRole
    from sqlalchemy.sql.selectable import TypedReturnsRows

_T = TypeVar("_T")
_T0 = TypeVar("_T0")
_T1 = TypeVar("_T1")
_T2 = TypeVar("_T2")
_T3 = TypeVar("_T3")
_T4 = TypeVar("_T4")
_T5 = TypeVar("_T5")
_T6 = TypeVar("_T6")
_T7 = TypeVar("_T7")
_Ts = TypeVarTuple("_Ts")


class Transaction:
    """Wrapper around SQLAlchemy sessions and transactions.

    Can be used as a context manager to create a new transaction
    that will be committed or rollbacked when the context is
    exited.

    >>> with Transaction(...) as t:
    ...     ...
    """

    def __init__(self, session: Session) -> None:
        """Create a new transaction for a session."""
        self.session = session

    @property
    def connection(self) -> Connection:
        """Return the connection for this transaction."""
        return self.session.connection()

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        try:
            self.session.flush()
        except BaseException:
            self.session.rollback()
            raise
        if exc_type:
            self.session.rollback()
        else:
            self.session.commit()

    @overload
    def query(self, _entity: _EntityType[_T]) -> Query[_T]: ...

    @overload
    def query(
        self, _colexpr: TypedColumnsClauseRole[_T]
    ) -> RowReturningQuery[_T]: ...

    # START OVERLOADED FUNCTIONS self.query RowReturningQuery 2-8

    # code within this block is **programmatically,
    # statically generated** by tools/generate_tuple_map_overloads.py

    @overload
    def query(
        self,
        __ent0: _TypedColumnClauseArgument[_T0],
        __ent1: _TypedColumnClauseArgument[_T1],
        /,
    ) -> RowReturningQuery[_T0, _T1]: ...

    @overload
    def query(
        self,
        __ent0: _TypedColumnClauseArgument[_T0],
        __ent1: _TypedColumnClauseArgument[_T1],
        __ent2: _TypedColumnClauseArgument[_T2],
        /,
    ) -> RowReturningQuery[_T0, _T1, _T2]: ...

    @overload
    def query(
        self,
        __ent0: _TypedColumnClauseArgument[_T0],
        __ent1: _TypedColumnClauseArgument[_T1],
        __ent2: _TypedColumnClauseArgument[_T2],
        __ent3: _TypedColumnClauseArgument[_T3],
        /,
    ) -> RowReturningQuery[_T0, _T1, _T2, _T3]: ...

    @overload
    def query(
        self,
        __ent0: _TypedColumnClauseArgument[_T0],
        __ent1: _TypedColumnClauseArgument[_T1],
        __ent2: _TypedColumnClauseArgument[_T2],
        __ent3: _TypedColumnClauseArgument[_T3],
        __ent4: _TypedColumnClauseArgument[_T4],
        /,
    ) -> RowReturningQuery[_T0, _T1, _T2, _T3, _T4]: ...

    @overload
    def query(
        self,
        __ent0: _TypedColumnClauseArgument[_T0],
        __ent1: _TypedColumnClauseArgument[_T1],
        __ent2: _TypedColumnClauseArgument[_T2],
        __ent3: _TypedColumnClauseArgument[_T3],
        __ent4: _TypedColumnClauseArgument[_T4],
        __ent5: _TypedColumnClauseArgument[_T5],
        /,
    ) -> RowReturningQuery[_T0, _T1, _T2, _T3, _T4, _T5]: ...

    @overload
    def query(
        self,
        __ent0: _TypedColumnClauseArgument[_T0],
        __ent1: _TypedColumnClauseArgument[_T1],
        __ent2: _TypedColumnClauseArgument[_T2],
        __ent3: _TypedColumnClauseArgument[_T3],
        __ent4: _TypedColumnClauseArgument[_T4],
        __ent5: _TypedColumnClauseArgument[_T5],
        __ent6: _TypedColumnClauseArgument[_T6],
        /,
    ) -> RowReturningQuery[_T0, _T1, _T2, _T3, _T4, _T5, _T6]: ...

    @overload
    def query(
        self,
        __ent0: _TypedColumnClauseArgument[_T0],
        __ent1: _TypedColumnClauseArgument[_T1],
        __ent2: _TypedColumnClauseArgument[_T2],
        __ent3: _TypedColumnClauseArgument[_T3],
        __ent4: _TypedColumnClauseArgument[_T4],
        __ent5: _TypedColumnClauseArgument[_T5],
        __ent6: _TypedColumnClauseArgument[_T6],
        __ent7: _TypedColumnClauseArgument[_T7],
        /,
        *entities: _ColumnsClauseArgument[Any],
    ) -> RowReturningQuery[
        _T0, _T1, _T2, _T3, _T4, _T5, _T6, _T7, *tuple[Any, ...]
    ]: ...

    @overload
    def query(
        self,
        *entities: _ColumnsClauseArgument[Any],
        **kwargs: Any,  # noqa: ANN401
    ) -> Query[Any]: ...

    def query(
        self, *entities: _ColumnsClauseArgument[Any], **kwargs: Any
    ) -> Query[Any]:
        """Execute a query against the database.

        Simple wrapper around Session.query().
        """
        return self.session.query(*entities, **kwargs)

    def add(self, *instances: Any) -> None:  # noqa: ANN401
        """Save one or more objects to the database."""
        self.session.add_all(instances)
        self.flush(*instances)

    def delete(self, *instances: Any) -> None:  # noqa: ANN401
        """Mark one or more instances as deleted."""
        for obj in instances:
            self.session.delete(obj)
        self.flush(*instances)

    def flush(self, *objects: Any) -> None:  # noqa: ANN401
        """Flush object changes to the database.

        As opposed to Session.flush() this takes the objects
        to flush as positional arguments. Flush all changes
        if no objects are provided.
        """
        if len(objects) == 0:
            self.session.flush()
        else:
            self.session.flush(objects)

    def refresh(self, *instances: Any) -> None:  # noqa: ANN401
        """Refresh instances from the database.

        Wrapper around Session.refresh.

        Can be called with multiple instances.
        """
        for instance in instances:
            self.session.refresh(instance)

    def expire_all(self) -> None:
        """Expire all instances in the session.

        Wrapper around Session.expire_all().
        """
        self.session.expire_all()

    @overload
    def execute(
        self,
        query: TypedReturnsRows[*_Ts],
        args: _CoreAnyExecuteParams | None = None,
    ) -> Result[*_Ts]: ...

    @overload
    def execute(
        self,
        query: Executable | str,
        args: _CoreAnyExecuteParams | None = None,
    ) -> Result[*tuple[Any, ...]]: ...

    def execute(
        self,
        query: Any,
        args: _CoreAnyExecuteParams | None = None,
    ) -> Result[*tuple[Any, ...]]:
        """Execute a query against the database.

        Wrapper around Session.execute().
        """
        if isinstance(query, str):
            query = text(query)
        return self.session.execute(query, args)

    @overload
    def scalar(
        self,
        query: TypedReturnsRows[_T],
        params: _CoreSingleExecuteParams | None = None,
    ) -> _T | None: ...

    @overload
    def scalar(
        self,
        query: Executable | str,
        params: _CoreSingleExecuteParams | None = None,
    ) -> Any: ...  # noqa: ANN401

    def scalar(
        self,
        query: Any,
        params: _CoreSingleExecuteParams | None = None,
    ) -> Any:
        """Execute a query and return a single scalar result.

        Wrapper around Session.scalar().
        """
        if isinstance(query, str):
            query = text(query)
        return self.session.scalar(query, params)
