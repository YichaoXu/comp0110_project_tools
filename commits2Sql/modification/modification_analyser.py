import os
from typing import List, Iterable

from commits2sql.modification.diff_analysis_report import AnalysisReport
from commits2sql.modification.driller_modification_extractor import ModificationExtractor

FILENAME_AFTER = 'after'
FILENAME_BEFORE = 'before'


class ModificationAnalyser(object):

    def __init__(self, tmp_path: str):
        os.makedirs(tmp_path, exist_ok=True)
        self.__tmp_path = tmp_path

    def analyse(self, code_before: str, code_after: str, suffix: str) -> AnalysisReport:
        path_to_before = f'{self.__tmp_path}/{FILENAME_BEFORE}.{suffix}'
        path_to_after = f'{self.__tmp_path}/{FILENAME_AFTER}.{suffix}'
        with open(path_to_before, 'w') as f: f.write(code_before)
        with open(path_to_after, 'w') as f: f.write(code_after)
        return AnalysisReport(path_to_before, path_to_after)

    def extract(self, method: Iterable[str]) -> ModificationExtractor:
        return ModificationExtractor(method)
