import sqlite3
import sys
from sqlite3 import Connection


# SQL STATEMENTS
from typing import Optional

# 4. TABLE METHOD
from traceLinker.change import cType

CREATE_TABLE_FOR_METHOD = """
    CREATE TABLE if NOT EXISTS {db_name}_methods (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        simple_name VARCHAR(31) NOT NULL, 
        class_id  INTEGER NOT NULL, 
        CONSTRAINT method_unique 
            UNIQUE (simple_name, class_id)
        CONSTRAINT related_to_class 
            FOREIGN KEY (class_id) 
            REFERENCES {db_name}_class(id)
    )
"""

SELECT_METHOD_ID = """
    SELECT (id) FROM {db_name}_methods
        WHERE simple_name = '{simple_name}' 
            AND class_id = '{class_id}'
"""

INSERT_METHOD = """
    INSERT INTO {db_name}_methods (simple_name, class_id) 
        VALUES ('{simple_name}', '{class_id}') 
"""

SELECT_LAST_INSERT_METHOD_ID = """
    SELECT last_insert_rowid() FROM {db_name}_methods
"""

UPDATE_METHOD_NAME = """
    UPDATE {db_name}_methods 
        SET simple_name = '{new_name}'
        WHERE id = {id}
"""

REMOVE_DUPLICATE_METHOD="""
    DELETE FROM {db_name}_methods
        WHERE id={id}
"""

# STATEMENT FOR TABLE CHANGE

CREATE_TABLE_FOR_CHANGE = """
    CREATE TABLE if NOT EXISTS {db_name}_changes (
        change_type  VARCHAR(31) NOT NULL, 
        target_method_id INTEGER NOT NULL, 
        commit_hash VARCHAR(63) NOT NULL, 
        CONSTRAINT change_unique 
            UNIQUE (target_method_id, change_type, commit_hash)
        CONSTRAINT relative_to_method  
            FOREIGN KEY (target_method_id) 
            REFERENCES {db_name}_methods(method_id)
    )
"""

INSERT_CHANGE = """
    INSERT OR IGNORE INTO {db_name}_changes  (change_type, target_method_id, commit_hash)
        VALUES ('{change_type}', {target_method_id}, '{commit_hash}') 
"""

UPDATE_CHANGES_TO_METHOD = """
    UPDATE {db_name}_changes 
        SET target_method_id = {id_after}
        WHERE target_method_id = {id_before}
"""


# PYTHON SOURCE CODES
class MethodRecorder(object):

    __table_initialised_dbs = []

    def __init__(self, db_name: str, db_connection: Connection):
        if db_name not in MethodRecorder.__table_initialised_dbs:
            create_methods_sql = CREATE_TABLE_FOR_METHOD.format(db_name=db_name)
            create_changes_sql = CREATE_TABLE_FOR_CHANGE.format(db_name=db_name)
            cursor = db_connection.cursor()
            cursor.execute(create_methods_sql)
            cursor.execute(create_changes_sql)
            cursor.close()
            db_connection.commit()
            MethodRecorder.__table_initialised_dbs.append(db_name)
        self.__db_name = db_name
        self.__db_connection = db_connection

    def new(self, name: str, class_id: int) -> int:
        cur_id = self.__get_id(name, class_id)
        return cur_id if cur_id is not None else self.__insert(name, class_id)

    def rename(self, old_name: str, new_name: str, class_id: int) -> int:
        cur_id = self.__get_id(old_name, class_id)
        exist_id = self.__get_id(new_name, class_id)
        if cur_id is None: return exist_id if exist_id is not None else  self.__insert(new_name, class_id)
        db_name = self.__db_name
        exe_cursor = self.__db_connection.cursor()
        try:
            if exist_id is not None:
                exe_cursor.execute(UPDATE_CHANGES_TO_METHOD.format(db_name=db_name, id_before=exist_id, id_after=cur_id))
                exe_cursor.execute(REMOVE_DUPLICATE_METHOD.format(db_name=db_name, id=exist_id))
            update_sql = UPDATE_METHOD_NAME.format(db_name=db_name, new_name=new_name, id=cur_id)
            exe_cursor.execute(update_sql)
        except sqlite3.IntegrityError as err:
            print(err)
        exe_cursor.close()
        return cur_id

    def change(self, change_type: str, method_id: int, in_commit: str):

        insert_sql = INSERT_CHANGE.format(
            db_name=self.__db_name, change_type=change_type, target_method_id=method_id, commit_hash=in_commit
        )
        self.__db_connection.execute(insert_sql).close()
        return

    def __get_id(self, name: str, class_id: int) -> Optional[int]:
        select_sql = SELECT_METHOD_ID.format(db_name=self.__db_name, simple_name=name, class_id=class_id)
        exe_cursor = self.__db_connection.execute(select_sql)
        id_container = exe_cursor.fetchone()
        result = id_container[0] if id_container is not None else None
        exe_cursor.close()
        return result

    def __insert(self, name: str, class_id: int) -> int:
        exe_cursor = self.__db_connection.cursor()
        exe_cursor.execute(INSERT_METHOD.format(db_name=self.__db_name, simple_name=name, class_id=class_id))
        exe_cursor.execute(SELECT_LAST_INSERT_METHOD_ID.format(db_name=self.__db_name))
        result = exe_cursor.fetchone()[0]
        exe_cursor.close()
        return result