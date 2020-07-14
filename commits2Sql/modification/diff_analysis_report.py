import os
import re
import subprocess
from typing import Dict, Tuple
from pydriller import Modification
from commits2Sql.modification.utils import ChangeType

CMD_DIFF = 'gumtree textdiff {before} {after}'

SPLIT_TREE = '===\n'
SPLIT_DATA = '\n---\n'

REGEX_CREATE_OR_DELETE = 'SimpleName: (.*?) \[.*?\]'
REGEX_UPDATE = 'replace (.*?) by (.*)'


class AnalysisReport(object):

    def __init__(self, path_before: str, path_after: str):
        diff_cmd = CMD_DIFF.format(before=path_before, after=path_after)
        exit_code, diff_output = subprocess.getstatusoutput(diff_cmd)
        if not exit_code == 0: raise Exception(f'FAIL TO EXECUTION {diff_cmd}')
        self.__core: Dict[str, Tuple[ChangeType, str]] = {}
        changes = (
            change.split(SPLIT_DATA)
            for change in diff_output.split(SPLIT_TREE)
            if change is not None and SPLIT_DATA in change
        )
        for change_type, change_detail in changes:
            if change_type is ChangeType.UPDATE.value:
                search_res = re.search(REGEX_UPDATE, change_detail)
                if search_res is None or search_res.lastindex < 2: continue
                old_name, new_name = search_res.groups()
                self.__core[old_name] = (ChangeType.UPDATE, new_name)
            elif change_type is ChangeType.CREATE.value:
                search_res = re.search(REGEX_CREATE_OR_DELETE, change_detail)
                if search_res is None or search_res.lastindex < 2: continue
                method_name, content = search_res.groups()
                self.__core[method_name] = (ChangeType.CREATE, content)
            elif change_type is ChangeType.REMOVE.value:
                search_res = re.search(REGEX_CREATE_OR_DELETE, change_detail)
                if search_res is None or search_res.lastindex < 2: continue
                method_name, content = search_res.groups()
                self.__core[method_name] = (ChangeType.REMOVE, content)
            # else if change_type is TYPE_NOCHANGE: continue

    def get_change_type_and_details(self, name: str) -> (ChangeType, str):
        return self.__core[name] if name in self.__core else (ChangeType.NOCHANGE, '')
