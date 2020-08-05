from enum import Enum
from sql2link.establisher import *


class LinkStrategy(Enum):
    COCHANGE = 'co_changed'
    COCREATE = 'co_created'
    APRIORI = 'apriori'


class LinkBase(Enum):
    FOR_COMMITS = 'for_commits'
    FOR_WEEKS = 'for_weeks'


class TraceabilityPredictor(object):

    def __init__(self, db_path: str):
        self.__db_path = db_path

    def run(self, strategy: LinkStrategy, base: LinkBase, parameter=None):
        if parameter is None: parameter = dict()
        if strategy is LinkStrategy.COCREATE:
            if base is LinkBase.FOR_COMMITS: CoCreatedInCommitLinkEstablisher(self.__db_path).do()
            elif base is LinkBase.FOR_WEEKS: CoCreatedInWeekLinkEstablisher(self.__db_path).do()
        if strategy is LinkStrategy.COCHANGE:
            if base is LinkBase.FOR_COMMITS: CoChangedInCommitLinkEstablisher(self.__db_path).do()
            elif base is LinkBase.FOR_WEEKS: CoChangedInWeekLinkEstablisher(self.__db_path).do()
        if strategy is LinkStrategy.APRIORI:
            if base is LinkBase.FOR_COMMITS: AprioriInCommitLinkEstablisher(self.__db_path).do(parameter)
            elif base is LinkBase.FOR_WEEKS: AprioriInWeekLinkEstablisher(self.__db_path).do(parameter)
