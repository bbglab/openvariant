"""
Where
====================================
Core functions to construct conditional statements and manage them
"""
from enum import Enum
from typing import List, Any


class WhereStatementKeys(Enum):
    """Enum of different operators in a where statement"""
    EQUAL = 'EQUAL'
    NO_EQUAL = 'NOEQUAL'
    MORE = 'MORE'
    LESS = 'LESS'
    MORE_EQUAL = 'MOREEQUAL'
    LESSEQUAL = 'LESSEQUAL'
    AND = 'AND'
    OR = 'OR'


class WhereAttributesKeys(Enum):
    """Enum for the conditional keys"""
    OPERATION = 'OPERATION'
    FIELD = 'FIELD'
    VALUE = 'VALUE'


WHERE_STMTS = {
    "==": WhereStatementKeys.EQUAL.value,
    "!=": WhereStatementKeys.NO_EQUAL.value,
    "<": WhereStatementKeys.LESS.value,
    ">": WhereStatementKeys.MORE.value,
    "<=": WhereStatementKeys.LESSEQUAL.value,
    ">=": WhereStatementKeys.MORE_EQUAL.value
}

WHERE_STMTS_REVERSE = {v: k for k, v in WHERE_STMTS.items()}


def _parse_where(where: str or None) -> List:
    stmt = {}
    if where is None or where == ():
        return []
    w_clauses = where.split(",")
    for w in w_clauses:
        wh = w.split()

        if len(wh) == 3:
            try:
                stmt = {WhereAttributesKeys.OPERATION.value: WHERE_STMTS[wh[1]],
                        WhereAttributesKeys.FIELD.value: wh[0],
                        WhereAttributesKeys.VALUE.value: wh[2]}
            except KeyError:
                raise ValueError(f"Unknown \"where\" syntax.")
        else:
            raise ValueError(f"Unknown where syntax.")
    return [stmt]


def parse_where(where: str or dict) -> Any:
    """Construct the conditional statement.

    Build a list of conditional statements with a specified structure.

    Parameters
    ----------
    where : str
        Conditional statement.

    Returns
    -------
    List[dict]
        List of where statements structured in a specified way.
    """
    return _parse_where(where)


def skip(row: dict, where: dict) -> bool:
    """Check if a row agrees with conditional statement.

    Return True if the row has to be skipped, otherwise it will return False.

    Parameters
    ----------
    row : dict
        Line parsed represented in a dict, where keys are fields.
    where : List[dict]
        A list of the conditional statements structured in a specified way.

    Returns
    -------
    bool
       Return True if the row has to be skipped and doesn't fulfill the conditional statement.
    """

    if where is None or len(where) == 0:
        return False

    filter_wh = False
    for k in where:
        try:
            value = row[k[WhereAttributesKeys.FIELD.value]]
            data_value = f"\"{value}\"" if isinstance(value, str) and not value.isnumeric() else value
            filter_wh = eval(data_value + ' ' +
                             str(WHERE_STMTS_REVERSE[k[WhereAttributesKeys.OPERATION.value]]) + ' ' +
                             k[WhereAttributesKeys.VALUE.value])

            return not filter_wh
        except (KeyError, ValueError):
            return True
    return filter_wh
