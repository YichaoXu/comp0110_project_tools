from typing import List, Dict


class ModificationExtractor(object):

    def __init__(self, methods: List[str]):
        core_dict: Dict[str, List[str]] = {}
        for method in methods:
            class_name, _, method_name = method.rpartition('::')
            if not class_name or not method_name: continue
            core_dict.setdefault(class_name, []).append(method_name)
        self.__core_dict = core_dict

    def get_all_class_names(self) -> List[str]:
        return list(self.__core_dict.keys())

    def get_method_names_in(self, class_name: str) -> List[str]:
        return self.__core_dict.setdefault(class_name, [])
