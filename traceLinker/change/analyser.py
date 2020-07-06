import os
import subprocess

from traceLinker.change import ChangeIdentifier


class ModificationAnalyser(object): # Refactory Class for the identifier
    FILENAME_AFTER = 'after'
    FILENAME_BEFORE = 'before'
    CMD_DIFF = 'gumtree textdiff {before} {after}'

    def __init__(self, tmp_path: str):
        os.makedirs(tmp_path, exist_ok=True)
        self.__tmp_path = tmp_path

    def analyse(self, before: str, after: str, postfix: str) -> ChangeIdentifier:
        path_to_before = f'{self.__tmp_path}/{self.FILENAME_BEFORE}.{postfix}'
        path_to_after = f'{self.__tmp_path}/{self.FILENAME_AFTER}.{postfix}'
        with open(path_to_before, 'w') as f: f.write(before)
        with open(path_to_after, 'w') as f: f.write(after)
        diff_cmd = self.CMD_DIFF.format(before=path_to_before, after=path_to_after)
        exit_code, diff_output = subprocess.getstatusoutput(diff_cmd)
        if not exit_code == 0: raise Exception(f'FAIL TO EXECUTION {diff_cmd}')
        return ChangeIdentifier(diff_output)
