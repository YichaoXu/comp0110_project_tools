from sqlite3 import Connection
from datetime import datetime

# 1. TABLE COMMIT

CREATE_TABLE_FOR_COMMIT = """
    CREATE TABLE if NOT EXISTS {db_name}_commits(
        hash_value VARCHAR(63) PRIMARY KEY,
        commit_date DATE NOT NULL,
        CONSTRAINT hash_unique UNIQUE (hash_value)
    )
"""

COUNT_COMMIT = """
    SELECT COUNT(*) FROM {db_name}_commits 
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
            create_sql = CREATE_TABLE_FOR_COMMIT.format(db_name=db_name)
            db_connection.execute(create_sql).close()
            db_connection.commit()
            CommitRecorder.__table_initialised_dbs.append(db_name)
        self.__db_name = db_name
        self.__db_connection = db_connection
        self.__commit_hash = None
        self.__commit_date = None
        self.__is_recorded_before = False

    def start_record(self, commit_hash: str, commit_date: datetime):
        select_sql = COUNT_COMMIT.format(db_name=self.__db_name, hash_value=commit_hash)
        res_cursor = self.__db_connection.execute(select_sql)
        result = res_cursor.fetchone()[0]
        is_recorded_before = (result != 0)
        res_cursor.close()
        if not is_recorded_before:
            self.__commit_hash = commit_hash
            self.__commit_date = commit_date.strftime('%Y-%m-%d')
        self.__is_recorded_before = is_recorded_before

    def is_recorded_before(self) -> bool:
        return self.__is_recorded_before

    def end_record(self, enforced: bool = False):
        if self.__is_recorded_before and not enforced: return
        if self.__commit_hash is None or self.__commit_date is None:
            return self.abort()
        insert_cmd = INSERT_COMMIT.format(
            db_name=self.__db_name,
            hash_value=self.__commit_hash,
            commit_date=self.__commit_date
        )
        self.__db_connection.execute(insert_cmd).close()
        self.__is_recorded_before = True
        return self.__db_connection.commit()

    def abort(self):
        return self.__db_connection.rollback()
