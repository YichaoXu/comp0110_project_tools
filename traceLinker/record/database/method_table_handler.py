from abc import ABC
from sqlite3 import Connection

from traceLinker.record.database.abs_table_handler import SqlStmtHolder, AbsTableHandler


class MethodStmtHolder(SqlStmtHolder):

    def create_db_stmt(self) -> str:
        return """
        CREATE TABLE if NOT EXISTS methods (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            simple_name VARCHAR(32) NOT NULL, 
            class_name VARCHAR(32) NOT NULL, 
            file_path VARCHAR(64) NOT NULL, 
            CONSTRAINT method_unique 
                UNIQUE (simple_name, class_name, file_path)
        )
        """

    def insert_row_and_select_pk_stmt(self) -> str:
        return """
        INSERT INTO methods (simple_name, class_name, file_path)
            OUTPUT Inserted.id
            VALUES (:name, :class, :path) 
        """


    def select_primary_key_stmt(self) -> str:
        return """
        SELECT id FROM methods
            WHERE simple_name = :name 
                AND class_name = :class
                AND file_path = :path
        """

    def update_simple_name_stmt(self) -> str:
        return """
        UPDATE methods 
            SET simple_name = :new_name
            WHERE simple_name = :old_name
                AND file_path = :path
                AND class_name = :class
        """

    def update_class_name_stmt(self) -> str:
        return """
        UPDATE methods 
            SET class_name = :new_class
            WHERE class_name = :old_class
                AND file_path = :path
        """

    def update_file_path_stmt(self) -> str:
        return """
        UPDATE methods 
            SET file_path = :new_path
            WHERE file_path = :old_path
        """

    def delete_




class MethodTableHandler(AbsTableHandler):

    def _get_stmts_holder(self) -> MethodStmtHolder:
        stmts = self._get_stmts_holder()
        if not isinstance(stmts, MethodStmtHolder): raise TypeError("IMPOSSIBLE")
        return stmts

    def _get_db_connection(self) -> Connection:
        pass

    def __init__(self, db_connection: Connection):
        AbsTableHandler.__init__(self, db_connection, MethodStmtHolder())
        self.__commit_hash = None
        self.__commit_date = None

    def


