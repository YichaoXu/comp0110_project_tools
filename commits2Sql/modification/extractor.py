import re
from typing import Dict, List, Tuple, Optional

from pydriller import Modification
from pydriller.domain.commit import Method

from modification.change_holder.class_holder import ClassHolder
from modification.change_holder.file_holder import FileHolder
from modification.change_holder.method_holder import MethodHolder


ClassMethodsDict = Dict[str:List[Method]]

class Extractor(object):

    CLASS_METHOD_REGEX = r'(?P<class_name>\S+?(?:<.*>)*)::(?P<method_name>\S+?\(.*\))'

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


        return result

    def __method_classify(self, methods: List[Method]) -> ClassMethodsDict:
        output: ClassMethodsDict = dict()
        for method in methods:
            match_names = re.match(self.CLASS_METHOD_REGEX, method.long_name).groupdict()
            if 'class_name' not in match_names: continue
            class_name = match_names['class_name']
            if class_name not in output: output[class_name] = list()
            output[class_name].append(method)
        return output

    def __handle_classes(self, before: List[Method], current: List[Method], changed: List[Method]) -> List[ClassHolder]:
        classes_dict_before = self.__method_classify(before)
        classes_dict_current = self.__method_classify(current)
        classes_dict_changed = self.__method_classify(changed)
        c_names_before = set(classes_dict_before.keys()) # MD(RN_old, Non-RN), Non-MD(RN_old, Non-RN), RM
        c_names_current = set(classes_dict_current.keys()) # MD(RN_new, Non-RN), Non-MD(RN_new, Non-RN), CT
        c_names_changed = set(classes_dict_changed.keys()) # RM, CT, MD(RN_new, Non-RN)
        c_names_unrenamed = (c_names_before & c_names_current) # MD(Non-RN), Non-MD (Non-RN)
        c_names_oldname_and_removed = c_names_before - c_names_unrenamed # RN_old(MD, Non-MD), RM
        c_names_newname_and_created = c_names_current - c_names_unrenamed # RN_new(MD, Non-MD), CT
        c_names_removed = c_names_changed - (c_names_unrenamed | c_names_newname_and_created) # RM
        c_names_old = c_names_oldname_and_removed - c_names_removed # RN_old(MD, Non-MD)
        c_names_renamed = dict()
        if len(c_names_old) == 0: # No classes are renamed
            c_names_created = c_names_newname_and_created
        else: # certain of they are renamed, so it is essential to find them out by classifier
            for old_name in c_names_oldname:


            pass

    def __handle_method(self, method_before: Method, method_current) -> MethodHolder: pass

