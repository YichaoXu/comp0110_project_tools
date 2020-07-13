from sqlite3 import Connection
from traceLinker.record.abs_recorder import SqlStmtsHolder, AbsRecorder


class FileStmts(SqlStmtsHolder):

    def create_db_stmt(self) -> str:
        return """
        CREATE TABLE if NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            path VARCHAR(63) NOT NULL,
            CONSTRAINT path_unique UNIQUE (path)
        )
        """

    def insert_row_and_select_pk_stmt(self) -> str:
        return """
        INSERT OR IGNORE INTO files (path)
            OUTPUT Inserted.id
            VALUES (:path) 
        """

    def select_primary_key_stmt(self) -> str:
        return """
        SELECT id FROM files
            WHERE path = :path
        """

    def update_file_path_stmt(self) -> str:
        return """
        UPDATE files 
            SET path = :new_path
            WHERE id = :id
        """

    def update_classes_in_file_stmt(self) -> str:
        return """
        UPDATE classes 
            SET file_id = :id_after
            WHERE file_id = :id_before
        """

    def rm_duplicate_file_stmt(self) -> str:
        return """
        DELETE FROM files 
            WHERE id = :id
        """

# CLASSES


class FileRecorder(AbsRecorder):

    __table_initialised_dbs = []

    def __init__(self, db_connection: Connection):
        AbsRecorder.__init__(self, db_connection, FileStmts())

    def new(self, path: str) -> int:
        path_id = self._get_primary_key(path=path)
        path_id = self._insert_new_row_and_return_primary_key(path=path) if path_id is None else path_id
        return path_id

    def relocate(self, old_path: str, new_path: str) -> int:
        id_current = self._get_primary_key(path=old_path)
        id_exist = self._get_primary_key(path=new_path)
        db_cursor = self._db_connection.cursor()
        db_stmts = self.__get_stmts()
        if id_current is None:
            if id_exist is not None:
                output_id = id_exist
            else: #if id_exist is None:
                output_id = self._insert_new_row_and_return_primary_key(path=new_path)
        else : # if id_current is not None:
            if id_exist is None:
                relocate_sql = db_stmts.update_file_path_stmt()
                db_cursor.execute(relocate_sql, {'new_path': new_path, 'id': id_current})
                db_cursor.close()
                output_id = id_current
            else: # if id_exist is not None:


        db_cursor.close()
        return output_id

    def __get_stmts(self) -> FileStmts:
        stmts = self._db_stmts
        if not isinstance(stmts, FileStmts): raise TypeError("IMPOSSIBLE")
        return stmts
