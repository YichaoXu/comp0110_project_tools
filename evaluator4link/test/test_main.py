import os

from evaluator4link.main import Main

path_to_comp0110 = os.path.expanduser('~/Project/PycharmProjects/comp0110')
path_to_tmp = f'{path_to_comp0110}/.tmp'
path_to_db = f'{path_to_tmp}/commons_lang.db'
path_to_csv = f'{path_to_tmp}/commons_lang.csv'

if __name__ == '__main__':
    evaluator = Main(path_to_db, path_to_csv)
    result = evaluator.precision_and_recall_of_strategy('')
    print(result)
