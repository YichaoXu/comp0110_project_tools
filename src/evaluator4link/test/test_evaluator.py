import os
from typing import List

import numpy as np
import matplotlib.pyplot as plt


from evaluator4link.evaluator import LinkEvaluator

path_to_comp0110 = os.path.expanduser('~/Project/PycharmProjects/comp0110')
path_to_tmp = f'{path_to_comp0110}/.tmp'
path_to_db = f'{path_to_tmp}/commons_lang.db'
path_to_csv = f'{path_to_tmp}/commons_lang.csv'


def draw_figure_for_co_changed():
    evaluation = evaluator.raw_links_for_predicated_and_ground_truth('co_changed_for_commits')
    num_of_links = len(evaluation.valid_predict_links)
    all_links_changed_id_pair = list(evaluation.valid_predict_links.keys())
    all_links_changed_rates = list(evaluation.valid_predict_links.values())
    plt.figure(num=1, figsize=(25, 5))
    X = np.arange(num_of_links)
    Y_pd = np.array(all_links_changed_rates)
    plt.bar(X, Y_pd, facecolor='#9999ff', edgecolor='white')
    for x, y in enumerate(all_links_changed_rates):
        if y == 0.0: continue
        plt.text(x + 0.01, y + 0.05, '%.1f' % y, ha='center', va='top')
    plt.xlim((-1, num_of_links))
    plt.ylim((0, 1.1))
    plt.xlabel("co_change_id")
    plt.ylabel("confidence")
    plt.show()


if __name__ == '__main__':
    evaluator = LinkEvaluator(path_to_db, path_to_csv)
    evaluation = evaluator.raw_links_for_predicated_and_ground_truth('co_changed_for_weeks')
    num_of_links = len(evaluation.ground_truth_links)
    gt_links_id_pair = list(evaluation.ground_truth_links.keys())
    pd_links_dict = evaluation.valid_predict_links
    predicted_links: List[float] = list()
    for link in gt_links_id_pair:
        if link not in pd_links_dict: predicted_links.append(0.0)
        else: predicted_links.append(pd_links_dict[link])
    plt.figure(num=1, figsize=(30, 5))
    X = np.arange(num_of_links)
    Y = np.array(predicted_links)
    plt.bar(X, Y, facecolor='#9999ff', edgecolor='white')
    for x, y in zip(X, Y): plt.text(x + 0.01, y + 0.05, '%.1f' % y, ha='center', va='top')
    plt.xlim((-1, num_of_links))
    plt.ylim((0, 1.25))
    plt.xlabel("co_change_id")
    plt.ylabel("confidence")
    plt.show()
