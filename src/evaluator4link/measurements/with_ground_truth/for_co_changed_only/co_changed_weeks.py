from typing import List, Dict, Tuple
from evaluator4link.measurements.with_ground_truth.for_co_changed_only import AbstractCoChangeMetaDataMeasurement


class CoChangedWeeksMeasurement(AbstractCoChangeMetaDataMeasurement):

    @property
    def select_test_changed_records_sql_stmt(self) -> str:
        return '''
            SELECT commit_hash FROM changes
            WHERE target_method_id = :test_id
        '''

    @property
    def select_co_changed_records_sql_stmt(self) -> str:
        return '''
            WITH week_commit_table AS (
                SELECT STRFTIME('%Y-%W', commit_date)  AS week, hash_value AS commit_hash  FROM git_commits
            ),
            modified_week_table AS (
                SELECT target_method_id, week AS change_week FROM (
                    changes JOIN week_commit_table 
                    ON changes.commit_hash = week_commit_table.commit_hash
                )
                GROUP BY target_method_id, change_week
            ) 
            SELECT change_week FROM modified_week_table WHERE target_method_id = :test_id
            INTERSECT 
            SELECT change_week FROM modified_week_table WHERE target_method_id = :tested_id
        '''

    def __init__(self, path_to_db: str, path_to_csv: str):
        super().__init__(path_to_db, path_to_csv, 'co_changed_for_weeks')

    @property
    def tested_change_weeks(self) -> Dict[str, List[int]]:
        return self._tested_change_records

    @property
    def co_change_weeks(self) -> Dict[Tuple[str, str], List[int]]:
        return self._co_changed_records

    @property
    def weeks_num_to_id_table(self) -> Dict[str, int]:
        return self._records_id_table

    def __str__(self):
        return str({
            'tested_change_weeks': self.tested_change_weeks,
            'co_change_weeks': self.co_change_weeks,
            'weeks_num_to_id_table': self.weeks_num_to_id_table
        })
