from sqlite3 import Connection
from datetime import datetime
from traceLinker.change import cType
from traceLinker.record import DbRecorderFactory

# 1. TABLE COMMIT

CREATE_TABLE_FOR_COMMIT = """
    CREATE TABLE if NOT EXISTS {db_name}_commits (
        hash_value VARCHAR(63) PRIMARY KEY,
        commit_date DATE NOT NULL,
        CONSTRAINT hash_unique UNIQUE (hash_value)
    )
"""

SELECT_COMMIT_ID = """
    SELECT id FROM {db_name}_commits 
        WHERE hash_value = '{hash_value}'
"""

INSERT_COMMIT = """
    INSERT INTO {db_name}_commits 
        (hash_value, commit_date)
    VALUES
        ('{hash_value}', '{commit_date}') 
"""



class CommitRecorder(object):

    __table_initialised_dbs = []

    def __init__(self, db_name: str, db_connection: Connection):
        if db_name not in CommitRecorder.__table_initialised_dbs:
            create_sql = CREATE_TABLE_FOR_COMMIT.format(db_name)
            db_connection.execute(create_sql).close()
            db_connection.commit()
            CommitRecorder.__table_initialised_dbs.append(db_name)
        self.__db_name = db_name
        self.__db_connection = db_connection
        self.__commit_hash = None
        self.__commit_date = None

    def start_record(self, commit_hash: str, commit_date: datetime) -> bool:
        select_sql = SELECT_COMMIT_ID.format(db_name=self.__db_name, hash_value=commit_hash)
        res_cursor = self.__db_connection.execute(select_sql)
        is_not_recorded = res_cursor.fetchone() is None
        res_cursor.close()
        if is_not_recorded:
            self.__commit_hash = commit_hash
            self.__commit_date = commit_date.strftime('%Y-%m-%d')
        return is_not_recorded

    def end_record(self):
        if self.__commit_hash is None or self.__commit_date is None:
            return self.abort()
        insert_cmd = INSERT_COMMIT.format(
            db_name=self.__db_name,
            commit_value=self.__commit_hash,
            commit_date=self.__commit_date
        )
        self.__db_connection.execute(insert_cmd).close()
        return self.__db_connection.commit()

    def abort(self):
        return self.__db_connection.rollback()


class DataRecorder(object):

    def __init__(self, tmp_path: str, repo_name: str):
        self.__db_manager = DbRecorderFactory(tmp_path, repo_name)
        self.__commit_hash = None
        self.__commit_date = None
        self.__file_name_with_path = None
        self.__class_name = None
        self.__method_name = None

    def is_recorded(self, commit_hash: str):
        return self.__db_manager.is_commit_recorded(commit_hash)

    def start_commit(self, commit_hash: str, commit_date: datetime):
        self.__commit_hash = commit_hash
        self.__commit_date = commit_date.strftime('%Y-%m-%d')
        return self

    def end_commit(self):
        self.__db_manager.record_commit(
            self.__commit_hash,
            self.__commit_date
        )
        self.__db_manager.flash()
        return

    def for_file(self, file_name_with_path: str):
        self.__file_name_with_path = file_name_with_path
        return self

    def for_method(self, class_name: str, method_name: str):
        self.__class_name = class_name
        self.__method_name = method_name
        return self

    def record(self, change_type: cType, change_details: str = None):
        method_id = self.__db_manager.get_method_id(
            m_name=self.__method_name,
            c_name=self.__class_name,
            rel_path=self.__file_name_with_path
        )
        if method_id is None:
            self.__db_manager.insert_method(
                m_name=self.__method_name,
                c_name=self.__class_name,
                rel_path=self.__file_name_with_path,
                commit_hash=self.__commit_hash
            )
        if change_type == cType.UPDATE:
            self.__db_manager.update_method_name(
                method_id,
                change_details,
                self.__commit_hash
            )
        self.__db_manager.store_change(
            c_type=change_type,
            m_id=method_id,
            c_hash=self.__commit_hash
        )
        return
