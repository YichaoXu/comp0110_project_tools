from typing import List

from traceLinker.change.utils import ChangeHolder


class FileChangeIdentifier(object):

    def __init__(self, diff_changes: ChangeHolder, driller_changes: List[str]):
        self.__changes = changes

    def get_renamed_methods(self):

