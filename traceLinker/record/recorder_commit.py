from sqlite3 import Connection
from datetime import datetime
from traceLinker.record.abs_recorder import SqlStmtsHolder, AbsRecorder


class CommitStmts(SqlStmtsHolder):

    def create_db_stmt(self) -> str:
        return """
        CREATE TABLE if NOT EXISTS commits(
            hash_value VARCHAR(63) PRIMARY KEY,
            commit_date DATE NOT NULL,
            CONSTRAINT hash_unique UNIQUE (hash_value)
        )
        """

    def insert_row_and_select_pk_stmt(self) -> str:
        return """
        INSERT INTO commits 
            (hash_value, commit_date)
        VALUES
            (:hash_value, :commit_date) 
        """

    def count_commit_stmts(self) -> str:
        return """
        SELECT COUNT(*) FROM commits 
            WHERE hash_value = ?
        """

    def select_primary_key_stmt(self) -> str:
        raise NotImplementedError("UNSUPPORTED SQL STMT")


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
