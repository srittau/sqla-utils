from __future__ import annotations

from collections.abc import Generator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from sqla_utils.transaction import Transaction


@pytest.fixture
def sa_session() -> Generator[Session, None, None]:
    engine = create_engine("sqlite:///:memory:")
    with Session(engine) as session:
        yield session


def test_execute_textual_sql(sa_session: Session) -> None:
    with Transaction(sa_session) as t:
        result = t.execute("SELECT 1")
        rows = result.fetchall()
        assert len(rows) == 1
        assert rows[0][0] == 1


def test_scalar_textual_sql(sa_session: Session) -> None:
    with Transaction(sa_session) as t:
        result = t.scalar("SELECT 1")
        assert result == 1
