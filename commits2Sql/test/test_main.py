import os
from datetime import datetime
from commits2sql.main import Main

path_to_comp0110 = os.path.expanduser('~/Project/PycharmProjects/comp0110')
path_to_data = f'{path_to_comp0110}/.tmp'
path_to_repository = f'{path_to_comp0110}/example_repositories/commons-lang'

main = Main(path_to_data, path_to_repository, start_date=datetime(2000, 1, 1))
main.mining()

