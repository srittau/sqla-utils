from __future__ import annotations

import re
from typing import Generator, Iterable, Iterator


_SQL_COMMENT_START = "--"
_SQL_STRING_DELIMITER = "'"
_SQL_STATEMENT_DELIMITER = ";"

_DELIMITER_LINE_RE = re.compile(r"^\s*delimiter\s+(.*)\s*$", re.IGNORECASE)


def split_sql(stream: Iterable[str]) -> Iterator[str]:
    """Return an iterator over the SQL statements in a stream.

    >>> list(split_sql("SELECT * FROM foo; DELETE FROM foo;"))
    ... ['SELECT * FROM foo', 'DELETE FROM foo']
    """
    return _SQLSplitter(stream).split()


class _SQLSplitter:
    def __init__(self, stream: Iterable[str]) -> None:
        self._stream = stream
        self._current_stmt = ""
        self._in_string = False
        self._stmt_delimiter = _SQL_STATEMENT_DELIMITER
        self._line = ""

    def split(self) -> Iterator[str]:
        for self._line in self._stream:
            yield from self._parse_line()
        if self._current_stmt.strip():
            yield self._current_stmt.strip()

    def _parse_line(self) -> Generator[str, None, None]:
        m = _DELIMITER_LINE_RE.match(self._line)
        if m:
            self._stmt_delimiter = m.group(1)
        else:
            yield from self._parse_sql_line()

    def _parse_sql_line(self) -> Generator[str, None, None]:
        self._pos = 0
        while self._pos < len(self._line):
            if self._at_comment_start():
                break
            elif self._at_statement_delimiter():
                if self._current_stmt.strip():
                    yield self._current_stmt.strip()
                self._current_stmt = ""
                self._pos += len(self._stmt_delimiter)
            elif self._at_string_delimiter():
                self._in_string = not self._in_string
                self._current_stmt += _SQL_STRING_DELIMITER
                self._pos += len(_SQL_STRING_DELIMITER)
            else:
                self._current_stmt += self._line[self._pos]
                self._pos += 1

    def _at_comment_start(self) -> bool:
        return self._current_pos_startswith(_SQL_COMMENT_START)

    def _at_statement_delimiter(self) -> bool:
        if self._in_string:
            return False
        return self._current_pos_startswith(self._stmt_delimiter)

    def _at_string_delimiter(self) -> bool:
        return self._current_pos_startswith(_SQL_STRING_DELIMITER)

    def _current_pos_startswith(self, s: str) -> bool:
        return self._line[self._pos :].startswith(s)
