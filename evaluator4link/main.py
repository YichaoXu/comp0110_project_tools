import sqlite3
import pandas
import re
from typing import Tuple, Dict

from evaluator4link.method_name.from_database import DatabaseMethodName
from evaluator4link.method_name.from_ground_true import GroundTruthMethodName

SELECT_ALL_CANDIDATE = '''
WITH candidate_test AS (
    SELECT simple_name AS name, id FROM main.methods
    WHERE simple_name LIKE :test_simple_name
    AND class_name = :test_class AND file_path LIKE :test_path
), candidate_tested AS (
    SELECT simple_name AS name, id FROM main.methods
    WHERE simple_name LIKE :tested_simple_name
    AND class_name = :tested_class AND file_path LIKE :tested_path
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

COUNT_NUM_OF_ALL_LINK = '''
SELECT COUNT(*) FROM {strategy}
'''


class Main(object):

    def __init__(self, path_to_db: str, path_to_csv: str):
        self.__ground_truth = pandas.read_csv(path_to_csv)
        self.__predicted_value = sqlite3.connect(path_to_db)


    def precision_and_recall_of_strategy(self, name: str) -> Dict[str, float]:
        correct_predict_link_num = 0
        total_gt_link_num = 0
        for row in self.__ground_truth.itertuples():
            test, tested = row[1], row[2]
            total_gt_link_num += 1
            gt_name_test = GroundTruthMethodName(test)
            gt_name_tested = GroundTruthMethodName(tested)
            cursor = self.__predicted_value.cursor()
            possible_link = cursor.execute(
                SELECT_ALL_CANDIDATE.format(strategy= name),
                {
                    'test_simple_name': f'{gt_name_test.simple_name}%',
                    'test_class': gt_name_test.class_name,
                    'test_path': f'%{gt_name_test.file_path}%',
                    'tested_simple_name': f'{gt_name_tested.simple_name}%',
                    'tested_class': gt_name_tested.class_name,
                    'tested_path': f'%{gt_name_tested.file_path}%'
                }
            )
            print(f'GroundTruth: \n\tTEST: {gt_name_test.signature} TESTED: {gt_name_tested.signature}')
            for test_candidate, tested_candidate in possible_link:
                pd_name_test = DatabaseMethodName(test_candidate)
                pd_name_tested = DatabaseMethodName(tested_candidate)
                if pd_name_test.signature == gt_name_test.signature  and pd_name_tested.signature == gt_name_tested.signature:
                    correct_predict_link_num += 1
                print(f'\tCandidate (TEST: {pd_name_test.signature} TESTED: {pd_name_tested.signature})')
            cursor.close()
        cursor = self.__predicted_value.cursor()
        cursor.execute(COUNT_NUM_OF_ALL_LINK.format(strategy= name))
        total_num_of_predict_link = cursor.fetchone()[0]
        cursor.close()
        return {
            'correct_predict_link_num': correct_predict_link_num,
            'total_gt_link_num': total_gt_link_num,
            'total_num_of_predict_link':  total_num_of_predict_link
        }





