import re
from typing import Dict, Tuple, Optional
from modification.change_identifier.change_utils import CodeDiffer, ChangeClassifier, CodeAnalyser


class ChangeIdentifier(object):

    __INSTANCE: Optional[object] = None
    __DIFFER: Optional[CodeDiffer] = None
    __CODE_BEFORE: Optional[str] = None
    __CODE_AFTER: Optional[str] = None

    def __new__(cls, *args, **kw):
        if cls.__INSTANCE is None: cls.__INSTANCE = object.__new__(cls, *args, **kw)
        return cls.__INSTANCE

    def __init__(self, code_before: str, code_after: str):
        if self.__DIFFER is None: self.__DIFFER = CodeDiffer()
        if code_before == self.__CODE_BEFORE and code_after == self.__CODE_AFTER: return
        exe_code, diff_output = self.__DIFFER.compare(code_before, code_after)
        if not exe_code == 0: raise Exception(f'FAIL TO EXECUTION DIFF {diff_output}')
        self.__CODE_BEFORE = code_before
        self.__CODE_AFTER = code_after
        self.__before = CodeAnalyser(code_before)
        self.__after = CodeAnalyser(code_after)
        self.__changed_char_num_dict = ChangeClassifier(diff_output).updated_char_num_dict

    def __del__(self):
        del self.__DIFFER

    def new_classname_of(self, old_classname: str) -> Optional[str]:
        start_char_num = self.__before.get_start_char_num_of_class_name(old_classname)
        return self.__changed_char_num_dict[start_char_num] if start_char_num in self.__changed_char_num_dict else None

    def new_lines_num_of(self, old_line_num: int) -> Optional[int]:
        char_range = self.__before.get_char_num_range(old_line_num)
        if char_range is None: return None
        for char_before, char_current in self.__changed_char_num_dict.keys():
            if char_range[0] <= char_before < char_range[1]: return self.__after.get_line_num(char_current)
        return None



        



