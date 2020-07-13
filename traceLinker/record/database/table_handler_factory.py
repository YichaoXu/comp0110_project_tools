import sqlite3
from typing import Dict


class DbConnector(object):

    __connections_dict: Dict[str: sqlite3.Connection]
    __DB_PATH_FORMAT = '{path}/{name}.db'

    def __init__(self, path: str, name: str):
        db_path = DbConnector.__DB_PATH_FORMAT.format(path=path, name=name)
        db_path = db_path.replace('-', '_')
        connections_dict = DbConnector.__connections_dict
        if db_path not in connections_dict:
            connections_dict[db_path] = sqlite3.connect(db_path)
        self.__connection = connections_dict[db_path]

    def get_method_table_handler(self):

    def get_commit_table_handler(self):

    def get_change_table_handler(self):

