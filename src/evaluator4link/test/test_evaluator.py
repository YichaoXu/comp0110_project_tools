import os
import numpy as np
import matplotlib.pyplot as plt


from evaluator4link.evaluator import LinkEvaluator

path_to_comp0110 = os.path.expanduser('~/Project/PycharmProjects/comp0110')
path_to_tmp = f'{path_to_comp0110}/.tmp'
path_to_db = f'{path_to_tmp}/commons_lang.db'
path_to_csv = f'{path_to_tmp}/commons_lang.csv'

if __name__ == '__main__':
    evaluator = LinkEvaluator(path_to_db, path_to_csv)
    print('APRIORI FOR COMMITS: ', evaluator.precision_recall_and_f1_score_of_strategy('apriori_for_commits'))


def draw_figure_for_co_changed():
    evaluation = evaluator.mean_absolute_and_squared_error_of_strategy('co_changed_for_weeks')
    num_of_links = len(evaluation.predicted_co_change_confidences)
    all_links_changed_rates = [float(value) for value in evaluation.predicted_co_change_confidences.values()]
    plt.figure(num=1, figsize=(25, 5))
    X = np.arange(num_of_links)
    Y_pd = np.array(all_links_changed_rates)
    plt.bar(X, Y_pd, facecolor='#9999ff', edgecolor='white')
    for index, rate in enumerate(all_links_changed_rates):
        if rate == 0: continue
        plt.text(index + 0.01, rate + 0.05, '%.1f' % rate, ha='center', va='top')
    plt.xlim((-1, num_of_links))
    plt.ylim((0, 1.25))
    plt.xlabel("co_change_id")
    plt.ylabel("confidence")
    plt.show()
