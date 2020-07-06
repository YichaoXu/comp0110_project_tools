import re
from traceLinker.change.type import cType


class ChangeIdentifier(object):

    SPLIT_TREE = '===\n'
    SPLIT_DATA = '\n---\n'

    REGEX_CREATE_OR_DELETE = 'SimpleName:(.*)\[.*\]'
    REGEX_UPDATE = 'replace (.*) by (.*)'

    def __init__(self, diff_output: str):
        self.__updated = {}  # {method_name : (method_type, new_name)}

        for change in diff_output.split(self.SPLIT_TREE):
            tmp_data_list = change.split(self.SPLIT_DATA)
            if len(tmp_data_list) < 2: continue
            change_type, change_detail = tmp_data_list
            change_detail = change_detail.replace('\n', '')
            if change_type == cType.UPDATE:
                search_res = re.search(self.REGEX_UPDATE, change_detail)
                if search_res is None or search_res.lastindex < 2: continue
                old_method_name = search_res.group(1)
                new_method_name = search_res.group(2)
                self.__updated[old_method_name] = (change_type, new_method_name)
            elif change_type in [cType.CREATE, cType.REMOVE]:
                search_res = re.search(self.REGEX_CREATE_OR_DELETE, change_detail)
                if search_res is None or search_res.lastindex < 1: continue
                method_name = search_res.group(1)
                self.__updated[method_name] = (change_type, None)
            # else if change_type is TYPE_NOCHANGE: continue
        self.__diff_text = diff_output

    def get_method_change_type(self, previous_method_name) -> (cType, str):
        if previous_method_name not in self.__updated:
            return cType.NOCHANGE, None
        else:
            return self.__updated[previous_method_name]
