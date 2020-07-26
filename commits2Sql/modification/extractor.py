from typing import Dict, List, Tuple, Optional

from pydriller import Modification
from pydriller.domain.commit import Method

from modification.change_holder.class_holder import ClassHolder
from modification.change_holder.file_holder import FileHolder
from modification.change_holder.method_holder import MethodHolder


class Extractor(object):

    CLASS_METHOD_PARTITION = '::'

    def __init__(self, modification: Modification):
        after_set = set(modification.methods) # Created, Renamed_after, Modified_after, Unchanged, Relocated_after
        before_set = set(modification.methods_before) # Removed, Renamed_before, Modified_before, Unchanged, Relocated_before
        changed_set = set(modification.changed_methods) # Created, Removed, Renamed_after, Renamed_before, Modified_after
        name_unchanged = before_set & after_set # Modified, Unchanged, Modified_
        created_and_renamed_af = (after_set - name_unchanged) & changed_set # Created, Renamed_after
        removed_and_renamed_bf = (before_set - name_unchanged) & changed_set # Removed, Renamed_before
        modified = changed_set - (removed_and_renamed_bf | created_and_renamed_af) # Modified
        if removed_and_renamed_bf is None or created_and_renamed_af is None:
            removed, created, renamed = removed_and_renamed_bf, created_and_renamed_af, dict()
        else: pass

    def __handle_file(self, file: Modification) -> FileHolder:
        result = FileHolder()
        result.path_before = file.old_path
        result.path_current = file.old_path
        classes_before = self.__method_classify(file.methods_before)
        classes_current = self.__method_classify(file.methods)

        return result

    def __method_classify(self, methods: List[Method]) -> Dict[str:List[Method]]:
        output: Dict[str:List[Method]] = dict()
        for method in methods:
            names = method.name.rpartition(Extractor.CLASS_METHOD_PARTITION)
            if len(names) < 3: continue
            class_name = names[0]
            if class_name not in output: output[class_name] = list()
            output[class_name].append(method)
        return output

    def __handle_class(self, methods_before: List[Method], methods_current: List[Method]) -> ClassHolder: pass

    def __handle_method(self, method_before: Method, method_current) -> MethodHolder: pass

