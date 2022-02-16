# News in version 0.3.0

Derive `UnknownItemError` from new exception `DataItemError` and add
`DuplicateItemError`.

# News in version 0.2.3

Only call `commit()` or `rollback()` from `Session.__exit__()`
if the session is still active.

# News in version 0.2.2

Add py.typed file to source distribution.

# News in version 0.2.1

Re-add missing py.typed file in wheel package.

# News in version 0.2.0

- `DBFixture` can now be configured with either an `sql_path` as
  before or with a `db_path`, pointing to a template database.
- `DBFixture.engine` is now initialized during `__enter__()`, not
  during `__init__()`.
- Initialize `DBFixture.__metadata__`.

# News in version 0.1.8

Flush objects after deleting them from the database.

# News in version 0.1.7

Fix `Transaction.add`.

# News in version 0.1.6

Flush objects after adding them to the database.

# News in version 0.1.5

- Raise a `RuntimeError` if entering a `Session` twice.
- Call `commit()` or `rollback()` when leaving a session.
- Add `Session.transaction` property.

# News in version 0.1.4

Add `DBFixture.session` and start a session during setup.

# News in version 0.1.3

Add `Session`.

# News in version 0.1.2

Reenable flush during `Transaction.__exit__()`.

# News in version 0.1.1

Simplify transaction setup and cleanup.

# News in version 0.1.0

Initial release.
