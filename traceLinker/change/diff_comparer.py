import os
import re
import subprocess
from typing import Dict, Tuple

from pydriller import Modification

from traceLinker.change.utils import ChangeType


class DiffComparer(object):

    FILENAME_AFTER = 'after'
    FILENAME_BEFORE = 'before'
    CMD_DIFF = 'gumtree textdiff {before} {after}'

    SPLIT_TREE = '===\n'
    SPLIT_DATA = '\n---\n'

    REGEX_CREATE_OR_DELETE = 'SimpleName: (.*?) \[.*?\]'
    REGEX_UPDATE = 'replace (.*?) by (.*)'

    def __init__(self, tmp_path: str):
        os.makedirs(tmp_path, exist_ok=True)
        self.__tmp_path = tmp_path

    def compare(self, file: Modification) -> Dict[str, Tuple[ChangeType, str]]: # {name: (type, details)}:
        suffix_name = file.filename.rpartition('.')[-1]
        diff_text = self.__run_diff(file.source_code_before, file.source_code, suffix_name)
        return self.__extract_output(diff_text)

    def __run_diff(self, code_before: str, code_after: str, suffix: str) -> str:
        path_to_before = f'{self.__tmp_path}/{self.FILENAME_BEFORE}.{suffix}'
        path_to_after = f'{self.__tmp_path}/{self.FILENAME_AFTER}.{suffix}'
        with open(path_to_before, 'w') as f: f.write(code_before)
        with open(path_to_after, 'w') as f: f.write(code_after)
        diff_cmd = self.CMD_DIFF.format(before=path_to_before, after=path_to_after)
        exit_code, diff_output = subprocess.getstatusoutput(diff_cmd)
        if not exit_code == 0: raise Exception(f'FAIL TO EXECUTION {diff_cmd}')
        return diff_output

    def __extract_output(self, diff_output: str) -> Dict[str, Tuple[ChangeType, str]]: # {name: (type, details)}
        updated = {}
        changes = (
            change.split(self.SPLIT_DATA)
            for change in diff_output.split(self.SPLIT_TREE)
            if change is not None and self.SPLIT_DATA in change
        )
        for change_type, change_detail in changes:
            if change_type is ChangeType.UPDATE.value:
                search_res = re.search(self.REGEX_UPDATE, change_detail)
                if search_res is None or search_res.lastindex < 2: continue
                old_name, new_name = search_res.groups()
                updated[old_name] = (ChangeType.UPDATE, new_name)
            elif change_type is ChangeType.CREATE.value:
                search_res = re.search(self.REGEX_CREATE_OR_DELETE, change_detail)
                if search_res is None or search_res.lastindex < 2: continue
                method_name, content = search_res.groups()
                updated[method_name] = (ChangeType.CREATE, content)
            elif change_type is ChangeType.REMOVE.value:
                search_res = re.search(self.REGEX_CREATE_OR_DELETE, change_detail)
                if search_res is None or search_res.lastindex < 2: continue
                method_name, content = search_res.groups()
                updated[method_name] = (ChangeType.REMOVE, content)
            # else if change_type is TYPE_NOCHANGE: continue
        return updated
