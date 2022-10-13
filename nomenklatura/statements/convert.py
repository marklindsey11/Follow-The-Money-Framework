import csv
from io import TextIOWrapper
import orjson
from typing import BinaryIO, Generator, Iterable, Type
from nomenklatura.statements.model import S

from followthemoney.cli.util import MAX_LINE

CSV_COLUMNS = [
    "canonical_id",
    "entity_id",
    "prop",
    "prop_type",
    "schema",
    "value",
    "dataset",
    "target",
    "external",
    "first_seen",
    "last_seen",
    "id",
]

# nk entity-statements --format csv/json
# nk statement-entities
# nk migrate/validate


def write_json_statement(fh: BinaryIO, statement: S) -> None:
    data = statement.to_dict()
    out = orjson.dumps(data, option=orjson.OPT_APPEND_NEWLINE)
    fh.write(out)


def write_json_statements(fh: BinaryIO, statements: Iterable[S]) -> None:
    for stmt in statements:
        write_json_statement(fh, stmt)


def read_json_statements(
    fh: BinaryIO,
    statement_type: Type[S],
    max_line: int = MAX_LINE,
) -> Generator[S, None, None]:
    while line := fh.readline(max_line):
        data = orjson.loads(line)
        yield statement_type.from_dict(data)


def read_csv_statements(
    fh: BinaryIO, statement_type: Type[S]
) -> Generator[S, None, None]:
    wrapped = TextIOWrapper(fh, encoding="utf-8")
    for row in csv.DictReader(wrapped, dialect=csv.unix_dialect):
        yield statement_type.from_row(row)


def write_csv_statements(fh: BinaryIO, statements: Iterable[S]) -> None:
    wrapped = TextIOWrapper(fh, encoding="utf-8")
    writer = csv.writer(wrapped, dialect=csv.unix_dialect)
    writer.writerow(CSV_COLUMNS)
    for stmt in statements:
        row = stmt.to_row()
        writer.writerow([row.get(c) for c in CSV_COLUMNS])
