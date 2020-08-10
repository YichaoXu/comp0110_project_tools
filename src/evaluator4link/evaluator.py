import csv
import sqlite3

from evaluator4link.measurements import *
from evaluator4link.measurements.co_changed_commits import CoChangedCommitMeasurement


class LinkEvaluator(object):

    def __init__(self, path_to_db: str, path_to_csv: str):
        self.__path_to_db = path_to_db
        self.__path_to_csv = path_to_csv

    def precision_recall_and_f1_score_of_strategy(self, name: str) -> PrecisionRecallMeasurement:
        return PrecisionRecallMeasurement(self.__path_to_db, self.__path_to_csv, name)

    def mean_absolute_and_squared_error_of_strategy(self, name: str) -> MeanAbsoluteAndSquaredErrorMeasurement:
        return MeanAbsoluteAndSquaredErrorMeasurement(self.__path_to_db, self.__path_to_csv, name)

    def raw_links_for_predicated_and_ground_truth(self, name: str) -> CoChangedDataMeasurement:
        return CoChangedDataMeasurement(self.__path_to_db, self.__path_to_csv, name)

    def co_changed_commits(self) -> CoChangedCommitMeasurement:
        return CoChangedCommitMeasurement(self.__path_to_db, self.__path_to_csv)

    def output_predict_to_csv(self) -> None:
        measurement = CoChangedCommitMeasurement(self.__path_to_db, self.__path_to_csv)
        csv_file = open(self.__path_to_csv.replace('.csv', '_predict_links.csv'), "w")
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['test', 'function', 'confidence'])
        for (tested, test), confidence in measurement.predict_links.items():
            csv_writer.writerow([
                measurement.get_method_name_by_id(test),
                measurement.get_method_name_by_id(tested),
                confidence]
            )
        csv_file.close()
        return None
