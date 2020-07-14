from sqlite3 import Connection
from typing import Optional

from traceLinker.record.abs_recorder import AbsRecorder
from traceLinker.record.database import MethodTableHandler


class ClassRecorder(AbsRecorder):

    def _get_table_handler(self) -> MethodTableHandler:

    def __init__(self, TableHandlerRefactory):
        AbsRecorder.__init__(self, table_handler)

    def rename(self, old_name: str, new_name: str, file_path: int) -> int:

