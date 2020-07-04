import os
import re
import subprocess

CMD_DIFF = 'gumtree textdiff {before} {after}'

PATH_TO_TMP = '../tmp'
FILENAME_BEFORE = 'before'
FILENAME_AFTER = 'after'

SPLIT_TREE = '===\n'
SPLIT_DATA = '\n---\n'
SPLIT_POSITION = ','

TYPE_NOTCHANGE = 'match'
TYPE_UPDATE = 'update-node'
TYPE_CREATE = 'insert-tree'
TYPE_REMOVE = 'delete-tree'

REGEX_CREATE_OR_DELETE = 'SimpleName:(.*)\[.*\]'
REGEX_UPDATE = 'replace (.*) by (.*)'


class ChangeIdentifier:

    def __init__(self, before: str, after: str, postfix: str):
        # Invoke GumTree to obtain diff result
        self.__updated = {}  # from:str => to: str
        self.__created = []  # name: str
        self.__removed = []  # name: str

        if not os.path.exists(PATH_TO_TMP):
            os.makedirs(PATH_TO_TMP)
        path_to_file_before = f'{PATH_TO_TMP}/{FILENAME_BEFORE}.{postfix}'
        with open(path_to_file_before, 'w') as f:
            f.write(before)
        path_to_file_after = f'{PATH_TO_TMP}/{FILENAME_AFTER}.{postfix}'
        with open(path_to_file_after, 'w') as f:
            f.write(after)
        diff_cmd = CMD_DIFF.format(before=path_to_file_before, after=path_to_file_after)
        exit_code, diff_output = subprocess.getstatusoutput(diff_cmd)
        if not exit_code == 0: raise Exception(f'WARNING: FAIL EXECUTION {diff_cmd}')

        # Extract changed methods
        change_list = diff_output.split(SPLIT_TREE)
        for change in change_list:
            tmp_data_list = change.split(SPLIT_DATA)
            if len(tmp_data_list) < 2: continue
            change_type, change_detail = tmp_data_list
            change_detail = str(change_detail).replace('\n', '')
            if change_type == TYPE_UPDATE:
                change_regex_search_res = re.search(REGEX_UPDATE, change_detail)
                before_method = change_regex_search_res.group(1)
                after_method = change_regex_search_res.group(2)
                self.__updated[before_method] = after_method
                continue
            elif change_type == TYPE_CREATE:
                search_res = re.search(REGEX_CREATE_OR_DELETE, change_detail)
                if search_res is None: continue
                self.__created.append(search_res.group(1))
            elif change_type == TYPE_REMOVE:
                search_res = re.search(REGEX_CREATE_OR_DELETE, change_detail)
                if search_res is None: continue
                self.__removed.append(search_res.group(1))
            # else if change_type is TYPE_NOCHANGE: continue
        self.__diff_text = diff_output

    def is_created(self, before: str) -> bool:
        return before in self.__created

    def is_removed(self, before: str) -> bool:
        return before in self.__removed

    def is_updated(self, before: str) -> bool:
        return before in self.__updated

    def get_updated_value(self, before: str) -> str:
        return self.__updated[before]
