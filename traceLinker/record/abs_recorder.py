from datetime import datetime
from typing import Any

from traceLinker.record.database import TableHandlerFactory


class Recorder(object):

    __DATE_TO_STR_FORMAT = '%Y-%m-%d'

    def __init__(self, handler_factory: TableHandlerFactory):
        self.__table_handler = handler_factory

    def is_record_before(self, commit_hash: str) -> bool:
        return self.__table_handler.for_commits_table.is_hash_exist(commit_hash)

    def record_commit(self, commit_hash: str, commit_date: datetime) -> Any:
        return self.__table_handler.for_commits_table.insert_new_row(
            commit_hash=commit_hash,
            commit_date=commit_date.strftime(Recorder.__DATE_TO_STR_FORMAT)
        )

    def record_relocate(self, old_path: str, new_path: str):
        ids = self.__table_handler.for_methods_table.find_ids_of_duplication_after_relocate(old_path, new_path)
        for id in ids:
            self.__table_handler.for_changes_table
        return
