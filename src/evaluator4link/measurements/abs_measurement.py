import abc
import pandas
import sqlite3
from typing import Optional, Any


class AbstractMeasurement(object):
    __metaclass__ = abc.ABCMeta
    __FLYWEIGHT_PREDICT_DB: Optional[sqlite3.Connection] = None
    __FLYWEIGHT_TRUTH_PANDAS: Optional[pandas.DataFrame] = None

    def __init__(self, path_to_db: str, path_to_csv: str):
        if self.__FLYWEIGHT_PREDICT_DB is None:
            self.__FLYWEIGHT_PREDICT_DB = sqlite3.connect(path_to_db)
        if self.__FLYWEIGHT_TRUTH_PANDAS is None:
            self.__FLYWEIGHT_TRUTH_PANDAS = pandas.read_csv(path_to_csv)
        self._measure()

    @property
    def _ground_truth_pandas(self) -> pandas.DataFrame:
        return self.__FLYWEIGHT_TRUTH_PANDAS

    @property
    def _predict_database(self) -> sqlite3.Connection:
        return self.__FLYWEIGHT_PREDICT_DB

    @abc.abstractmethod
    def _measure(self) -> Any: pass
