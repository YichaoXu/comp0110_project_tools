from sqlite3 import Connection
from datetime import datetime
from traceLinker.record.abs_recorder import AbsRecorder

class CommitRecorder(AbsRecorder):

    __DATE_TO_STR_FORMAT = '%Y-%m-%d'

    def __init__(self, db_connection: Connection):
        AbsRecorder.__init__(self, db_connection, CommitStmts())
        self.__commit_hash = None
        self.__commit_date = None

    def is_recorded_before(self, commit_hash: str) -> bool:
        count_sql = self.__get_stmts().count_commit_stmts()
        res_cursor = self._db_connection.execute(count_sql, [commit_hash])
        is_recorded_before = (res_cursor.fetchone()[0] != 0)
        res_cursor.close()
        return is_recorded_before

    def start(self, commit_hash: str, commit_date: datetime) -> None:
        self.__commit_hash = commit_hash
        self.__commit_date = commit_date.strftime(CommitRecorder.__DATE_TO_STR_FORMAT)

    def stop(self) -> None:
        if self.__commit_hash is None or self.__commit_date is None:
            return self._db_connection.rollback()
        self._insert_new_row_and_return_primary_key(
            commit_hash=self.__commit_hash,
            commit_date=self.__commit_date
        )
        self._db_connection.commit()

    def __get_stmts(self) -> CommitStmts:
        stmts = self._db_stmts
        if not isinstance(stmts, CommitStmts):
            raise TypeError("IMPOSSIBLE")
        return stmts
