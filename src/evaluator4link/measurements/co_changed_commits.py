from typing import List, Dict, Tuple

from evaluator4link.measurements import CoChangedDataMeasurement


class CoChangedCommitMeasurement(CoChangedDataMeasurement):

    __SELECT_TEST_CHANGED_COMMITS = '''
        SELECT commit_hash FROM changes
        WHERE target_method_id = :test_id
    '''

    __SELECT_CO_CHANGED_COMMITS_SQL = '''
        SELECT commit_hash FROM changes WHERE target_method_id = :tested_id
        INTERSECT 
        SELECT commit_hash FROM changes WHERE target_method_id = :test_id
    '''

    def __init__(self, path_to_db: str, path_to_csv: str):
        self.__tested_change_commits: Dict[str, List[int]] = dict()
        self.__co_changed_commits: Dict[Tuple[str, str], List[int]] = dict()
        self.__commits_id_table: Dict[str, int] = dict()
        super().__init__(path_to_db, path_to_csv, 'co_changed_for_commits')

    def _measure(self) -> None:
        super(CoChangedCommitMeasurement, self)._measure()
        db_cursor = self._predict_database.cursor()
        for tested_id, test_id in self._ground_truth_links.keys():
            select_sql = self.__SELECT_TEST_CHANGED_COMMITS
            exe_result = db_cursor.execute(select_sql, {'test_id': test_id})
            possible_commit_hashes = [row[0] for row in exe_result if exe_result is not None and len(row) >= 1]
            possible_commit_ids = self.__from_hashes_to_ids(possible_commit_hashes)
            test_long_name = self.get_method_name_by_id(test_id)
            self.__tested_change_commits[test_long_name] = possible_commit_ids
            select_sql = self.__SELECT_CO_CHANGED_COMMITS_SQL
            exe_result = db_cursor.execute(select_sql, {'tested_id': tested_id, 'test_id': test_id})
            possible_commit_hashes = [row[0] for row in exe_result if exe_result is not None and len(row) >= 1]
            possible_commit_ids = self.__from_hashes_to_ids(possible_commit_hashes)
            tested_long_name = self.get_method_name_by_id(tested_id)
            self.__co_changed_commits[(test_long_name, tested_long_name)] = possible_commit_ids
        return None

    def __from_hashes_to_ids(self, hashes: List[str]) -> List[int]:
        output = list()
        for hash_val in hashes:
            if hash_val not in self.__commits_id_table:
                self.__commits_id_table[hash_val] = len(self.__commits_id_table) + 1
            output.append(self.__commits_id_table[hash_val])
        return output

    @property
    def tested_change_commits(self) -> Dict[str, List[int]]:
        return self.__tested_change_commits

    @property
    def co_change_commits(self) -> Dict[Tuple[str, str], List[int]]:
        return self.__co_changed_commits

    @property
    def commit_hash_to_id_table(self) -> Dict[str, int]:
        return self.__commits_id_table

    def __str__(self):
        return str({
            'tested_change_commits': self.__tested_change_commits,
            'ground_truth_co_change_commits': self.__co_changed_commits,
            'commit_hash_to_id_table': self.__commits_id_table
        })
