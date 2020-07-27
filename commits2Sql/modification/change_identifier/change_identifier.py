import re
from enum import Enum
from typing import Dict, Tuple, Optional

from modification.change_identifier.change_utils import CodeDiffer

SPLIT_ALL_CHANGES = '===\n'
SPLIT_TYPE_DETAIL = '\n---\n'

METHOD_DECLARATION = 'MethodDeclaration'
TYPE_DECLARATION = 'TypeDeclaration'
JAVADOC_DECLARATION = 'Javadoc'

REGEX_CLASS_CREATE_OR_DELETE = r'^TypeDeclaration\s*\[(?P<range>.+)\]'
REGEX_METHOD_CREATE_OR_DELETE = r'^MethodDeclaration\s*\[(?P<range>.+)\]'

REGEX_UPDATE_NAME = r'^SimpleName:.*\[(?P<old_range>.+)\][ |\n|\r]*' \
                    r'replace (?<old_name>.+) by (?<new_name>.+)'
REGEX_MATCH_NAME = r'^SimpleName: (?P<old_name>.+) \[(?P<old_range>.+)\][\n\r]' \
                   r'SimpleName: (?P<new_name>.+) \[(?P<new_range>.+)\]'


def is_for_method_or_class(detail: str):
    return detail.startswith(METHOD_DECLARATION) or detail.startswith(TYPE_DECLARATION)


class ChangeType(Enum):
    NOCHANGE = 'match'
    UPDATE = 'update-node'
    CREATE = 'insert-tree'
    REMOVE = 'delete-tree'

ClassNamePairDict = Dict[Tuple[str, int], Tuple[str, int]] # (OldSimpleName, LineNum) -> (NewSimpleName, LineNum)
MethodNamePairDict = Dict[Tuple[str, int], Tuple[str, int]] # (OldSimpleName, LineNum) -> (NewSimpleName, LineNum)

class ChangeIdentifier(object):

    __INSTANCE: Optional[object] = None
    __DIFFER: Optional[CodeDiffer] = None
    __CODE_BEFORE: Optional[str] = None
    __CODE_AFTER: Optional[str] = None

    def __new__(cls, *args, **kw):
        if cls.__INSTANCE is None: cls.__INSTANCE = object.__new__(cls, *args, **kw)
        return cls.__INSTANCE

    def __init__(self, code_before: str, code_after: str):
        if self.__DIFFER is None: self.__DIFFER = CodeDiffer()
        if code_before == self.__CODE_BEFORE and code_after == self.__CODE_AFTER: return
        exe_code, diff_output = self.__DIFFER.compare(code_before, code_after)
        if not exe_code == 0: raise Exception(f'FAIL TO EXECUTION DIFF {diff_output}')
        for change_diff in diff_output.split(SPLIT_ALL_CHANGES):
            diff_data = change_diff.partition(SPLIT_TYPE_DETAIL)
            if len(diff_data) < 3: continue
        self.__CODE_BEFORE = code_before
        self.__CODE_AFTER = code_after

    def __del__(self):
        del self.__DIFFER

    def __analyse(self, diff_txt: str):
        output_name_match:Dict[Tuple[str, int], Tuple[str, int]] = dict()
        names_match: Dict[str, str]
        for change_diff in diff_txt.split(SPLIT_ALL_CHANGES):
            change_type, _, change_detail = change_diff.partition(SPLIT_TYPE_DETAIL)
            if change_type != ChangeType.MATCH.value: continue
            search_res = re.search(REGEX_MATCH_NAME, change_detail)
            if search_res.lastindex < 4: continue
            old_name, new_name = search_res.group('old_name'), search_res.group('new_name')
            if old_name == new_name: continue


        return output

    def analyse(self, code_before: str, code_after: str) -> :
        file_before = open(f'{self.__tmp_dir}/{FILENAME_BEFORE}.{FILENAME_SUFFIX}', 'w')
        file_after = open(f'{self.__tmp_dir}/{FILENAME_AFTER}.{FILENAME_SUFFIX}', 'w')
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


    def new_classname_of(self, old_classname: str) -> Optional[str]: pass

    def get_change_type_and_details(self, name: str) -> (ChangeType, str):
        return self.__core[name] if name in self.__core else (ChangeType.NOCHANGE, '')
