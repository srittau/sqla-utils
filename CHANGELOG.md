# Changelog for SQLA Tools

SQLA Tools adheres to [semantic versioning](https://semver.org/).

## [Unreleased]

## [0.6.1] – 2024-06-06

### Added

- Support Python 3.12.

### Changed

- `assert_rows_equal()`: Improve assertion message when the number of rows
  doesn't match.

## [0.6.0]

- Add a `check_existence` argument to `DBObjectBase.delete_one()` and
  `DBObjectBase.delete_by_*()` methods.
- Fix a race condition when using `DBObjectBase.delete_one()` or one of the
  `delete_by_*()` methods.

## [0.5.0]

- Make compatible with SQLAlchemy 2.0.
- This changes some type annotations to make them compatible with
  SQLAlchemy 2.0.

## [0.4.1]

- Fix various `DBFixture` methods.
- Fix various SQLAlchemy 2.0 compatibility issues in `DBFixture`.
- Update the `RowType` type alias.

## [0.4.0]

- Prepare `DBFixture` for SQLAlchemy 2.0.
    - Wrap all SQL calls in explicit transactions to avoid
      SQLAlchemy future compatibility warnings.
    - Encapsulate all SQL strings into `text()` to avoid
      SQLAlchemy future compatibility warnings.
    - Bind parameters in the first argument to `execute_sql()`,
      `select_sql()`, and `select_sql_one_row()` are now specified using
      the `:arg` format. Arguments are passed as a mapping as second
      argument.
- Fix the example in the docstring for `DatabaseBuilder`.

## [0.3.4]

- `Transaction.execute()` and `Transaction.scalar()`: Wrap SQL strings in
  `text()` to avoid SQLAlchemy future compatibility warnings.

## [0.3.3]

- Fix an SQLAlchemy future compatibility warning when executing text queries.

## [0.3.2]

- Fix an SQLAlchemy future compatibility warning.

## [0.3.1]

- Re-export all exceptions from `sqla_utils`.
- Improve return type annotation of `Transaction.execute()`.
- Fix exception message of `DBFixture.select_only_row()`.

## [0.3.0]

Derive `UnknownItemError` from new exception `DataItemError` and add
`DuplicateItemError`.

## [0.2.3]

Only call `commit()` or `rollback()` from `Session.__exit__()`
if the session is still active.

## [0.2.2]

Add py.typed file to source distribution.

## [0.2.1]

Re-add missing py.typed file in wheel package.

## [0.2.0]

- `DBFixture` can now be configured with either an `sql_path` as
  before or with a `db_path`, pointing to a template database.
- `DBFixture.engine` is now initialized during `__enter__()`, not
  during `__init__()`.
- Initialize `DBFixture.__metadata__`.

## [0.1.8]

Flush objects after deleting them from the database.

## [0.1.7]

Fix `Transaction.add`.

## [0.1.6]

Flush objects after adding them to the database.

## [0.1.5]

- Raise a `RuntimeError` if entering a `Session` twice.
- Call `commit()` or `rollback()` when leaving a session.
- Add `Session.transaction` property.

## [0.1.4]

Add `DBFixture.session` and start a session during setup.

## [0.1.3]

Add `Session`.

## [0.1.2]

Reenable flush during `Transaction.__exit__()`.

## [0.1.1]

Simplify transaction setup and cleanup.

## [0.1.0]

Initial release.
