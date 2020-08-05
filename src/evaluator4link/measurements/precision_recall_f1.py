from typing import Set, Tuple

from evaluator4link.measurements.abs_measurement import AbstractMeasurement
from evaluator4link.measurements.utils import GroundTruthMethodName, DatabaseMethodName


class PrecisionRecallMeasurement(AbstractMeasurement):

    __SELECT_ALL_CANDIDATE_SQL = '''
        WITH alive_methods AS (
            SELECT id, simple_name AS name, class_name, file_path FROM methods
            WHERE NOT EXISTS(
                SELECT target_method_id FROM changes
                WHERE change_type = 'REMOVE' and target_method_id = id
            )
        ), candidate_test AS (
            SELECT id, name FROM alive_methods
            WHERE name LIKE :test_simple_name 
            AND class_name = :test_class 
            AND file_path LIKE :test_path
        ), candidate_tested AS (
            SELECT id, name FROM alive_methods
            WHERE name LIKE :tested_simple_name 
            AND class_name = :tested_class 
            AND file_path LIKE :tested_path
        )
        SELECT candidate_test.name,candidate_tested.name FROM (
            candidate_test JOIN candidate_tested
            ON EXISTS(
                SELECT * FROM {strategy}
                WHERE tested_method_id = candidate_tested.id
                AND test_method_id = candidate_test.id
            )
        )
    '''

    __SELECT_PREDICT_FOR_CLASS = '''
        WITH method_for_class AS (
            SELECT id FROM methods
            WHERE class_name = :class_name
            AND file_path LIKE :file_path
        )
        SELECT tested_method_id, test_method_id FROM {strategy}
        WHERE tested_method_id IN method_for_class 
        OR test_method_id IN method_for_class
    '''

    def __init__(self, path_to_db: str, path_to_csv: str, for_strategy: str):
        self.__strategy_name = for_strategy
        self.__ground_truth_link_num = 0
        self.__valid_predict_link_num = 0
        self.__all_predict_link_num = 1
        super().__init__(path_to_db, path_to_csv)

    def _measure(self) -> None:
        test_and_tested_classes = set()
        for row in self._ground_truth_pandas.itertuples():
            self.__ground_truth_link_num += 1
            test, tested = GroundTruthMethodName(row[1]), GroundTruthMethodName(row[2])
            test_and_tested_classes.add((test.class_name, test.file_path))
            test_and_tested_classes.add((tested.class_name, tested.file_path))
            if self.__is_link_valid(test, tested): self.__valid_predict_link_num += 1
        links = set()
        for (class_name, file_path) in test_and_tested_classes:
            links.update(self.__get_all_predicate_links_for_class(class_name, file_path))
        self.__all_predict_link_num = len(links)

    def __is_link_valid(self, test: GroundTruthMethodName, tested: GroundTruthMethodName) -> bool:
        cursor = self._predict_database.cursor()
        select_sql = self.__SELECT_ALL_CANDIDATE_SQL.format(strategy=self.__strategy_name)
        parameters = {
            'test_simple_name': f'{test.simple_name}%',
            'test_class': test.class_name,
            'test_path': f'%{test.file_path}%',
            'tested_simple_name': f'{tested.simple_name}%',
            'tested_class': tested.class_name,
            'tested_path': f'%{tested.file_path}%'
        }
        possible_link = cursor.execute(select_sql, parameters).fetchall()
        for test_candidate, tested_candidate in possible_link:
            pd_name_test = DatabaseMethodName(test_candidate)
            pd_name_tested = DatabaseMethodName(tested_candidate)
            if pd_name_test.signature != test.signature: continue
            if pd_name_tested.signature != tested.signature: continue
            return True
        cursor.close()
        return False

    def __get_all_predicate_links_for_class(self, name:str, path: str) -> Set[Tuple[str, str]]:
        output = set()
        cursor = self._predict_database.cursor()
        select_sql = self.__SELECT_PREDICT_FOR_CLASS.format(strategy=self.__strategy_name)
        all_links = cursor.execute(select_sql, {'class_name': name,'file_path': f'%{path}%'}).fetchall()
        for test_id, tested_id in all_links: output.add((test_id, tested_id))
        return output

    @property
    def precision(self) -> float:
        return self.__valid_predict_link_num / self.__all_predict_link_num

    @property
    def recall(self) -> float:
        return self.__valid_predict_link_num / self.__ground_truth_link_num

    @property
    def f1_score(self) -> float:
        return self.fn_score(1)

    def fn_score(self, n) -> float:
        return ((1 + n**2) * self.precision * self.recall)/((n**2*self.precision) + self.recall)

    def __str__(self) -> str:
        return str({
            'precision': self.precision,
            'recall': self.recall,
            'f1_score': self.f1_score,
            'valid_predict_link_num (True Positive)': self.__valid_predict_link_num,
            'all_predict_link_num (True Positive + False Positive)': self.__all_predict_link_num,
            'ground_truth_link_num (True Positive + False Negative)': self.__ground_truth_link_num
        })
