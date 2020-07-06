import os

from pydriller import RepositoryMining

from traceLinker.record import DbRecorderFactory

path_to_comp0110 = os.path.expanduser('~/Project/PycharmProjects/comp0110')
path_to_data = f'{path_to_comp0110}/.tmp'
path_to_repository = f'{path_to_comp0110}/example_repositories'
name_of_repos = 'test'

repository = DbRecorderFactory(path_to_data, name_of_repos)

