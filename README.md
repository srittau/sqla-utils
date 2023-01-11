# sqla-utils

Opinionated utilities for working with SQLAlchemy

[![MIT License](https://img.shields.io/pypi/l/sqla-utils.svg)](https://pypi.python.org/pypi/sqla-utils/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/sqla-utils)](https://pypi.python.org/pypi/sqla-utils/)
[![GitHub](https://img.shields.io/github/release/srittau/sqla-utils/all.svg)](https://github.com/srittau/sqla-utils/releases/)
[![pypi](https://img.shields.io/pypi/v/sqla-utils.svg)](https://pypi.python.org/pypi/sqla-utils/)
[![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/srittau/sqla-utils/test-and-lint.yml?branch=main)](https://github.com/srittau/sqla-utils/actions/workflows/test-and-lint.yml)

## Contents

### Transaction Wrapper

**FIXME**

### `DBObjectBase`

`DBObjectBase` is a base class for mapped classes.

Example:

```python
from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String
from sqla_utils import DBObjectBase, Transaction

class DBAppointment(DBObjectBase):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True)
    date = Column(DateTime, nullable=False)
    description = Column(String(1000), nullable=False, default="")
```

Appointment items can then be queried like this:

```python
from sqla_utils import begin_transaction

with begin_transaction() as t:
    app123 = DBAppointment.fetch_by_id(t, 123)
    great_apps = DBAppointment.fetch_all(t, DBAppointment.description.like("%great%"))
```

It is recommended to add custom query, creation, and update methods:

```python
class DBAppointment(DBObjectBase):
    ...

    @classmethod
    def create(cls, t: Transaction, date: datetime, description: str) -> DBAppointment:
        o = cls()
        o.date = date
        o.description = description
        t.add(o)
        return o

    @classmethod
    def fetch_all_after(cls, t: Transaction, date: datetime) -> List[DBAppointment]:
        return cls.fetch_all(t, cls.start >= dates.start)

    def update_description(self, t: Transaction, new_description: str) -> None:
        self.description = new_description
        t.changed(self)
```

### Database Builder

**FIXME**

### pytest Utilities

The `sqla_utils.test` module contains a few utilities for working with pytest and SQLAlchemy.

**FIXME**
