import os
from commits2sql.miner import DataMiner

path_to_comp0110 = os.path.expanduser('~/Project/PycharmProjects/comp0110')
path_to_data = f'{path_to_comp0110}/.tmp'


def mining_commons_io():
    DataMiner(
        f'{path_to_comp0110}/.tmp',
        f'{path_to_comp0110}/example_repositories/commons-io'
    ).mining(to_commit='54eeaee27c4d73a5b3b6ee84e53ee9046919a18b')

def mining_jfreechart():
    DataMiner(
        f'{path_to_comp0110}/.tmp',
        f'{path_to_comp0110}/example_repositories/jfreechart'
    ).mining(to_commit='b3f5f21ba0fe32a8f7eccb6760a79df30628be3e')

def mining_ant():
    DataMiner(
        f'{path_to_comp0110}/.tmp',
        f'{path_to_comp0110}/example_repositories/ant'
    ).mining(to_commit='d769172a135b19064dccb660b703ecf08f967e3e')


if __name__ == '__main__':
    mining_jfreechart()




