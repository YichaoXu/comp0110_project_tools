import sqlite3
import re
from traceLinker.record import ClassRecorder, MethodRecorder, CommitRecorder, FileRecorder


class RecorderFactory(object):

    def __init__(self, path: str, name: str):
        db_name = name.replace('-', '_')
        db_connect = sqlite3.connect(f'{path}/{name}.db')
        self.__db_connect = db_connect
        self.for_commit = CommitRecorder(db_name, db_connect)
        self.for_file = FileRecorder(db_name, db_connect)
        self.for_class = ClassRecorder(db_name, db_connect)
        self.for_method = MethodRecorder(db_name, db_connect)

    def __del__(self):
        self.__db_connect.close()