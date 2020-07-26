from sqlite3 import Connection

from database.table_handler.abs_table_handler import SqlStmtHolder, AbsTableHandler


class ChangeStmtHolder(SqlStmtHolder):

    def create_db_stmt(self) -> str:
        return """
            CREATE TABLE if NOT EXISTS changes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                change_type VARCHAR(32) NOT NULL, 
                target_method_id INTEGER NOT NULL, 
                commit_hash VARCHAR(64) NOT NULL, 
                FOREIGN KEY (target_method_id)  REFERENCES methods(id),
                FOREIGN KEY (commit_hash)  REFERENCES commits(hash_value) 
            );
        """

    def insert_row_stmt(self) -> str:
        return """
            INSERT INTO changes (change_type, target_method_id, commit_hash)
            VALUES (:change_type, :method_id, :commit_hash) 
        """

    def select_primary_key_stmt(self) -> str:
        # SHOULD NOT BE USED
        raise NotImplementedError('TABLE "CHANGE" DO NOT HAVE ALTERNATIVE KEYS')

    def update_target_method_id_stmt(self) -> str:
        return """
            UPDATE changes 
            SET target_method_id = :current_method_id
            WHERE target_method_id = :previous_method_id
        """


class ChangeTableHandler(AbsTableHandler):

    def _get_stmts_holder(self) -> ChangeStmtHolder:
        stmts = super(ChangeTableHandler, self)._get_stmts_holder()
        if not isinstance(stmts, ChangeStmtHolder): raise TypeError("IMPOSSIBLE")
        return stmts

    def __init__(self, db_connection: Connection):
        AbsTableHandler.__init__(self, db_connection, ChangeStmtHolder())

    def update_target_method(self, previous_method_id: str, current_method_id: str) -> None:
        update_sql = self._get_stmts_holder().update_target_method_id_stmt()
        parameters = {'previous_method_id':previous_method_id, 'current_method_id': current_method_id}
        exe_cursor = self._get_db_connection().execute(update_sql, parameters)
        exe_cursor.close()
        return None

    def insert_new_change(self, change_type: str, target_method_id: int, commit_hash: str) -> int:
        return self._insert_new_row(change_type=change_type, method_id=target_method_id, commit_hash=commit_hash)

