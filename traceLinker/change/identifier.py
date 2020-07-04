import re

class ChangeIdentifier:
    SPLIT_TREE = '===\n'
    SPLIT_DATA = '\n---\n'

    TYPE_NOTCHANGE = 'match'
    TYPE_UPDATE = 'update-node'
    TYPE_CREATE = 'insert-tree'
    TYPE_REMOVE = 'delete-tree'

    REGEX_CREATE_OR_DELETE = 'SimpleName:(.*)\[.*\]'
    REGEX_UPDATE = 'replace (.*) by (.*)'

    def __init__(self, diff_output: str):
        self.__updated = {}  # from => to
        self.__created = []
        self.__removed = []
        for change in diff_output.split(self.SPLIT_TREE):
            tmp_data_list = change.split(self.SPLIT_DATA)
            if len(tmp_data_list) < 2: continue
            change_type, change_detail = tmp_data_list
            change_detail = change_detail.replace('\n', '')
            if change_type == self.TYPE_UPDATE:
                change_regex_search_res = re.search(self.REGEX_UPDATE, change_detail)
                old_method_name = change_regex_search_res.group(1)
                new_method_name = change_regex_search_res.group(2)
                self.__updated[old_method_name] = new_method_name
                continue
            elif change_type == self.TYPE_CREATE:
                search_res = re.search(self.REGEX_CREATE_OR_DELETE, change_detail)
                if search_res is None: continue
                self.__created.append(search_res.group(1))
            elif change_type == self.TYPE_REMOVE:
                search_res = re.search(self.REGEX_CREATE_OR_DELETE, change_detail)
                if search_res is None: continue
                self.__removed.append(search_res.group(1))
            # else if change_type is TYPE_NOCHANGE: continue
        self.__diff_text = diff_output

    def is_created(self, before: str) -> bool:
        return before in self.__created

    def is_removed(self, before: str) -> bool:
        return before in self.__removed

    def is_updated(self, before: str) -> bool:
        return before in self.__updated

    def get_updated_value(self, before: str) -> str:
        return self.__updated[before]
