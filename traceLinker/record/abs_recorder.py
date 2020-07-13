import abc
from sqlite3 import Connection
from typing import Any


class SqlStmtsHolder(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def create_db_stmt(self) -> str:
        pass

    @abc.abstractmethod
    def insert_row_and_select_pk_stmt(self) -> str:
        pass

    @abc.abstractmethod
    def select_primary_key_stmt(self) -> str:
        pass


class AbsRecorder(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, connection: Connection, stmts: SqlStmtsHolder):
        connection.execute(stmts.create_db_stmt()).close()
        connection.commit()
        self._db_stmts = stmts
        self._db_connection = connection

    def _get_primary_key(self, **unique_keys) -> Any:
        select_sql = self._db_stmts.select_primary_key_stmt()
        exe_cursor = self._db_connection.execute(select_sql, unique_keys)
        primary_key_holder = exe_cursor.fetchone()
        result = primary_key_holder[0] if primary_key_holder is not None else None
        ''.format()
        exe_cursor.close()
        return result

    def _insert_new_row_and_return_primary_key(self, **parameters) -> Any:
        insert_sql = self._db_stmts.insert_row_and_select_pk_stmt()
        exe_cursor = self._db_connection.execute(insert_sql, parameters)
        result = exe_cursor.fetchone()[0]
        exe_cursor.close()
        return result
