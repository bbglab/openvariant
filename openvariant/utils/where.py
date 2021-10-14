from enum import Enum
from typing import List


class WhereStatementKeys(Enum):
    EQUAL = 'EQUAL'
    NOEQUAL = 'NOEQUAL'
    MORE = 'MORE'
    LESS = 'LESS'
    MOREEQUAL = 'MOREEQUAL'
    LESSEQUAL = 'LESSEQUAL'


class WhereAttributesKeys(Enum):
    OPERATION = 'OPERATION'
    FIELD = 'FIELD'
    VALUE = 'VALUE'


where_stmts = {
    "==": WhereStatementKeys.EQUAL.value,
    "!=": WhereStatementKeys.NOEQUAL.value,
    "<": WhereStatementKeys.LESS.value,
    ">": WhereStatementKeys.MORE.value,
    "<=": WhereStatementKeys.LESSEQUAL.value,
    ">=": WhereStatementKeys.MOREEQUAL.value
}

where_stmts_reverse = {v: k for k, v in where_stmts.items()}


# FIXME: Need an AST for where conditions also check the order
def parse_where(where: str) -> List[dict]:
    if where is None or where == ():
        return []
    where_clauses = []
    w_clauses = where.split(",")
    for w in w_clauses:
        wh = w.split()

        if len(wh) == 3:
            try:
                stmt = {WhereAttributesKeys.OPERATION.value: where_stmts[wh[1]],
                        WhereAttributesKeys.FIELD.value: wh[0],
                        WhereAttributesKeys.VALUE.value: wh[2]}
            except KeyError:
                raise ValueError(f"Unknown \"where\" syntax.")
            where_clauses.append(stmt)
        else:
            raise ValueError(f"Unknown where syntax.")
    return where_clauses


def skip(row: dict, where: List[dict]) -> bool:
    if where is None or len(where) == 0:
        return False

    filter_wh = False
    for k in where:
        try:
            value = row[k[WhereAttributesKeys.FIELD.value]]
            data_value = f"\"{value}\"" if isinstance(value, str) and not value.isnumeric() else str(value)
            filter_wh = eval(data_value + ' ' +
                             str(where_stmts_reverse[k[WhereAttributesKeys.OPERATION.value]]) + ' ' +
                             str(k[WhereAttributesKeys.VALUE.value]))
            return not filter_wh
        except (KeyError, ValueError):
            return True
    return filter_wh
