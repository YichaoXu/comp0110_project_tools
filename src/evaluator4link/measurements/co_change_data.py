import logging
from typing import Dict, Tuple, Set, Optional

from evaluator4link.measurements import AbstractMeasurement
from evaluator4link.measurements.utils import GroundTruthMethodName, DatabaseMethodName


class CoChangedDataMeasurement(AbstractMeasurement):


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

    __SELECT_CANDIDATE_ID_SQL = '''
        WITH alive_methods AS (
            SELECT id, simple_name, class_name, file_path FROM methods
            WHERE NOT EXISTS(
                SELECT target_method_id FROM changes
                WHERE change_type = 'REMOVE' AND target_method_id = id
            )
            AND simple_name NOT IN ('main(String [ ] args)', 'suite()', 'setUp()', 'tearDown()')
            AND simple_name NOT LIKE (class_name || '%') AND simple_name NOT LIKE ('for(int i%')
        )
        SELECT id, simple_name FROM alive_methods
        WHERE simple_name LIKE :simple_name
        AND class_name = :class_name
        AND file_path LIKE :file_path
    '''

    __SELECT_PREDICT_FOR_CLASS = '''
        WITH method_for_class AS (
            SELECT id FROM methods
            WHERE class_name = :class_name
            AND file_path LIKE :file_path
        )
        SELECT tested_method_id, test_method_id, confidence_num FROM {strategy}
        WHERE tested_method_id IN method_for_class 
        OR test_method_id IN method_for_class
    '''

    def __init__(self, path_to_db: str, path_to_csv: str, for_strategy: str):
        self.__strategy_name = for_strategy
        self.__predict_links: Dict[Tuple[int, int], float] = dict()
        self.__ground_truth_links: Dict[Tuple[int, int], float] = dict()
        super().__init__(path_to_db, path_to_csv)

    def _measure(self) -> None:
        test_and_tested_classes = set()
        for row in self._ground_truth_pandas.itertuples():
            test, tested = GroundTruthMethodName(row[1]), GroundTruthMethodName(row[2])
            test_and_tested_classes.add((test.class_name, test.file_path))
            test_and_tested_classes.add((tested.class_name, tested.file_path))
            test_id = self.__get_method_id_by_(test)
            tested_id = self.__get_method_id_by_(tested)
            self.__ground_truth_links[(test_id, tested_id)] = 1.0
        for (class_name, file_path) in test_and_tested_classes:
            links_for_class = self.__get_predicate_links_for_class(class_name, file_path)
            self.__predict_links.update(links_for_class)
        return None

    def __get_method_id_by_(self, gt_name: GroundTruthMethodName) -> Optional[int]:
        cursor = self._predict_database.cursor()
        select_sql = self.__SELECT_CANDIDATE_ID_SQL.format(strategy=self.__strategy_name)
        candidates_methods = cursor.execute(select_sql, {
            'simple_name': f'{gt_name.simple_name}%',
            'class_name': gt_name.class_name,
            'test_path': f'%{gt_name.file_path}%',
        })
        for method_id, long_name in candidates_methods.fetchall():
            if DatabaseMethodName(long_name).signature == gt_name.signature: return method_id
        logging.warning(f'cannot find {gt_name.signature} out from the database. ')
        return None

    def __get_predicate_links_for_class(self, name:str, path: str) -> Dict[Tuple[int, int], float]:
        output = dict()
        cursor = self._predict_database.cursor()
        select_sql = self.__SELECT_PREDICT_FOR_CLASS.format(strategy=self.__strategy_name)
        all_links = cursor.execute(select_sql, {'class_name': name,'file_path': f'%{path}%'}).fetchall()
        for test_id, tested_id, confidence_num in all_links: output[(test_id, tested_id)] = confidence_num
        return output