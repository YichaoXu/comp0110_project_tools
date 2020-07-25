import os
import sql2link.main

path_to_comp0110 = os.path.expanduser('~/Project/PycharmProjects/comp0110')
path_to_data = f'{path_to_comp0110}/.tmp'
path_to_repository = f'{path_to_comp0110}/example_repositories/commons-lang'

sql2link.main.strategy_three(path_to_data, 'commons-lang')
