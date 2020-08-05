from evaluator4link.measurements import *


class LinkEvaluator(object):

    def __init__(self, path_to_db: str, path_to_csv: str):
        self.__path_to_db = path_to_db
        self.__path_to_csv = path_to_csv

    def precision_recall_and_f1_score_of_strategy(self, name: str) -> PrecisionRecallMeasurement:
        return PrecisionRecallMeasurement(self.__path_to_db, self.__path_to_csv, name)

    def mean_absolute_and_squared_error_of_strategy(self, name: str) -> MeanAbsoluteAndSquaredErrorMeasurement:
        return MeanAbsoluteAndSquaredErrorMeasurement(self.__path_to_db, self.__path_to_csv, name)

    def raw_links_for_predicated_and_ground_truth(self, name: str):
        return CoChangedDataMeasurement(self.__path_to_db, self.__path_to_csv, name)
