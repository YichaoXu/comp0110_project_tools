import re
from datetime import datetime
from pydriller import RepositoryMining
from traceLinker.recorder import CommitRecorder
from traceLinker.identifier import ChangeIdentifier


class Main:

    def __init__(self, repos_path: str,
                 src_sub_path: str = 'src',
                 test_sub_path: str = 'test'
                 ):
        start_date = datetime(2019, 7, 1)
        self.__repository = RepositoryMining(repos_path, since=start_date)
        self.__recorder = CommitRecorder()
        self.__src_sub_path = src_sub_path
        self.__test_sub_path = test_sub_path

    def __handle_create_file(self, methods, file_path: str):
        for each_name in methods:
            if self.__test_sub_path in file_path:
                self.__recorder.add_test(each_name)
            elif self.__src_sub_path in file_path:
                self.__recorder.add_source(each_name)

    def __handle_remove_file(self, methods, file_path: str):
        for each_name in methods:
            if self.__test_sub_path in file_path:
                self.__recorder.remove_test(each_name)
            elif self.__src_sub_path in file_path:
                self.__recorder.remove_source(each_name)

    def __handle_modify_file(self, method_names_list, before: str, after: str, file_path: str):
        identifier = ChangeIdentifier(before, after, file_path.split('.')[-1])
        for m_name in method_names_list:
            if identifier.is_created(m_name):
                if self.__test_sub_path in file_path:
                    self.__recorder.add_test(m_name)
                elif self.__src_sub_path in file_path:
                    self.__recorder.add_source(m_name)
            elif identifier.is_removed(m_name):
                if self.__test_sub_path in file_path:
                    self.__recorder.remove_test(m_name)
                elif self.__src_sub_path in file_path:
                    self.__recorder.remove_source(m_name)
            elif identifier.is_updated(m_name):
                if self.__test_sub_path in file_path: continue
                new_name = identifier.get_updated_value(m_name)
                self.__recorder.change_name(m_name, new_name)

    def __is_modify_only(self, mn_before_list: list, mn_after_list: list) -> bool:
        if len(mn_before_list) != len(mn_after_list): return False
        for method_name in mn_before_list:
            if method_name not in mn_after_list: return False
        return True

    def run(self):
        for commit in self.__repository.traverse_commits():
            for modification in commit.modifications:
                code_after = modification.source_code
                code_before = modification.source_code_before
                all_changed = (
                    re.sub('(.*)::', "", method.name, count=1)
                    for method in modification.changed_methods
                )
                if code_before is None:  # Handle File Creation
                    self.__handle_create_file(all_changed, modification.new_path)
                elif code_after is None:  # Handle File Deletion
                    self.__handle_remove_file(all_changed, modification.old_path)
                else:  # Handle File Modification
                    mn_before = [method.name for method in modification.methods_before]
                    mn_after = [method.name for method in modification.methods]
                    if self.__is_modify_only(mn_before, mn_after): continue
                    self.__handle_modify_file(all_changed, code_before, code_after, modification.new_path)
            self.__recorder.next_commit()
