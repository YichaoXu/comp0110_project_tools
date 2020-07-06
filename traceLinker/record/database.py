import sqlite3

from traceLinker.record import ClassRecorder, MethodRecorder
from traceLinker.record.recorder_file import FileRecorder


class DbRecorderFactory(object):

    def __init__(self, path: str, name: str):
        self.__db_name = name
        self.__db_connect = sqlite3.connect(f'{path}/{name}.db')
        self.__recorder_cache = {}

    def __del__(self):
        self.__db_connect.close()



    def get_file_recorder(self)-> FileRecorder:
        name = FileRecorder.__name__
        cache = self.__recorder_cache
        if name not in cache:
            cache[name] = FileRecorder(self.__db_name, self.__db_connect)
        return cache[name]

    def get_class_recorder(self)-> ClassRecorder:
        name = ClassRecorder.__name__
        cache = self.__recorder_cache
        if name not in cache:
            cache[name] = ClassRecorder(self.__db_name, self.__db_connect)
        return cache[name]

    def get_method_recorder(self)-> MethodRecorder:
        name = MethodRecorder.__name__
        cache = self.__recorder_cache
        if name not in cache:
            cache[name] = MethodRecorder(self.__db_name, self.__db_connect)
        return cache[name]