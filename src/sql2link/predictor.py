from enum import Enum
from typing import Optional

from sql2link.establisher import *
from sql2link.establisher.with_filter.co_changed import CoChangedtedInAllChangeTypeFilteredCommitLinkEstablisher


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

    def run(self, strategy: LinkStrategy, base: LinkBase, parameter=None, ignore_previous: bool = False):
        if parameter is None: parameter = dict()
        establish: Optional[AbsLinkEstablisher] = None
        if strategy is LinkStrategy.COCREATE:
            if base is LinkBase.FOR_COMMITS: establish = CoCreatedInCommitLinkEstablisher(self.__db_path)
            elif base is LinkBase.FOR_WEEKS: establish = CoCreatedInWeekLinkEstablisher(self.__db_path)
        elif strategy is LinkStrategy.COCHANGE:
            if base is LinkBase.FOR_COMMITS: establish = CoChangedInCommitLinkEstablisher(self.__db_path)
            elif base is LinkBase.FOR_WEEKS: establish = CoChangedInWeekLinkEstablisher(self.__db_path)
        elif strategy is LinkStrategy.APRIORI:
            if base is LinkBase.FOR_COMMITS: establish = AprioriInCommitLinkEstablisher(self.__db_path)
            elif base is LinkBase.FOR_WEEKS: establish = AprioriInWeekLinkEstablisher(self.__db_path)
        if establish is not None: establish.do(parameters=parameter,is_previous_ingored=ignore_previous)

    def run_with_filter(self, strategy: LinkStrategy, base: LinkBase, parameter=None, ignore_previous: bool = False):
        establish = CoChangedtedInAllChangeTypeFilteredCommitLinkEstablisher(self.__db_path)
        if establish is not None: establish.do(parameters=parameter,is_previous_ingored=ignore_previous)
