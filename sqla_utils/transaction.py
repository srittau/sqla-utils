from __future__ import annotations

from types import TracebackType
from typing import Any, Iterable, Mapping, TypeVar, overload

from sqlalchemy.engine import Connection
from sqlalchemy.orm import Query, Session
from sqlalchemy.schema import Table
from sqlalchemy.sql import ColumnElement

_T = TypeVar("_T")
_TA = TypeVar("_TA", bound="Transaction")


class Transaction:
    """Wrapper around SQLAlchemy sessions and transactions.

    Can be used as a context manager to create a new transaction
    that will be committed or rollbacked when the context is
    exited.

    >>> with Transaction(...) as t:
    ...     ...
    """

    def __init__(self, session: Session) -> None:
        self.session = session

    @property
    def connection(self) -> Connection:
        return self.session.connection()

    def __enter__(self: _TA) -> _TA:
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
    def query(self, entities: Table, **kwargs: Any) -> Query[Any]:
        ...

    @overload  # noqa: F811
    def query(
        self, *entities: type[_T], **kwargs: Any
    ) -> Query[_T]:  # noqa: F811
        ...

    @overload  # noqa: F811
    def query(  # type: ignore  # noqa: F811
        self, entities: ColumnElement[_T], **kwargs: Any
    ) -> Query[tuple[_T]]:
        ...

    @overload  # noqa: F811
    def query(  # noqa: F811
        self, *entities: ColumnElement[_T], **kwargs: Any
    ) -> Query[tuple[_T, ...]]:
        ...

    def query(self, *entities: Any, **kwargs: Any) -> Any:  # noqa: F811
        """Wrapper around Session.query()."""
        return self.session.query(*entities, **kwargs)

    def add(self, *instances: Any) -> None:
        """Save one or more objects to the database."""
        self.session.add_all(instances)

    def delete(self, *instances: Any) -> None:
        """Mark one or more instances as deleted."""
        for obj in instances:
            self.session.delete(obj)

    def flush(self, *objects: Any) -> None:
        """Flush object changes to the database.

        As opposed to Session.flush() this takes the objects
        to flush as positional arguments. Flush all changes
        if no objects are provided.
        """
        if len(objects) == 0:
            self.session.flush()
        else:
            self.session.flush(objects)

    def refresh(self, *instances: Any) -> None:
        """Wrapper around Session.refresh.

        Can be called with multiple instances.
        """
        for instance in instances:
            self.session.refresh(instance)

    def expire_all(self) -> None:
        """Wrapper around Session.expire_all()."""
        self.session.expire_all()

    def execute(
        self,
        query: Any,
        args: Mapping[str, Any] | Iterable[Mapping[str, Any]] | None = None,
    ) -> Any:
        """Wrapper around Session.execute()."""
        return self.session.execute(query, args)

    def scalar(
        self,
        query: Any,
        params: Mapping[str, Any] | Iterable[Mapping[str, Any]] | None = None,
    ) -> Any:
        """Wrapper around Session.scalar()."""
        return self.session.scalar(query, params)
