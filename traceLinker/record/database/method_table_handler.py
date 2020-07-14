from abc import ABC
from sqlite3 import Connection
from typing import List

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

    def select_dup_row_id_after_relocate_stmt(self) -> str:
        return """
            SELECT id FROM methods
            WHERE file_path = :old_path
                AND (class_name, simple_name) = (
                    SELECT class_name, simple_name from methods 
                    WHERE file_path = :new_path
                ) 
        """

    def select_dup_row_id_after_rename_class_stmt(self) -> str:
        return """
            SELECT id FROM methods
            WHERE class_name = :old_class 
                AND file_path = :path
                AND simple_name = (
                    SELECT simple_name from methods 
                    WHERE class_name = :new_name AND file_path = :path
                )
        """

    def select_dup_row_id_after_rename_method_stmt(self) -> str:
        return """
            SELECT id FROM methods
            WHERE class_name = :class_name 
                AND file_path = :path
                AND method_name = :old_name
        """

    def delete_row_by_id_stmt(self) -> str:
        return """
            DELETE FROM methods 
            WHERE id = :id
        """
    def update_simple_name_stmt(self) -> str:
        return """
            UPDATE methods 
            SET simple_name = :new_name
            WHERE simple_name = :old_name
                AND file_path = :path
                AND class_name = :class_name
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


class MethodTableHandler(AbsTableHandler):

    def _get_stmts_holder(self) -> MethodStmtHolder:
        stmts = self._get_stmts_holder()
        if not isinstance(stmts, MethodStmtHolder): raise TypeError("IMPOSSIBLE")
        return stmts

    def __init__(self, db_connection: Connection):
        AbsTableHandler.__init__(self, db_connection, MethodStmtHolder())
        self.__commit_hash = None
        self.__commit_date = None

    def __find_ids_of_duplication(self, sql:str, **parameters) -> List[int]:
        exe_cursor = self._get_db_connection().execute(sql, parameters)
        result = [each_row[0] for each_row in exe_cursor.fetchall()]
        exe_cursor.close()
        return result

    def find_ids_of_duplication_after_relocate(self, old_path: str, new_path: str) -> List[int]:
        select_sql = self._get_stmts_holder().select_dup_row_id_after_relocate_stmt()
        return self.__find_ids_of_duplication(select_sql, old_path=old_path, new_path=new_path)

    def find_ids_of_duplication_after_rename_class(self, old_class:str, new_class:str, path: str) -> List[int]:
        select_sql = self._get_stmts_holder().select_dup_row_id_after_rename_class_stmt()
        return self.__find_ids_of_duplication(select_sql, old_class=old_class, new_class=new_class, path=path)

    def find_ids_of_duplication_after_rename_method(self, old_name: str, new_name: str, path: str) -> List[int]:
        select_sql = self._get_stmts_holder().select_dup_row_id_after_rename_method_stmt()
        return self.__find_ids_of_duplication(select_sql, old_name=old_name, new_name=new_name, path=path)

    def delete_methods_by_ids(self, ids:List[str]) -> None:
        exe_cursor = self._get_db_connection().cursor()
        for each_id in ids:
            delete_sql = self._get_stmts_holder().delete_row_by_id_stmt()
            exe_cursor = exe_cursor.execute(delete_sql, {'id':each_id})
        exe_cursor.close()
        return None

    def __change(self, sql:str, **parameters) -> None:
        exe_cursor = self._get_db_connection().execute(sql, parameters)
        exe_cursor.close()
        return None

    def change_path(self, old_path:str, new_path:str) -> None:
        update_sql = self._get_stmts_holder().update_file_path_stmt()
        return self.__change(update_sql, old_path=old_path, new_path=new_path)

    def change_class(self, path:str, old_class: str, new_class:str) -> None:
        update_sql = self._get_stmts_holder().update_class_name_stmt()
        return self.__change(update_sql, path=path, old_class=old_class, new_class=new_class)

    def change_name(self, path:str, class_name: str, old_name: str, new_name:str) -> None:
        update_sql = self._get_stmts_holder().update_simple_name_stmt()
        return self.__change(update_sql, path=path, class_name=class_name, old_name=old_name, new_name=new_name)
