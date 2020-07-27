import errno
import shutil
import subprocess
import tempfile
from typing import List, Tuple


class LineNumberCalculator(object):

    def __init__(self, code: str):
        total_char_num = 0
        core: List[int] = [-1]
        for each_line in code.split('\n'):
            core.append(total_char_num)
            total_char_num += len(each_line)
        self.__matching = core

    def get_line_num(self, char_num: int) -> int:
        for line_num, start_num in enumerate(self.__matching, start=1):
            if start_num > char_num: return line_num - 1
        return -1


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

    SPLIT_ALL_CHANGES = '===\n'
    SPLIT_TYPE_DETAIL = '\n---\n'

    REGEX_CLASS_CREATE_OR_DELETE = r'^TypeDeclaration\s*\[(?P<range>.+)\]'
    REGEX_METHOD_CREATE_OR_DELETE = r'^MethodDeclaration\s*\[(?P<range>.+)\]'

    REGEX_UPDATE_NAME = r'^SimpleName:.*\[(?P<old_range>.+)\][ |\n|\r]*' \
                        r'replace (?<old_name>.+) by (?<new_name>.+)'
    REGEX_MATCH_NAME = r'^SimpleName: (?P<old_name>.+) \[(?P<old_range>.+)\][\n\r]' \
                       r'SimpleName: (?P<new_name>.+) \[(?P<new_range>.+)\]'
