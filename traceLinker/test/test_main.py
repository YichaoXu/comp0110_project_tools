import os
from datetime import datetime

from traceLinker.main import Main

path_to_comp0110 = os.path.expanduser('~/Project/PycharmProjects/comp0110')
path_to_data = f'{path_to_comp0110}/.tmp'
path_to_repository = f'{path_to_comp0110}/example_repositories/simi-project'

start = datetime(2020, 7, 3)
Main(path_to_data).mining(path_to_repository, start_date=start)

