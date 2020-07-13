from sqlite3 import Connection

from traceLinker.record.database.abs_table_handler import SqlStmtHolder, AbsTableHandler


class CommitStmtHolder(SqlStmtHolder):

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
        INSERT INTO commits (hash_value, commit_date)
            OUTPUT Inserted.hash_value
            VALUES (:commit_hash, :commit_date) 
        """

    def count_commit_stmts(self) -> str:
        return """
        SELECT COUNT(*) FROM commits 
            WHERE hash_value = :commit_hash
        """

    def select_primary_key_stmt(self) -> str:
        # SHOULD NOT BE USED
        return """
        SELECT hash_value FROM commits
            WHERE hash_value = :commit_hash
        """


class CommitTableHandler(AbsTableHandler):

    def __init__(self, db_connection: Connection):
        AbsTableHandler.__init__(self, db_connection, CommitStmtHolder())
        self.__commit_hash = None
        self.__commit_date = None

    def is_hash_exist(self, commit_hash: str):
        count_sql = self._get_stmts_holder().count_commit_stmts()
        res_cursor = self._get_db_connection().execute(count_sql, {"hash_value": commit_hash})
        is_recorded_before = (res_cursor.fetchone()[0] != 0)
        res_cursor.close()
        return is_recorded_before

    def _get_stmts_holder(self) -> CommitStmtHolder:
        stmts = super(CommitTableHandler, self)._get_stmts_holder()
        if not isinstance(stmts, CommitStmtHolder): raise TypeError("IMPOSSIBLE")
        return stmts

