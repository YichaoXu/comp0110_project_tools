import sqlite3
from typing import Dict

from traceLinker.database.commit_table_handler import CommitTableHandler
from traceLinker.database.method_table_handler import MethodTableHandler
from traceLinker.database.change_table_handler import ChangeTableHandler



class TableHandlerFactory(object):

    __connections_dict: Dict[str: sqlite3.Connection]
    __DB_PATH_FORMAT = '{path}/{name}.db'

    def __init__(self, path: str, name: str):
        db_path = TableHandlerFactory.__DB_PATH_FORMAT.format(path=path, name=name)
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
