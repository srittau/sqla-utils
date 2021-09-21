from __future__ import annotations

from collections.abc import Callable
from types import TracebackType

from sqlalchemy.orm.session import Session as SASession

from .transaction import Transaction


class Session:
    """Wrapper for SQLAlchemy session objects.

    Initialize by providing with a `sessionmaker` object.

    Must be used as context manager.
    """

    def __init__(self, session_maker: Callable[[], SASession]) -> None:
        self._session_maker = session_maker
        self._session: SASession | None = None
        self._transaction: Transaction | None = None

    def __enter__(self) -> Session:
        if self._session:
            raise RuntimeError("session already entered")
        self._session = self._session_maker()
        assert self._session
        self._transaction = Transaction(self._session)
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        if not self._session:
            raise RuntimeError("not in a session context")
        if self._session.is_active:
            if exc_type:
                self._session.rollback()
            else:
                self._session.commit()
        self._session.close()
        self._session = None
        self._transaction = None

    @property
    def transaction(self) -> Transaction:
        """Access the transaction directly."""
        if self._transaction is None:
            raise RuntimeError("not in a session context")
        return self._transaction

    def begin_transaction(self) -> Transaction:
        """Start a new transaction.

        Use as a context manager:

        >>> with session.begin_transaction() as t:
        ...     ...

        It is not possible to nest calls to begin_transaction().
        """
        if not self._transaction:
            raise RuntimeError("not in a session context")
        return self._transaction
