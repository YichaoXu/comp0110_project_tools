from evaluator4link.measurements import StrategyWithGroundTruthMeasurement


class PrecisionRecallMeasurement(StrategyWithGroundTruthMeasurement):

    def __init__(self, path_to_db: str, path_to_csv: str, for_strategy: str):
        super().__init__(path_to_db, path_to_csv, for_strategy)
        self.__ground_truth_link_num = len(self._ground_truth_links)
        self.__valid_predict_link_num = len(self._valid_predict_links)
        self.__all_predict_link_num = len(self._predict_links)

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
