from __future__ import annotations

import re
from os import PathLike
from pathlib import Path
from typing import Any, Callable, Iterable

from .split_sql import split_sql


SQLExecutor = Callable[[str], Any]


class DependencyLoopError(Exception):
    pass


class DatabaseBuilder:
    """Automatic SQL database builder.

    Apply select SQL scripts from a given directory to the given SQL engine.

    SQL scripts can require other SQL scripts to be read beforehand.

    >>> class MyEngine:
    ...     def execute(self, query):
    ...         print(query)
    ...
    >>> engine = MyEngine()
    >>> f = open("feature1.sql", "w")
    >>> f.write("-- Require: feature2\\n\\nSELECT * FROM feature1;")
    >>> f.close()
    >>> f = open("feature2.sql", "w")
    >>> f.write("SELECT * FROM feature2;")
    >>> f.close()
    >>> builder = DatabaseBuilder(engine, ".")
    >>> builder.require("feature1")
    SELECT * FROM feature2
    SELECT * FROM feature1
    >>> os.remove("feature1.sql")
    >>> os.remove("feature2.sql")
    >>>
    """

    def __init__(self, executor: SQLExecutor, path: PathLike | str) -> None:
        self._executor = executor
        self._path = Path(path)
        self._parsed: set[str] = set()
        self._parsing: list[str] = []

    def require(self, *requirements: str) -> None:
        for requirement in requirements:
            if requirement not in self._parsed:
                if requirement in self._parsing:
                    raise DependencyLoopError(
                        "dependency loop: " + requirement
                    )
                self._require_one(requirement)
                self._parsed.add(requirement)

    def _require_one(self, requirement: str) -> None:
        self._parsing.append(requirement)
        try:
            req_file = self._path / (requirement + ".sql")
            with open(req_file) as f:
                headers = _parse_sql_headers(f)
                self._add_requires(headers.get("require", ""))
            with open(req_file) as f:
                _execute_sql_stream(self._executor, f)
        finally:
            self._parsing.pop()

    def _add_requires(self, requires_string: str) -> None:
        if requires_string.strip():
            requires = [r.strip() for r in requires_string.split(",")]
            self.require(*requires)


_SQL_LINE_RE = re.compile(
    r"^--+\s+((?:[a-zA-Z][a-zA-Z0-9]*)(?:-[a-zA-Z][a-zA-Z0-9]*)*):\s+(.*)$"
)


def _parse_sql_headers(stream: Iterable[str]) -> dict[str, str]:
    matches = []
    for line in stream:
        m = _SQL_LINE_RE.match(line)
        if not m:
            break
        matches.append(m)
    return {m.group(1).lower(): m.group(2).strip() for m in matches}


def _execute_sql_stream(executor: SQLExecutor, stream: Iterable[str]) -> None:
    """Run the SQL statements in a stream against a database."""
    for query in split_sql(stream):
        query = query.replace("%", "%%")
        executor(query)
