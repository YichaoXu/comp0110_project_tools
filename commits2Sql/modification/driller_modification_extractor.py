from typing import List, Dict, Iterable, Set


class ModificationExtractor(object):

    def __init__(self, methods: Iterable[str]):
        core_dict: Dict[str, Set[str]] = dict()
        for method in methods:
            class_name, _, method_name = method.rpartition('::')
            if not class_name or not method_name: continue
            core_dict.setdefault(class_name, set()).add(method_name)
        self.__core_dict = core_dict

    def get_all_class_names(self) -> Set[str]:
        return set(self.__core_dict.keys())

    def get_method_names_in(self, class_name: str) -> Set[str]:
        return self.__core_dict[class_name] if class_name in self.__core_dict else set()
