import os
from pydriller import RepositoryMining

from commits2sql.miner import DataMiner

if __name__ == '__main__':
    path_to_comp0110 = os.path.expanduser('~/Project/PycharmProjects/comp0110')
    path_to_data = f'{path_to_comp0110}/.tmp'
    path_to_repository = f'{path_to_comp0110}/example_repositories/commons-lang'
    repos = RepositoryMining(path_to_repository)
    DataMiner(path_to_data, path_to_repository).mining(to_commit='425d8085cfcaab5a78bf0632f9ae77b7e9127cf8')

