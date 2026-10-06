from __future__ import annotations

from collections.abc import Generator
from pathlib import Path

import pytest

from sqla_utils.test import NOT_NULL, DBFixture, assert_row_equals


class ExampleFixture(DBFixture):
    sql_path = Path(__file__).parent.parent / "test_sql"


@pytest.fixture
def fix() -> Generator[ExampleFixture, None, None]:
    with ExampleFixture() as fixture:
        yield fixture


class TestAssertRowEquals:
    def test_not_null(self, fix: DBFixture) -> None:
        row = fix.select_sql_one_row("SELECT 'foo' AS text, NULL AS n")
        assert_row_equals(row, {"text": "foo", "n": None})
        assert_row_equals(row, {"text": NOT_NULL})
        with pytest.raises(AssertionError):
            assert_row_equals(row, {"n": NOT_NULL})


class TestDBFixture:
    def test_require(self, fix: ExampleFixture) -> None:
        fix.require("test-tables")

    def test_execute_sql(self, fix: ExampleFixture) -> None:
        fix.execute_sql("SELECT 1")
        fix.execute_sql("SELECT :arg", {"arg": 1})

    def test_select_sql(self, fix: ExampleFixture) -> None:
        assert fix.select_sql("SELECT 1") == [(1,)]
        assert fix.select_sql("SELECT :arg", {"arg": 42}) == [(42,)]

    def test_select_sql_one_row(self, fix: ExampleFixture) -> None:
        assert fix.select_sql_one_row("SELECT 1") == (1,)
        assert fix.select_sql_one_row("SELECT :arg", {"arg": 42}) == (42,)

    def test_select_all_rows(self, fix: ExampleFixture) -> None:
        fix.execute_sql("CREATE TABLE test (id INTEGER, text VARCHAR(10))")
        fix.execute_sql("INSERT INTO test VALUES (42, 'foo')")
        assert fix.select_all_rows("test") == [(42, "foo")]

    def test_insert(self, fix: ExampleFixture) -> None:
        fix.execute_sql("CREATE TABLE test (id INTEGER, text VARCHAR(10))")
        fix.insert("test", {"id": 42, "text": "foo"})
        assert fix.select_sql("SELECT id, text FROM test") == [(42, "foo")]

    def test_assert_row_equals(self, fix: ExampleFixture) -> None:
        fix.execute_sql("CREATE TABLE test (id INTEGER, text VARCHAR(10))")
        fix.execute_sql("INSERT INTO test VALUES (42, 'foo')")
        fix.assert_only_row_equals("test", {"id": 42, "text": "foo"})
