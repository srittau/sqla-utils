from __future__ import annotations

from typing import Any, TypeVar
from uuid import UUID

from sqlalchemy import Table
from sqlalchemy.orm import Query, declarative_base

from .exc import UnknownItemError
from .transaction import Transaction

_DB = TypeVar("_DB", bound="DBObjectBase")

_DeclarativeBase = declarative_base()


class DBObjectBase(_DeclarativeBase):  # type: ignore
    """Base class for mapped classes.

    Each non-abstract sub-class must provide a __tablename__
    or a __table__ class attribute.
    """

    __abstract__ = True
    __tablename__: str
    __table__: Table

    @classmethod
    def item_type(cls) -> str:
        """Name of the kind of items this represents.

        Used for describing exceptions. Can be overriden by sub-classes.
        Defaults to the table name.
        """
        if hasattr(cls, "__tablename__"):
            return cls.__tablename__
        elif hasattr(cls, "__table__"):
            return cls.__table__.name
        else:
            raise RuntimeError(f"{cls!r} missing __table__ and __tablename__")

    @classmethod
    def query(
        cls: type[_DB],
        t: Transaction,
        *conditions: Any,
        order_by: Any | None = None,
    ) -> Query[_DB]:
        """Return an SQLAlchemy query for a list of database entries.

        Return a query for all entries of this class's table by default,
        but the query can be narrowed by supplying filter conditions.
        """
        query = t.query(cls).filter(*conditions)
        if order_by is not None:
            query = query.order_by(order_by)
        return query

    @classmethod
    def count(cls, t: Transaction, *conditions: Any) -> int:
        """Return number of entries for a given query condition.

        Return the total number of entries if no filter condition
        is specified.
        """
        return cls.query(t, *conditions).count()

    @classmethod
    def first(
        cls: type[_DB],
        query: Query[_DB],
        *,
        field: str | None = None,
        value: Any = None,
    ) -> _DB:
        """Return a single entry from a query.

        If the database contains multiple entries that match the given
        conditions, return an arbitrary entry. If it contains no matching
        entries, raise a UnknownItemError.
        """
        o: _DB | None = query.first()
        if o is None:
            raise UnknownItemError(cls.item_type(), field, value)
        return o

    @classmethod
    def fetch_all(
        cls: type[_DB],
        t: Transaction,
        *conditions: Any,
        order_by: Any | None = None,
    ) -> list[_DB]:
        """Return an a list of entries from the database.

        Return all entries of this class's table by default, but the
        query can be narrowed by supplying filter conditions.
        """
        return cls.query(t, *conditions, order_by=order_by).all()

    @classmethod
    def fetch_one(
        cls: type[_DB],
        t: Transaction,
        *conditions: Any,
        order_by: Any | None = None,
        field: str | None = None,
        value: Any = None,
    ) -> _DB:
        """Return a single entry from the database.

        If the database contains no matching entries, raise an
        UnknownItemError. If it contains multiple entries that match the given
        conditions, return the first entry according to the given order
        condition. If no condition is given, return an arbitrary entry.
        """
        q = cls.query(t, *conditions, order_by=order_by)
        return cls.first(q, field=field, value=value)

    @classmethod
    def fetch_by_id(cls: type[_DB], t: Transaction, id: int) -> _DB:
        """Return the database entry with the given id.

        For this method to work, the database table needs to have a
        numeric column named "id".
        """
        return cls.fetch_one(t, cls.id == id, field="id", value=id)

    @classmethod
    def fetch_by_tag(cls: type[_DB], t: Transaction, tag: str) -> _DB:
        """Return the database entry with the given tag.

        For this method to work, the database table needs to have a
        string "tag" column.
        """
        return cls.fetch_one(t, cls.tag == tag, field="tag", value=tag)

    @classmethod
    def fetch_by_uuid(cls: type[_DB], t: Transaction, uuid: UUID) -> _DB:
        """Return the database entry with the given UUID.

        For this method to work, the database table needs to have a
        string "uuid" column.
        """
        return cls.fetch_one(
            t, cls._uuid == str(uuid), field="uuid", value=uuid
        )

    @classmethod
    def delete_all(cls, t: Transaction, *conditions: Any) -> None:
        """Delete all entries that match certain conditions.

        If no conditions are given, delete all entries from the table.
        """
        cls.query(t, *conditions).delete()

    @classmethod
    def delete_one(
        cls, t: Transaction, *conditions: Any, check_existence: bool = True
    ) -> None:
        """Delete an entry that matches certain conditions.

        If the database contains multiple entries that match the given
        conditions, delete an arbitrary entry. If it contains no matching
        entries, raise a UnknownItemError.
        """
        if check_existence:
            cls.fetch_one(t, *conditions)
        cls.query(t, *conditions).delete()

    @classmethod
    def delete_by_id(
        cls, t: Transaction, id: int, *, check_existence: bool = True
    ) -> None:
        """Delete the entry with the given id.

        Raise UnknownItemError if no entry with this id exists.

        For this method to work, the database table needs to have a
        numeric column named "id".
        """
        if check_existence:
            cls.fetch_by_id(t, id)
        cls.query(t, cls.id == id).delete()

    @classmethod
    def delete_by_tag(
        cls, t: Transaction, tag: str, *, check_existence: bool = True
    ) -> None:
        """Delete the entry with the given tag.

        Raise UnknownItemError if no entry with this tag exists.

        For this method to work, the database table needs to have a
        string column named "tag".
        """
        if check_existence:
            cls.fetch_by_tag(t, tag)
        cls.query(t, cls.tag == tag).delete()

    @classmethod
    def delete_by_uuid(
        cls, t: Transaction, uuid: UUID, *, check_existence: bool = True
    ) -> None:
        """Delete the entry with the given UUID.

        Raise UnknownItemError if no entry with this UUID exists.

        For this method to work, the database table needs to have a
        numeric column named "uuid".
        """
        if check_existence:
            cls.fetch_by_uuid(t, uuid)
        cls.query(t, cls._uuid == str(uuid)).delete()

    def delete(self, t: Transaction) -> None:
        """Delete this entry from the database."""
        t.delete(self)
