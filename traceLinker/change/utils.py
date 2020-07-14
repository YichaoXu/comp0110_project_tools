from enum import Enum
from typing import List, Tuple, Dict
from pydriller import Modification


class ChangeHolder(object):

    def __init__(self):
        self.removed: List[str] = []
        self.created: List[str] = []
        self.updated: List[str] = []
        self.renamed_pairs: Dict[str, str] = {}

class ClassExtractor(object):

    def __init__(self, modified_file: Modification):
        core_dict: Dict[str, List[str]] = {}
        for method in modified_file.changed_methods:
            class_name, _, method_name = str(method.name).rpartition('::')
            if not class_name or not method_name: continue
            core_dict.setdefault(class_name, []).append(method_name)
        self.__core_dict = core_dict

    def get_all_class_names(self) -> List[str]:
        return list(self.__core_dict.keys())

    def get_method_names_in(self, class_name: str) -> List[str]:
        return self.__core_dict.setdefault(class_name, [])


class ChangeType(Enum):
    NOCHANGE = 'match'
    UPDATE = 'update-node'
    CREATE = 'insert-tree'
    REMOVE = 'delete-tree'

    def __str__(self):
        return self.value
