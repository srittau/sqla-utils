"""pytest utilities for working with SQLAlchemy."""

from __future__ import annotations

import os
import shutil
from pathlib import Path
from tempfile import mkstemp
from types import TracebackType
from typing import TYPE_CHECKING, Any, Iterable, Mapping, Sequence, TypeVar

import pytest
from sqlalchemy import text
from sqlalchemy.engine import Connection, Engine, Row, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import insert, select
from sqlalchemy.sql.schema import MetaData, Table

from .builder import DatabaseBuilder
from .session import Session

if TYPE_CHECKING:
    from sqlalchemy.sql._typing import _DMLColumnArgument

_S = TypeVar("_S", bound="DBFixture")
_TP = TypeVar("_TP", bound="tuple[Any, ...]")

_MEMORY_DB_URL = "sqlite:///:memory:"


def assert_row_equals(
    row: Row[Any], expected_values: Mapping[str, Any]
) -> None:
    """Assert that a row contains expected values.

    row is a mapping as returned from execute_sql_one_row() or
    fetch_only_row(). expected_values is a column name -> expected value
    mapping. The row may contain additional columns that are not listed
    in expected_values. Those are ignored.
    """

    for column_name, expected in expected_values.items():
        column_value = row._mapping[column_name]
        assert (
            column_value == expected
        ), f"column '{column_name}': {expected!r} != {column_value!r}"


def assert_one_row_equals(
    rows: Iterable[Row[Any]], expected_values: Mapping[str, Any]
) -> None:
    """Assert that one of a list of rows contains the expected values.

    rows is a list of mappings as returned from execute_sql() or
    fetch_all_rows(). expected_values is a column name -> expected value
    mapping. The row may contain additional columns that are not listed
    in expected_values. Those are ignored.
    """

    def check_row(row: Row[Any]) -> bool:
        try:
            assert_row_equals(row, expected_values)
        except AssertionError:
            return False
        else:
            return True

    if not any(check_row(r) for r in rows):
        pytest.fail("no row is matching the expectation")


class DBFixture:
    """Database test fixture for pytest and SQLalchemy.

    This uses SQLite to test the SUT, which means that it
    can't be used to test database-specific code.

    Databases fixtures can be set up with one of two methods. Either, by
    supplying a path to a directory containing SQL files that configure
    the database. Example:

        >>> class MyFixture(DBFixture):
        ...     __metadata__ = DBObjectBase.metadata
        ...     sql_path = Path("./foo")
        ...     requirements = ["items"]

    Alternatively, it can be pointed to a template SQLite database that
    will be copied. Example:

        >>> class MyFixture(DBFixture):
        ...     __metadata__ = DBObjectBase.metadata
        ...     db_path = Path("./foo.sqlite")

    The fixture sub-class should contain utility methods for setting up
    and querying the database:

        >>> class MyFixture(DBFixture):
        ...     __metadata__ = DBObjectBase.metadata
        ...     db_path = Path("./foo.sqlite")
        ...
        ...     def insert_item(self, *, id: int, text: str) -> int:
        ...         self.insert("items", {"id": id, "text": text})
        ...         return id
    """

    __metadata__: MetaData = MetaData()
    sql_path: Path | None = None
    db_path: Path | None = None
    requirements: list[str] = []

    def __init__(self) -> None:
        if self.sql_path is None and self.db_path is None:
            raise RuntimeError("either of sql_path or db_path must be set")
        if self.sql_path is not None and self.db_path is not None:
            raise RuntimeError("only one of sql_path and db_path can be set")
        self._tmp_db: Path | None = None
        self.engine: Engine | None = None
        self._connection: Connection | None = None
        self._db_builder: DatabaseBuilder | None = None
        self._session: Session | None = None

    def __enter__(self: _S) -> _S:
        if self.db_path is not None:
            self._tmp_db = _copy_database(self.db_path)
        self.engine = create_engine(self.db_url)
        self._connection = self.engine.connect()
        self.execute_sql("PRAGMA foreign_keys=ON")
        self._session = Session(sessionmaker(bind=self.engine)).__enter__()

        if self.sql_path is not None:
            self._db_builder = DatabaseBuilder(
                self.connection.execute, str(self.sql_path)
            )
        if self.requirements:
            self.require(*self.requirements)
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        assert self._session is not None
        assert self._connection is not None
        self._session.__exit__(exc_type, exc_val, exc_tb)
        self._session = None
        self._connection.close()
        self._connection = None
        self.engine = None
        if self._tmp_db is not None:
            os.remove(self._tmp_db)
            self._tmp_db = None

    @property
    def db_url(self) -> str:
        if self._tmp_db is not None:
            return f"sqlite:///{self._tmp_db}"
        else:
            return _MEMORY_DB_URL

    @property
    def connection(self) -> Connection:
        if self._connection is None:
            raise RuntimeError("call __enter__() before accessing connection")
        return self._connection

    @property
    def session(self) -> Session:
        if self._session is None:
            raise RuntimeError("call __enter__() before accessing session")
        return self._session

    def require(self, *features: str) -> None:
        if self._db_builder is None:
            raise RuntimeError("SQL database not built dynamically")
        with self.connection.begin():
            self._db_builder.require(*features)

    def execute_sql(
        self, query: str, args: Mapping[str, Any] | None = None
    ) -> None:
        """Execute a SQL query."""
        with self.connection.begin():
            if args is None:
                res = self.connection.execute(text(query))
            else:
                res = self.connection.execute(text(query), args)
            res.close()

    def select_sql(
        self, query: str, args: Mapping[str, Any] | None = None
    ) -> Sequence[Row[Any]]:
        """Execute a SQL SELECT and return all rows."""
        with self.connection.begin():
            if args is None:
                res = self.connection.execute(text(query))
            else:
                res = self.connection.execute(text(query), args)
            try:
                return res.fetchall()
            finally:
                res.close()

    def select_sql_one_row(
        self, query: str, args: Mapping[str, Any] | None = None
    ) -> Row[Any]:
        """Execute a SQL SELECT and return one row.

        Raise an AssertionError if the result has zero or more than one row.
        """
        rows = self.select_sql(query, args)
        assert len(rows) == 1, f"got {len(rows)} rows, expected 1"
        return rows[0]

    def select_all_rows(self, table_name: str) -> Sequence[Row[Any]]:
        """Return all rows from a table."""
        table = Table(table_name, self.__metadata__, autoload_with=self.engine)
        with self.connection.begin():
            res = self.connection.execute(select(table))
            return res.fetchall()

    def select_only_row(self, table_name: str) -> Row[Any]:
        """Return the only row from a table.

        Raise an AssertionError if the table has zero or more than one row."""
        rows = self.select_all_rows(table_name)
        assert len(rows) == 1, (
            f"expected exactly one row in table '{table_name}', "
            f"got {len(rows)}"
        )
        return rows[0]

    def insert(
        self,
        table_name: str,
        values: dict[_DMLColumnArgument, Any] | Sequence[Any],
    ) -> None:
        """Insert one row into a table using a mapping of values."""
        table = Table(table_name, self.__metadata__, autoload_with=self.engine)
        with self.connection.begin():
            self.connection.execute(insert(table).values(values))

    def assert_table_is_empty(self, table_name: str) -> None:
        """Assert that a table has no rows."""
        rows = self.select_all_rows(table_name)
        assert len(rows) == 0, (
            f"table {table_name} contains {len(rows)} rows, "
            "expected it to be empty"
        )

    def assert_row_count(self, table_name: str, expected_rows: int) -> None:
        """Assert that a table has a certain amount of rows."""
        rows = self.select_all_rows(table_name)
        assert len(rows) == expected_rows, (
            f"table {table_name} contains {len(rows)} rows, "
            f"expected {expected_rows}"
        )

    def assert_only_row_equals(
        self, table_name: str, expected_values: Mapping[str, Any]
    ) -> None:
        """Assert that a table contains only one row with expected values.

        expected_values is a column name -> expected value
        dictionary. The row may contain additional columns that are not listed
        in expected_values. Those are ignored.
        """
        row = self.select_only_row(table_name)
        assert_row_equals(row, expected_values)

    def assert_any_row_equals(
        self, table_name: str, expected_values: Mapping[str, Any]
    ) -> None:
        """Assert that a table contains a row with expected values.

        expected_values is a column name -> expected value
        dictionary. The row may contain additional columns that are not listed
        in expected_values. Those are ignored.
        """
        for row in self.select_all_rows(table_name):
            try:
                assert_row_equals(row, expected_values)
            except AssertionError:
                pass
            else:
                return
        pytest.fail("no row matches the expectations")

    def assert_rows_equal(
        self, table_name: str, expected_rows: Sequence[Mapping[str, Any]]
    ) -> None:
        """Assert that the expected rows are in table and no other rows."""
        __tracebackhide__ = True

        fetched_rows = self.select_all_rows(table_name)
        if not fetched_rows and not expected_rows:
            return
        assert len(fetched_rows) == len(expected_rows)

        def find_one(
            rs: Sequence[Row[_TP]], expected: Mapping[str, Any]
        ) -> list[Row[_TP]]:
            __tracebackhide__ = True
            for i, tr in enumerate(rs):
                try:
                    assert_row_equals(tr, expected)
                except AssertionError:
                    pass
                else:
                    return [*rs[:i], *rs[i + 1 :]]
            pytest.fail(f"no row matching {expected} found")

        for row in expected_rows:
            fetched_rows = find_one(fetched_rows, row)


def _copy_database(path: Path) -> Path:
    fd, name = mkstemp(".sqlite", "test-")
    with os.fdopen(fd, "wb") as dst:
        with open(path, "rb") as src:
            shutil.copyfileobj(src, dst)
    return Path(name)
