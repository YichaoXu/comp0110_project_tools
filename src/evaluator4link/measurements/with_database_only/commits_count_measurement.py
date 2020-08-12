from typing import Dict, List, Tuple
from evaluator4link.measurements import AbstractMeasurement
from evaluator4link.measurements.utils import DatabaseMethodName


class CommitsCountMeasurement(AbstractMeasurement):

    __COUNT_FILE_CHANGES_IN_COMMITS_SQL_STMT = '''
           WITH file_changes AS (
               SELECT DISTINCT file_path, change_type, commit_hash FROM (
                   changes INNER JOIN methods
                   ON changes.target_method_id = methods.id
               )
           )
           SELECT COUNT(commit_hash) AS count, commit_hash FROM file_changes
           WHERE change_type = :change_type GROUP BY commit_hash
       '''

    __COUNT_CLASS_CHANGES_IN_COMMITS_SQL_STMT = '''
           WITH classes_changes AS (
               SELECT DISTINCT class_name, file_path, change_type, commit_hash FROM (
                   changes INNER JOIN methods
                   ON changes.target_method_id = methods.id
               )
           )
           SELECT COUNT(commit_hash) AS count, commit_hash FROM classes_changes
           GROUP BY commit_hash
       '''

    __COUNT_METHODS_IN_COMMITS_SQL_STMT = '''
           WITH methods_changes AS (
               SELECT DISTINCT target_method_id, commit_hash FROM (
                   changes INNER JOIN methods
                   ON changes.target_method_id = methods.id
               )
           )
           SELECT COUNT(commit_hash) AS count, commit_hash FROM methods_changes
           GROUP BY commit_hash
       '''

    def __init__(self, path_to_db: str):
        super().__init__(path_to_db)

    def _measure(self) -> None:
        return None