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

'''
def _dequote(s):
    """
    If a string has single or double quotes around it, remove them.
    Make sure the pair of quotes match.
    If a matching pair of quotes is not found, return the string unchanged.
    """
    if (s[0] == s[-1]) and s.startswith(("'", '"')):
        return s[1:-1]
    return s
'''


def parse_where(where: str) -> List[dict]:
    if where is None:
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
