import re
import subprocess
from typing import Dict, Tuple
from modification.change_identifier.change_type import ChangeType

CMD_DIFF = 'gumtree textdiff {before} {after}'

SPLIT_TREE = '===\n'
SPLIT_DATA = '\n---\n'

METHOD_DECLARATION = 'MethodDeclaration'
TYPE_DECLARATION = 'TypeDeclaration'
JAVADOC_DECLARATION = 'Javadoc'

REGEX_CREATE_OR_DELETE = r'SimpleName: (.+) \[(.+)\]'
REGEX_UPDATE = r'replace (.+) by (.+)'


def is_for_method_or_class(detail: str):
    return detail.startswith(METHOD_DECLARATION) or detail.startswith(TYPE_DECLARATION)


class AnalysisReport(object):

    def __init__(self, path_before: str, path_after: str):
        diff_cmd = CMD_DIFF.format(before=path_before, after=path_after)
        exit_code, diff_output = subprocess.getstatusoutput(diff_cmd)
        if not exit_code == 0: raise Exception(f'FAIL TO EXECUTION {diff_cmd}')
        self.__core: Dict[str, Tuple[ChangeType, str]] = {}
        changes = (
            change_data.split(SPLIT_DATA) for change_data in diff_output.split(SPLIT_TREE)
            if change_data is not None and SPLIT_DATA in change_data
        )
        for change_type, change_detail in changes:
            if change_detail.startswith(JAVADOC_DECLARATION): continue
            if change_type == ChangeType.UPDATE.value:
                search_res = re.search(REGEX_UPDATE, change_detail)
                if search_res is None or search_res.lastindex < 2: continue
                old_name, new_name = search_res.groups()
                self.__core[old_name] = (ChangeType.UPDATE, new_name)
            elif change_type == ChangeType.CREATE.value and is_for_method_or_class(change_detail):
                search_res = re.search(REGEX_CREATE_OR_DELETE, change_detail)
                if search_res is None or search_res.lastindex < 2: continue
                method_name, content = search_res.groups()
                self.__core[method_name] = (ChangeType.CREATE, content)
            elif change_type == ChangeType.REMOVE.value and is_for_method_or_class(change_detail):
                search_res = re.search(REGEX_CREATE_OR_DELETE, change_detail)
                if search_res is None or search_res.lastindex < 2: continue
                method_name, content = search_res.groups()
                self.__core[method_name] = (ChangeType.REMOVE, content)
            # else if change_type is TYPE_NOCHANGE: continue

    def get_change_type_and_details(self, name: str) -> (ChangeType, str):
        return self.__core[name] if name in self.__core else (ChangeType.NOCHANGE, '')