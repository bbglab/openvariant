class Context(object):
    """Base class that each context must inherit from"""

    def __init__(self, row: dict, field_name: str, file_path: str) -> None:
        self._row = row
        self._field_name = field_name
        self._file_path = file_path

    @property
    def row(self) -> dict:
        return self._row

    @property
    def field_name(self) -> str:
        return self._field_name

    @property
    def file_path(self) -> str:
        return self._file_path
