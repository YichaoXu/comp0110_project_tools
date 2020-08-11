from typing import List, Dict, Tuple
from evaluator4link.measurements.with_ground_truth.for_co_changed_only import AbstractCoChangeMetaDataMeasurement


class CoChangedCommitMeasurement(AbstractCoChangeMetaDataMeasurement):

    @property
    def select_test_changed_records_sql_stmt(self) -> str:
        return '''
            SELECT commit_hash FROM changes
            WHERE target_method_id = :test_id
        '''

    @property
    def select_co_changed_records_sql_stmt(self) -> str:
        return '''
            SELECT commit_hash FROM changes WHERE target_method_id = :tested_id
            INTERSECT 
            SELECT commit_hash FROM changes WHERE target_method_id = :test_id
        '''

    def __init__(self, path_to_db: str, path_to_csv: str):
        super().__init__(path_to_db, path_to_csv, 'co_changed_for_commits')

    @property
    def tested_change_commits(self) -> Dict[str, List[int]]:
        return self._tested_change_records

    @property
    def co_change_commits(self) -> Dict[Tuple[str, str], List[int]]:
        return self._co_changed_records

    @property
    def commit_hash_to_id_table(self) -> Dict[str, int]:
        return self._records_id_table

    def __str__(self):
        return str({
            'tested_change_commits': self.tested_change_commits,
            'ground_truth_co_change_commits': self.co_change_commits,
            'commit_hash_to_id_table': self.commit_hash_to_id_table
        })
