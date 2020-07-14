from sqlite3 import Connection

from traceLinker.record.database.abs_table_handler import SqlStmtHolder, AbsTableHandler


class ChangeStmtHolder(SqlStmtHolder):

    def create_db_stmt(self) -> str:
        return """
            CREATE TABLE if NOT EXISTS changes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                change_type VARCHAR(31) NOT NULL, 
                target_method_id INTEGER NOT NULL FOREIGN KEY REFERENCES methods(id), 
                commit_hash VARCHAR(63) NOT NULL FOREIGN KEY REFERENCES commits(commit_hash)
            );
        """

    def insert_row_and_select_pk_stmt(self) -> str:
        return """
            INSERT INTO changes (change_type, target_method_id, commit_hash)
            OUTPUT Inserted.id
            VALUES (:name, :class, :path) 
        """

    def select_primary_key_stmt(self) -> str:
        # SHOULD NOT BE USED
        raise NotImplementedError('TABLE "CHANGE" DO NOT HAVE ALTERNATIVE KEYS')

    def update_target_method_id_stmt(self) -> str:
        return """
            UPDATE changes 
            SET target_method_id = :new_method_id
            WHERE target_method_id = :old_method_id
        """


class ChangeTableHandler(AbsTableHandler):

    def _get_stmts_holder(self) -> ChangeStmtHolder:
        stmts = super(ChangeTableHandler, self)._get_stmts_holder()
        if not isinstance(stmts, ChangeStmtHolder): raise TypeError("IMPOSSIBLE")
        return stmts

    def __init__(self, db_connection: Connection):
        AbsTableHandler.__init__(self, db_connection, ChangeStmtHolder())

    def reset_target_method(self, old_method_id: str, new_method_id: str) -> None:
        update_sql = self._get_stmts_holder().update_target_method_id_stmt()
        parameters = {'old_method_id':old_method_id, 'new_method_id': new_method_id}
        exe_cursor = self._get_db_connection().execute(update_sql, parameters)
        exe_cursor.close()
        return None

