import sqlite3
from typing import Dict

from database.table_handler.commit_table_handler import CommitTableHandler
from database.table_handler.method_table_handler import MethodTableHandler
from database.table_handler.change_table_handler import ChangeTableHandler


class TableHandlerFactory(object):

    __connections_dict: Dict[str, sqlite3.Connection] = {}

    def __init__(self, path: str, name: str):
        db_path = f'{path}/{name}.db'
        db_path = db_path.replace('-', '_')
        connections_dict = TableHandlerFactory.__connections_dict
        if db_path not in connections_dict:
            connections_dict[db_path] = sqlite3.connect(db_path)
        self.__connection = connections_dict[db_path]
        self.for_commits_table = CommitTableHandler(connections_dict[db_path])
        self.for_methods_table = MethodTableHandler(connections_dict[db_path])
        self.for_changes_table = ChangeTableHandler(connections_dict[db_path])

    def close(self):
        self.__connection.close()
