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
