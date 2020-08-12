import abc
from typing import Dict, List, Tuple
from evaluator4link.measurements import AbstractMeasurement


class AbstractCommitsCountMeasurement(AbstractMeasurement):
    __metaclass__ = abc.ABCMeta

    @property
    @abc.abstractmethod
    def _count_changes_in_commit_sql_stmt(self) -> str: pass

    @property
    def commits_xs_mapping(self) -> Dict[str, int]:
        return self.__commit_xs_table

    @property
    def type_zs_mapping(self) -> Dict[str, int]:
        return self.__type_zs_table

    @property
    def commits_count_coordinates(self) -> List[Tuple[int, int, int]]:
        return self.__commit_change_counts

    def __init__(self, path_to_db: str):
        self.__commit_xs_table: Dict[str, int] = dict()
        self.__type_zs_table: Dict[str, int] = {'ADD': 1, 'MODIFY': 2, 'RENAME': 3}
        self.__commit_change_counts: List[Tuple[int, int, int]] = list()
        super().__init__(path_to_db)

    def _measure(self) -> None:
        cursor = self._predict_database.cursor()
        exe_res = cursor.execute(self._count_changes_in_commit_sql_stmt)
        for commit_hash, change_type, change_count in exe_res:
            x_val = self.__from_hash_to_x_value(commit_hash)
            y_val = change_count
            z_val = self.__from_change_type_to_y_value(change_type)
            self.__commit_change_counts.append((x_val, y_val, z_val))
        cursor.close()
        return None

    def __from_hash_to_x_value(self, hash_value: str) -> int:
        if hash_value not in self.__commit_xs_table:
            self.__commit_xs_table[hash_value] = len(self.__commit_xs_table) + 1
        return self.__commit_xs_table[hash_value]

    def __from_change_type_to_y_value(self, change_type: str) -> int:
        return self.__type_zs_table[change_type]


class FileCommitsCountMeasurement(AbstractCommitsCountMeasurement):

    @property
    def _count_changes_in_commit_sql_stmt(self) -> str:
        return '''
           WITH file_changes AS (
               SELECT DISTINCT file_path, change_type, commit_hash, commit_date FROM (
                   changes INNER JOIN methods INNER JOIN git_commits
                   ON changes.target_method_id = methods.id 
                   AND commit_hash = hash_value
               )
           )
           SELECT commit_hash, change_type, COUNT(*) AS change_count FROM file_changes
           GROUP BY commit_hash, change_type
           ORDER BY commit_date, commit_hash
       '''


class ClassCommitsCountMeasurement(AbstractCommitsCountMeasurement):
    @property
    def _count_changes_in_commit_sql_stmt(self) -> str:
        return '''
           WITH classes_changes AS (
               SELECT DISTINCT  file_path, class_name, change_type, commit_hash, commit_date FROM (
                   changes INNER JOIN methods INNER JOIN git_commits
                   ON changes.target_method_id = methods.id
                   AND commit_hash = hash_value
               )
           )
           SELECT commit_hash, change_type, COUNT(*) AS change_count FROM classes_changes
           GROUP BY commit_hash, change_type
           ORDER BY commit_date, commit_hash
       '''


class MethodCommitsCountMeasurement(AbstractCommitsCountMeasurement):
    @property
    def _count_changes_in_commit_sql_stmt(self) -> str:
        return '''
           WITH methods_changes AS (
               SELECT DISTINCT target_method_id, change_type, commit_hash, commit_date FROM (
                   changes INNER JOIN methods INNER JOIN git_commits
                   ON changes.target_method_id = methods.id
                   AND commit_hash = hash_value
               )
           )
           SELECT commit_hash, change_type, COUNT(*) AS change_count FROM methods_changes
           GROUP BY commit_hash, change_type
           ORDER BY commit_date, commit_hash
       '''


class TestedCommitsCountMeasurement(AbstractCommitsCountMeasurement):
    @property
    def _count_changes_in_commit_sql_stmt(self) -> str:
        return '''
           WITH tested_changes AS (
               SELECT DISTINCT target_method_id, change_type, commit_hash, commit_date FROM (
                   changes INNER JOIN methods INNER JOIN git_commits
                   ON changes.target_method_id = methods.id
                   AND commit_hash = hash_value
               )
               WHERE file_path LIKE 'src/main/java/org/apache/commons/lang3%'
           )
           SELECT commit_hash, change_type, COUNT(*) AS change_count FROM tested_changes
           GROUP BY commit_hash, change_type
           ORDER BY commit_date, commit_hash
       '''


class TestCommitsCountMeasurement(AbstractCommitsCountMeasurement):
    @property
    def _count_changes_in_commit_sql_stmt(self) -> str:
        return '''
           WITH test_changes AS (
               SELECT DISTINCT target_method_id, change_type, commit_hash, commit_date FROM (
                   changes INNER JOIN methods INNER JOIN git_commits
                   ON changes.target_method_id = methods.id
                   AND commit_hash = hash_value
               )
                WHERE file_path LIKE 'src/test/java/org/apache/commons/lang3%'
           )
           SELECT commit_hash, change_type, COUNT(*) AS change_count FROM test_changes
           GROUP BY commit_hash, change_type
           ORDER BY commit_date, commit_hash
       '''
