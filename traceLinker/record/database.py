import sqlite3
from datetime import datetime

from traceLinker.record import sql
from traceLinker.change import cType


class DbRecorderFactory(object):

    def __init__(self, path: str, name: str):
        self.__db_name = name
        path_to_db = f'{path}/{name}.db'
        connection = sqlite3.connect(path_to_db)
        cursor = connection.cursor()
        cursor.execute(sql.CREATE_TABLE_FOR_COMMIT.format(db_name=name))
        cursor.execute(sql.CREATE_TABLE_FOR_FILE.format(db_name=name))
        cursor.execute(sql.CREATE_TABLE_FOR_CLASS.format(db_name=name))
        cursor.execute(sql.CREATE_TABLE_FOR_METHOD.format(db_name=name))
        cursor.execute(sql.CREATE_TABLE_FOR_CHANGE.format(db_name=name))
        cursor.close()
        connection.commit()
        self.__db_connect = connection
        self.__cursor = connection.cursor()

    def __del__(self):
        self.__cursor.close()
        self.__db_connect.close()

    def get_commit_id(self, commit_hash: str) -> int:
        count_cmd = sql.SELECT_COMMIT_ID.format(commit_hash=commit_hash)
        cursor = self.__db_connect.execute(count_cmd)
        res = cursor.fetchone()[0]
        cursor.close()
        return res

    def record_commit(self, commit_hash: str, commit_date: datetime):
        insert_cmd = sql.INSERT_COMMIT.format(
            commit_hash=commit_hash,
            commit_date=commit_date
        )
        self.__cursor.execute(insert_cmd)

    def get_method_id(self, m_name: str, c_name: str, rel_path: str) -> int:
        select_cmd = sql.SELECT_METHOD_ID.format(
            db_name=self.___db_name,
            method_name=m_name,
            class_name=c_name,
            relative_path=rel_path
        )
        exe_res = self.__cursor.execute(select_cmd).fetchone()
        return exe_res[0] if exe_res is not None else None

    def update_method(self, m_id: int, m_name: str, c_name: str, path: str, commit_hash: str):
        update_cmd = sql.UPDATE_METHOD.format(
            db_name=self.___db_name,
            last_commit_hash=commit_hash,
            method_id=m_id,
            new_name=m_name,
            new_class=c_name,
            new_path=path
        )
        self.__cursor.execute(update_cmd)

    def insert_method(self, m_name: str, c_name: str, rel_path: str, commit_hash: str):
        insert_cmd = sql.INSERT_METHOD.format(
            method_name=m_name,
            class_name=c_name,
            relative_path=rel_path,
            last_commit_hash=commit_hash
        )
        self.__cursor.execute(insert_cmd)

    def store_change(self, c_type: cType, m_id: int, c_hash: str):
        insert_cmd = sql.INSERT_CHANGE.format(
            change_type=c_type,
            target_method_id=m_id,
            commit_hash=c_hash
        )
        self.__cursor.execute(insert_cmd)
