import os
from typing import List, Tuple, Dict
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

from evaluator4link.evaluator import LinkEvaluator

path_to_comp0110 = os.path.expanduser('~/Project/PycharmProjects/comp0110')
path_to_tmp = f'{path_to_comp0110}/.tmp'
path_to_db = f'{path_to_tmp}/commons_lang.db'
path_to_csv = f'{path_to_tmp}/commons_lang.csv'


def init_figure():
    evaluator = LinkEvaluator(path_to_db, path_to_csv)
    evaluation = evaluator.raw_links_for_predicated_and_ground_truth('apriori_for_weeks')
    num_of_links = len(evaluation.ground_truth_links)
    gt_links_id_pair = list(evaluation.ground_truth_links.keys())
    pd_links_dict = evaluation.predict_links
    valid_pd_links_dict = evaluation.valid_predict_links
    predicted_links: List[float] = list()
    for link in gt_links_id_pair:
        if link not in valid_pd_links_dict: predicted_links.append(0.0)
        else: predicted_links.append(valid_pd_links_dict[link])


def draw_figure_for_co_changed(predicted_links: List[float]):
    plt.figure(num=1, figsize=(30, 5))
    X = np.arange(len(predicted_links))
    Y = np.array(predicted_links)
    plt.bar(X, Y, facecolor='#9999ff', edgecolor='white')
    for x, y in zip(X, Y): plt.text(x + 0.01, y + 0.05, '%.1f' % y, ha='center', va='top')
    plt.xlim((-1, len(predicted_links)))
    plt.ylim((0, 1.25))
    plt.xlabel("co_change_id")
    plt.ylabel("confidence")
    plt.show()


def __draw_scatter_from_dict(ax: Axes3D, dict: Dict[Tuple[int, int], float], color: str, marker: str, size: int):
    id_pairs = dict.keys()
    tested_ids = [id_pair[1] for id_pair in id_pairs]
    test_ids = [id_pair[0] for id_pair in id_pairs]
    predict_value = [value for value in dict.values()]
    zs = np.array(predict_value)
    xs = np.array(test_ids)
    ys = np.array(tested_ids)
    ax.scatter(xs, ys, zs, c=color, marker=marker, s=size)


def draw_3D_for_co_changed():
    fig = plt.figure(num=1, figsize=(15, 15))
    ax1 = fig.add_subplot(111, projection='3d')
    __draw_scatter_from_dict(ax1, pd_links_dict, 'b', '.', 1)
    __draw_scatter_from_dict(ax1, valid_pd_links_dict, 'r', '^', 10)
    __draw_scatter_from_dict(ax1, evaluation.ground_truth_links, 'g', '^', 20)
    plt.title('sale')
    plt.xlabel("tested_id")
    plt.ylabel("test_id")
    plt.show()


def print_complete_report() -> None:
    evaluate_report = LinkEvaluator(path_to_db, path_to_csv)
    print(evaluate_report.precision_recall_and_f1_score_of_strategy('co_created_for_commits'))
    print(evaluate_report.precision_recall_and_f1_score_of_strategy('co_changed_for_commits'))
    print(evaluate_report.precision_recall_and_f1_score_of_strategy('apriori_for_commits'))
    print(evaluate_report.precision_recall_and_f1_score_of_strategy('co_created_for_weeks'))
    print(evaluate_report.precision_recall_and_f1_score_of_strategy('co_changed_for_weeks'))
    print(evaluate_report.precision_recall_and_f1_score_of_strategy('apriori_for_weeks'))
    return None


def print_apriori_report() -> None:
    evaluate_report = LinkEvaluator(path_to_db, path_to_csv)
    print(evaluate_report.precision_recall_and_f1_score_of_strategy('apriori_for_commits'))
    print(evaluate_report.precision_recall_and_f1_score_of_strategy('apriori_for_weeks'))


def output_to_csv() -> None:
    evaluate_report = LinkEvaluator(path_to_db, path_to_csv)
    evaluate_report.output_predict_to_csv()


if __name__ == '__main__':
    evaluate_report = LinkEvaluator(path_to_db, path_to_csv)
    evaluate_report.output_predict_to_csv()
