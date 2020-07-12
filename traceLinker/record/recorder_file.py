import sqlite3
from sqlite3 import Connection
from typing import Optional

# SQL STATEMENTS

CREATE_TABLE_FOR_FILE = """
    CREATE TABLE if NOT EXISTS {db_name}_files (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        path VARCHAR(63) NOT NULL,
        CONSTRAINT path_unique UNIQUE (path)
    )
"""

SELECT_FILE_ID = """
    SELECT id FROM {db_name}_files
        WHERE path = '{path}'
"""

INSERT_FILE_PATH = """
    INSERT OR IGNORE INTO {db_name}_files (path)
        VALUES ('{path}') 
"""

SELECT_LAST_INSERT_FILE_ID = """
    SELECT last_insert_rowid() FROM {db_name}_files
"""

UPDATE_FILE_PATH = """
    UPDATE {db_name}_files 
        SET path = '{new_path}'
        WHERE id = {id}
"""

UPDATE_CLASSES_IN_FILE = """
    UPDATE {db_name}_classes 
        SET file_id = {id_after}
        WHERE file_id = {id_before}
"""

REMOVE_DUPLICATE_FILE = """
    DELETE FROM {db_name}_files 
        WHERE id={id}
"""

# CLASSES


class FileRecorder(object):

    __table_initialised_dbs = []

    def __init__(self, db_name: str, db_connection: Connection):
        if db_name not in FileRecorder.__table_initialised_dbs:
            create_sql = CREATE_TABLE_FOR_FILE.format(db_name=db_name)
            db_connection.execute(create_sql).close()
            db_connection.commit()
            FileRecorder.__table_initialised_dbs.append(db_name)
        self.__db_name = db_name
        self.__db_connection = db_connection

    def record(self, path: str) -> int:
        previous_same_path_id = self.__get_id(path)
        return previous_same_path_id if previous_same_path_id is not None else self.__insert(path)

    def record_relocate(self, old_path: str, new_path: str) -> int:
        id_current = self.__get_id(old_path)
        id_exist = self.__get_id(new_path)
        if id_current is None: return id_exist if id_exist is not None else self.__insert(new_path)
        db_name = self.__db_name
        exe_cursor = self.__db_connection.cursor()
        try:
            if id_exist is not None:
                exe_cursor.execute(UPDATE_CLASSES_IN_FILE.format(db_name=db_name, id_before=id_exist, id_after=id_current))
                exe_cursor.execute(REMOVE_DUPLICATE_FILE.format(db_name=db_name, id=id_exist))
            exe_cursor.execute(UPDATE_FILE_PATH.format(db_name=db_name, new_path=new_path, id=id_current))
        except sqlite3.IntegrityError as err:
            print(err)
        exe_cursor.close()
        exe_cursor.close()
        return id_current

    def __get_id(self, path: str) -> Optional[int]:
        exe_cursor = self.__db_connection.execute(SELECT_FILE_ID.format(db_name=self.__db_name, path=path))
        id_container = exe_cursor.fetchone()
        result = id_container[0] if id_container is not None else None
        exe_cursor.close()
        return result

    def __insert(self, path) -> int:
        exe_cursor = self.__db_connection.cursor()
        exe_cursor.execute(INSERT_FILE_PATH.format(db_name=self.__db_name, path=path))
        exe_cursor.execute(SELECT_LAST_INSERT_FILE_ID.format(db_name=self.__db_name))
        id_container = exe_cursor.fetchone()
        if id_container is None: raise LookupError("DATABASE: mistakenly handle the data")
        exe_cursor.close()
        return id_container[0]
