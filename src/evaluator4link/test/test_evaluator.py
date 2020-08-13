import os
from typing import List, Tuple, Dict, Optional
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
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
        if link not in valid_pd_links_dict:
            predicted_links.append(0.0)
        else:
            predicted_links.append(valid_pd_links_dict[link])


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


def draw_scatter_figure_for_coordinates_for_methods_and_commits_type():
    fig = plt.figure(num=1, figsize=(15, 15))
    axes = fig.add_subplot(111, projection='3d')

    def draw_3d_scatter(by_3d_coordinates: List[Tuple[int, int, int]], color: str, marker: str, size: int):
        xs, ys, zs = list(), list(), list()
        for x, y, z in by_3d_coordinates:
            xs.append(x)
            ys.append(y)
            zs.append(z)
        axes.scatter(np.array(xs), np.array(ys), np.array(zs), c=color, marker=marker, s=size)

    coordinates = LinkEvaluator(path_to_db, path_to_csv).coordinates_for_methods_commits()
    draw_3d_scatter(coordinates.coordinates_for_test, 'r', '.', 1)
    draw_3d_scatter(coordinates.coordinates_for_tested, 'b', '^', 1)
    print(coordinates.package_name_x_table)
    print(coordinates.commit_hash_y_table)
    print(coordinates.change_type_z_table)
    plt.title('sale')
    plt.xlabel("method_id")
    plt.ylabel("commit_id")
    plt.show()


def draw_2d_scatter_for_commits_distributions():

    def draw_2d_scatter_for_type_z(
            axes: Axes,
            by_3d_coordinates: List[Tuple[int, int, int]],
            title: str, y_max: Optional[int] = None
    ) -> None:
        added: Tuple[List[int], List[int]] = (list(), list())
        modified: Tuple[List[int], List[int]] = (list(), list())
        renamed: Tuple[List[int], List[int]] = (list(), list())
        for coordinate in by_3d_coordinates:
            if y_max is not None and coordinate[1] > y_max:
                print(f'IGNORE COMMITS({coordinate[0]}), SIZE ({coordinate[1]}), TYPE({coordinate[2]}).')
                continue
            target_collections = added if coordinate[2] == 1 else modified if coordinate[2] == 2 else renamed
            target_collections[0].append(coordinate[0])
            target_collections[1].append(coordinate[1])
        axes.scatter(np.array(added[0]), np.array(added[1]), c='r', marker='.', s=1)
        axes.scatter(np.array(modified[0]), np.array(modified[1]), c='b', marker='.', s=1)
        axes.scatter(np.array(renamed[0]), np.array(renamed[1]), c='g', marker='.', s=1)
        axes.set_xlabel("commits_id(chronological)")
        axes.set_ylabel("number of changed (R: ADD, B: MODIFY, G: RENAME)")
        axes.set_title(title)
        return None

    evaluate_report = LinkEvaluator(path_to_db, path_to_csv)
    files = evaluate_report.coordinates_for_files_changes_distribution_of_commits().commits_count_coordinates
    classes = evaluate_report.coordinates_for_classes_changes_distribution_of_commits().commits_count_coordinates
    methods = evaluate_report.coordinates_for_methods_changes_distribution_of_commits().commits_count_coordinates
    test = evaluate_report.coordinates_for_test_changes_distribution_of_commits().commits_count_coordinates
    tested = evaluate_report.coordinates_for_tested_changes_distribution_of_commits().commits_count_coordinates

    fig = plt.figure(num=5, figsize=(25, 25))
    draw_2d_scatter_for_type_z(fig.add_subplot(511), files, 'changes for files', 5)
    draw_2d_scatter_for_type_z(fig.add_subplot(512), classes, 'changes for classes', 5)
    draw_2d_scatter_for_type_z(fig.add_subplot(513), methods, 'changes for methods', 25)
    draw_2d_scatter_for_type_z(fig.add_subplot(514), test, 'changes for test', 25)
    draw_2d_scatter_for_type_z(fig.add_subplot(515), tested, 'changes for tested', 25)
    plt.show()


if __name__ == '__main__':

    def draw_2d_scatter_for_ground_truth_and_predict_in_commits(
            axes: Axes,
            ground_truth_count: Dict[int, int],
            predicted_count: Dict[int, int],
            title: str,
            y_max: Optional[int] = None

    ) -> None:
        filtered: Dict[int, int] = dict()
        xs, ys = list(), list()
        for commit, count in predicted_count.items():
            if y_max is not None and count > y_max:
                filtered[commit] = count
                continue
            xs.append(commit)
            ys.append(count)
        axes.scatter(np.array(xs), np.array(ys), c='b', marker='.', s=200)

        xs, ys = list(), list()
        for commit, count in ground_truth_count.items():
            if commit in filtered:
                print(f'{count} valid links from {filtered[commit]} predicted ones in commit {commit} are filtered')
                continue
            xs.append(commit)
            ys.append(count)
        axes.scatter(np.array(xs), np.array(ys), c='r', marker='.', s=200)
        axes.set_xlabel('commit_id')
        axes.set_ylabel('co_changed_num')
        axes.set_title(title)
        return None

    evaluate_report = LinkEvaluator(path_to_db, path_to_csv).coordinates_for_test_and_tested_and_commits()
    fig = plt.figure(num=2, figsize=(25, 25))
    draw_2d_scatter_for_ground_truth_and_predict_in_commits(
        fig.add_subplot(211),
        evaluate_report.commits_ground_truth,
        evaluate_report.commit_predicted_co_changed_for_test,
        'test_based',
        20
    )
    draw_2d_scatter_for_ground_truth_and_predict_in_commits(
        fig.add_subplot(212),
        evaluate_report.commits_ground_truth,
        evaluate_report.commit_predicted_co_changed_for_tested,
        'tested_based',
        20
    )
    plt.show()






