from sqlite3 import Connection


# SQL STATEMENTS
from typing import Optional

CREATE_TABLE_FOR_CLASS = """
    CREATE TABLE if NOT EXISTS {db_name}_classes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        simple_name VARCHAR(31) NOT NULL, 
        file_id  INTEGER NOT NULL, 
        CONSTRAINT class_unique 
            UNIQUE (simple_name, file_id)
        CONSTRAINT related_to_file 
            FOREIGN KEY (file_id) 
            REFERENCES {db_name}_file(id)
    )
"""

SELECT_CLASS_ID = """
    SELECT (id) FROM {db_name}_classes
        WHERE simple_name = '{simple_name}'
            AND file_id = '{file_id}'
"""

INSERT_CLASS = """
    INSERT INTO {db_name}_classes  (simple_name, file_id)
        VALUES ('{simple_name}', '{file_id}') 
"""

SELECT_LAST_INSERT_CLASS_ID = """
    SELECT last_insert_rowid() FROM {db_name}_classes
"""

UPDATE_CLASS_NAME = """
    UPDATE {db_name}_classes 
        SET simple_name = '{new_name}'
        WHERE id = {id}
"""

UPDATE_METHOD_IN_CLASS = """
    UPDATE {db_name}_methods 
        SET class_id = {id_after}
        WHERE class_id = {id_before}
"""

REMOVE_DUPLICATE_CLASS="""
    DELETE FROM {db_name}_classes
        WHERE id={id}
"""


# PYTHON SOURCE CODES
class ClassRecorder(object):

    __table_initialised_dbs = []

    def __init__(self, db_name: str, db_connection: Connection):
        if db_name not in ClassRecorder.__table_initialised_dbs:
            create_sql = CREATE_TABLE_FOR_CLASS.format(db_name=db_name)
            db_connection.execute(create_sql).close()
            db_connection.commit()
            ClassRecorder.__table_initialised_dbs.append(db_name)
        self.__db_name = db_name
        self.__db_connection = db_connection

    def record(self, name: str, file_id: int) -> int:
        cur_id = self.__get_id(name, file_id)
        return cur_id if cur_id is not None else self.__insert(name, file_id)

    def record_rename(self, old_name: str, new_name: str, file_id: int) -> int:
        cur_id = self.__get_id(old_name, file_id)
        exist_id = self.__get_id(new_name, file_id)
        if cur_id is None: return exist_id if exist_id is not None else  self.__insert(new_name, file_id)
        db_name = self.__db_name
        exe_cursor = self.__db_connection.cursor()
        if exist_id is not None:
            exe_cursor.execute(UPDATE_METHOD_IN_CLASS.format(db_name=db_name, id_before=exist_id, id_after=cur_id))
            exe_cursor.execute(REMOVE_DUPLICATE_CLASS.format(db_name=db_name, id=exist_id))
        exe_cursor.execute(UPDATE_CLASS_NAME.format(db_name=db_name, new_name=new_name, id=cur_id))
        exe_cursor.close()
        return cur_id

    def __get_id(self, name: str, file_id: int) -> Optional[int]:
        select_sql = SELECT_CLASS_ID.format(db_name=self.__db_name, simple_name=name, file_id=file_id)
        exe_cursor = self.__db_connection.execute(select_sql)
        id_container = exe_cursor.fetchone()
        result = id_container[0] if id_container is not None else None
        exe_cursor.close()
        return result

    def __insert(self, name: str, file_id: int) -> int:
        exe_cursor = self.__db_connection.cursor()
        exe_cursor.execute(INSERT_CLASS.format(db_name=self.__db_name, simple_name=name, file_id=file_id))
        exe_cursor.execute(SELECT_LAST_INSERT_CLASS_ID.format(db_name=self.__db_name))
        result = exe_cursor.fetchone()[0]
        exe_cursor.close()
        return result
