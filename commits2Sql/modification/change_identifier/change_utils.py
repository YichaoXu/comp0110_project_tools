import re
import errno
import shutil
import subprocess
import tempfile
from typing import List, Tuple, Dict, Set, Any, Optional


class CodeAnalyser(object):

    __REGEX_CLASS_DECLARATION = r'(?P<before_name>class\s+)(?P<name>\w+)(?<after_name>\s*{)'

    def __init__(self, code: str):
        self.code = code
        total_char_num = 0
        matching_char_nums: List[int] = [-1]
        for each_line in code.splitlines(True):
            matching_char_nums.append(total_char_num)
            total_char_num += len(each_line)
        matching_char_nums.append(total_char_num)
        self.__matching_char_nums = matching_char_nums
        class_name_char_nums: Dict[str, Tuple[int, int]] = dict()
        for match in re.finditer(self.__REGEX_CLASS_DECLARATION, code):
            if match is not None and match.lastindex == 3:
                before_target = match.group('before_name')
                after_target = match.group('after_name')
                target = match.group('name')
                start = match.span()[0] + len(before_target)
                end = match.span()[1] - len(after_target)
                class_name_char_nums[target] = (start,end)
        self.__class_name_char_nums = class_name_char_nums

    def get_line_num(self, char_num: int) -> int:
        for line_num, start_num in enumerate(self.__matching_char_nums, start=1):
            if start_num > char_num: return line_num - 1
        return -1

    def get_char_num_range(self, line_num: int) -> Optional[Tuple[int, int]]:
        if len(self.__matching_char_nums) <= line_num + 1: return -1, -1
        start_of_target = self.__matching_char_nums[line_num]
        end_of_target = self.__matching_char_nums[line_num + 1] - 1
        return start_of_target, end_of_target

    def get_start_char_num_of_class_name(self, class_name: str) -> int:
        if class_name in self.__class_name_char_nums: return -1
        return self.__class_name_char_nums[class_name][0]
        


class CodeDiffer(object):
    __NAME_AFTER = 'after'
    __NAME_BEFORE = 'before'
    __SUFFIX = 'java'
    __CMD_DIFF = 'gumtree textdiff {before} {after}'

    def __init__(self):
        self.__tmp_dir = tempfile.mkdtemp()

    def __del__(self):
        try:
            if self.__tmp_dir is not None: shutil.rmtree(self.__tmp_dir)
        except OSError as exc:
            if exc.errno != errno.ENOENT: raise

    def compare(self, before: str, after: str) -> Tuple[int, str]:
        if before == after: return 0, ''
        path_before = f'{self.__tmp_dir}/{self.__NAME_BEFORE}.{self.__SUFFIX}'
        with open(path_before, 'w') as f: f.write(before)
        path_after = f'{self.__tmp_dir}/{self.__NAME_AFTER}.{self.__SUFFIX}'
        with open(path_after, 'w') as f: f.write(after)
        diff_cmd = self.__CMD_DIFF.format(before=path_before, after=path_after)
        return subprocess.getstatusoutput(diff_cmd)


class ChangeClassifier(object):
    __SPLIT_ALL_CHANGES = '===\n'
    __SPLIT_TYPE_DETAIL = '\n---\n'

    __TYPE_MATCH = 'match'
    __TYPE_UPDATE = 'update-node'
    __TYPE_INSERT = 'insert-tree'
    __TYPE_DELETE = 'delete-tree'

    __REGEX_MATCH_NAME = r'^SimpleName: (?P<old_name>\w+) \[(?P<old_start>\d+),(?P<old_end>\d+)\][\n\r]' \
                         r'SimpleName: (?P<new_name>\w+) \[(?P<new_start>\d+),(?P<old_end>\d+)\]'
    __REGEX_UPDATE_NAME = r'^SimpleName:.*\[(?P<old_start>\d+),(?P<old_end>\d+)\][\n\r]' \
                          r'replace (?<old_name>\w+) by (?<new_name>\w+)'
    __REGEX_NEW_OR_DEL = r'^(?P<type>MethodDeclaration|TypeDeclaration) \[(?P<start>\d+),(?P<end>\d+)\]'

    def __init__(self, diff_txt: str):
        matched, updated, inserted, deleted = list(), list(), list(), list()
        for change_diff in diff_txt.split(self.__SPLIT_ALL_CHANGES):
            change_type, _, change_detail = change_diff.partition(self.__SPLIT_TYPE_DETAIL)
            if change_type == self.__TYPE_MATCH: matched.append(change_detail)
            elif change_type == self.__TYPE_UPDATE: updated.append(change_detail)
            elif change_type == self.__TYPE_INSERT: inserted.append(change_detail)
            elif change_detail == self.__TYPE_DELETE: deleted.append(change_detail)
        names_match_char_num: Dict[int, int] = dict()
        for match_detail in matched:
            res = re.match(self.__REGEX_MATCH_NAME, match_detail)
            if res is None: continue
            res_dict = res.groupdict()
            if 'old_start' not in res_dict or 'new_start' not in res_dict: continue
            old_start, new_start = int(res_dict['old_start']), int(res_dict['new_start'])
            names_match_char_num[old_start] = new_start
        renamed_char_nums: Dict[int, int] = dict()
        for update_detail in updated:
            res = re.match(self.__REGEX_UPDATE_NAME, update_detail)
            res_dict = res.groupdict()
            if res is None or 'old_start' not in res_dict: continue
            old_start_char_num = int(res.group('old_start'))
            if old_start_char_num not in names_match_char_num: continue
            renamed_char_nums[old_start_char_num] = names_match_char_num[old_start_char_num]
        self.updated_char_num_dict = renamed_char_nums
