import logging
from typing import Dict, Tuple, Set, Optional

from evaluator4link.measurements import AbstractMeasurement
from evaluator4link.measurements.utils import GroundTruthMethodName, DatabaseMethodName


class CoChangedDataMeasurement(AbstractMeasurement):

    __SELECT_CANDIDATE_ID_SQL = '''
        WITH alive_methods AS (
            SELECT id, simple_name, class_name, file_path FROM methods
            WHERE NOT EXISTS(
                SELECT target_method_id FROM changes
                WHERE change_type = 'REMOVE' AND target_method_id = id
            )
            AND simple_name NOT IN ('main(String [ ] args)', 'suite()', 'setUp()', 'tearDown()')
            AND simple_name NOT LIKE ('for(int i%')
        )
        SELECT id, simple_name FROM alive_methods
        WHERE simple_name LIKE :simple_name
        AND class_name LIKE :class_name
        AND file_path LIKE :file_path
    '''

    __SELECT_PREDICT_FOR_SAME_TESTED_CLASS = '''
        WITH alive_methods AS (
            SELECT id, simple_name, class_name, file_path FROM methods
            WHERE NOT EXISTS(
                SELECT target_method_id FROM changes
                WHERE change_type = 'REMOVE' AND target_method_id = id
            )
            AND simple_name NOT IN ('main(String [ ] args)', 'suite()', 'setUp()', 'tearDown()')
            AND simple_name NOT LIKE ('for(int i%')
        ), tested_class_name_path AS (
            SELECT class_name, file_path FROM alive_methods
            WHERE id = :method_id
        ), tested_methods_in_same_class AS (
            SELECT id FROM (
                tested_class_name_path JOIN alive_methods
                ON alive_methods.class_name = tested_class_name_path.class_name
                AND alive_methods.file_path = tested_class_name_path.file_path
            )
        )
        SELECT tested_method_id, test_method_id, confidence_num FROM {strategy}
        WHERE tested_method_id IN tested_methods_in_same_class
    '''

    def __init__(self, path_to_db: str, path_to_csv: str, for_strategy: str):
        self.__strategy_name = for_strategy
        self._predict_links: Dict[Tuple[int, int], float] = dict()
        self._ground_truth_links: Dict[Tuple[int, int], float] = dict()
        self._valid_predict_links: Dict[Tuple[int, int], float] = dict()
        super().__init__(path_to_db, path_to_csv)

    def _measure(self) -> None:
        for row in self._ground_truth_pandas.itertuples():
            test, tested = GroundTruthMethodName(row[1]), GroundTruthMethodName(row[2])
            test_id, tested_id = self.__get_method_id_by_(test), self.__get_method_id_by_(tested)
            self._ground_truth_links[(tested_id, test_id)] = 1.0
        for (tested_id, test_id) in self._ground_truth_links.keys():
            links_for_class = self.__get_predicate_links_for_same_class(tested_id)
            self._predict_links.update(links_for_class)
        predicted_links_set = set(self._predict_links.keys())
        ground_truth_links_set = set(self._ground_truth_links.keys())
        valid_predict_links_set = predicted_links_set.intersection(ground_truth_links_set)
        self._valid_predict_links = {names: self._predict_links[names] for names in valid_predict_links_set}
        return None

    def __get_method_id_by_(self, gt_name: GroundTruthMethodName) -> Optional[int]:
        cursor = self._predict_database.cursor()
        select_sql = self.__SELECT_CANDIDATE_ID_SQL.format(strategy=self.__strategy_name)
        candidates_methods = cursor.execute(select_sql, {
            'simple_name': f'{gt_name.simple_name}%',
            'class_name': f'{gt_name.class_name.replace("::", "%::")}%',
            'file_path': f'%{gt_name.file_path}%',
        })
        for method_id, long_name in candidates_methods.fetchall():
            if DatabaseMethodName(long_name).signature == gt_name.signature: return method_id
        logging.warning(f'cannot find out method "{gt_name.long_name()}" from the database. ')
        return None

    def __get_predicate_links_for_same_class(self, id: int) -> Dict[Tuple[int, int], float]:
        output = dict()
        cursor = self._predict_database.cursor()
        select_sql = self.__SELECT_PREDICT_FOR_SAME_TESTED_CLASS.format(strategy=self.__strategy_name)
        all_links = cursor.execute(select_sql, {'method_id': id}).fetchall()
        for tested_id, test_id, confidence_num in all_links: output[(tested_id, test_id)] = confidence_num
        return output

    @property
    def predict_links(self) -> Dict[Tuple[int, int], float]:
        return self._predict_links

    @property
    def ground_truth_links(self) -> Dict[Tuple[int, int], float]:
        return self._ground_truth_links

    @property
    def valid_predict_links(self) -> Dict[Tuple[int, int], float]:
        return self._valid_predict_links
