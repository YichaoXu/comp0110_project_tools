import abc
from typing import Dict, List, Tuple

from evaluator4link.measurements.with_ground_truth import StrategyWithGroundTruthMeasurement


class AbstractCoChangeMetaDataMeasurement(StrategyWithGroundTruthMeasurement):
    __metaclass__ = abc.ABCMeta

    @property
    @abc.abstractmethod
    def select_test_changed_records_sql_stmt(self) -> str: pass

    @property
    @abc.abstractmethod
    def select_co_changed_records_sql_stmt(self) -> str: pass

    def __init__(self, path_to_db: str, path_to_csv: str, for_strategy: str):
        self._tested_change_records: Dict[str, List[int]] = dict()
        self._co_changed_records: Dict[Tuple[str, str], List[int]] = dict()
        self._records_id_table: Dict[str, int] = dict()
        super().__init__(path_to_db, path_to_csv, for_strategy)

    def _measure(self) -> None:
        super(AbstractCoChangeMetaDataMeasurement, self)._measure()
        db_cursor = self._predict_database.cursor()
        for tested_id, test_id in self._ground_truth_links.keys():
            select_sql = self.select_test_changed_records_sql_stmt
            exe_result = db_cursor.execute(select_sql, {'test_id': test_id})
            possible_commit_hashes = [row[0] for row in exe_result if exe_result is not None and len(row) >= 1]
            possible_commit_ids = self.__from_hashes_to_ids(possible_commit_hashes)
            test_long_name = self.get_method_name_by_id(test_id)
            self._tested_change_records[test_long_name] = possible_commit_ids
            select_sql = self.select_co_changed_records_sql_stmt
            exe_result = db_cursor.execute(select_sql, {'tested_id': tested_id, 'test_id': test_id})
            possible_commit_hashes = [row[0] for row in exe_result if exe_result is not None and len(row) >= 1]
            possible_commit_ids = self.__from_hashes_to_ids(possible_commit_hashes)
            tested_long_name = self.get_method_name_by_id(tested_id)
            self._co_changed_records[(test_long_name, tested_long_name)] = possible_commit_ids
        return None

    def __from_hashes_to_ids(self, hashes: List[str]) -> List[int]:
        output = list()
        for hash_val in hashes:
            if hash_val not in self._records_id_table:
                self._records_id_table[hash_val] = len(self._records_id_table) + 1
            output.append(self._records_id_table[hash_val])
        return output

    def __str__(self):
        return str({
            'tested_change_records': self._tested_change_records,
            'ground_truth_co_change_records': self._co_changed_records,
            'commit_hash_to_id_table': self._records_id_table
        })
