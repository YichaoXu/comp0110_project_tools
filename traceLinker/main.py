import re
from datetime import datetime
from pydriller import RepositoryMining
from traceLinker.record import *
from traceLinker.change import *


class Main:

    def __init__(self, software_data_dir: str):
        self.__src_sub_path = None
        self.__test_sub_path = None
        self.__recorder = CommitRecorder(software_data_dir)
        self.__analyser = ModificationAnalyser(software_data_dir)

    def mining(
            self, repos_path: str,
            start_date: datetime = None, end_date: datetime = None,
            src_sub_path: str = 'src', test_sub_path: str = 'test'
    ):
        repository = RepositoryMining(repos_path, since=start_date, to=end_date)
        self.__src_sub_path = src_sub_path
        self.__test_sub_path = test_sub_path
        for commit in repository.traverse_commits():
            for changed_file in commit.modifications:
                code_after = changed_file.source_code
                code_before = changed_file.source_code_before
                all_changed = (
                    re.sub('(.*)::', "", method.name, count=1)
                    for method in changed_file.changed_methods
                )
                if code_before is None:  # Handle File Creation
                    self.__handle_create_file(all_changed, changed_file.new_path)
                elif code_after is None:  # Handle File Deletion
                    self.__handle_remove_file(all_changed, changed_file.old_path)
                else:  # Handle File Modification
                    mn_before = [method.name for method in changed_file.methods_before]
                    mn_after = [method.name for method in changed_file.methods]
                    if self.__is_modify_only(mn_before, mn_after): continue
                    self.__handle_modify_file(all_changed, code_before, code_after, changed_file.new_path)
            self.__recorder.next_commit()

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
        change = self.__analyser.analyse(before, after, file_path.split('.')[-1])
        for method_name in method_names_list:
            if change.is_created(method_name):
                if self.__test_sub_path in file_path:
                    self.__recorder.add_test(method_name)
                elif self.__src_sub_path in file_path:
                    self.__recorder.add_source(method_name)
            elif change.is_removed(method_name):
                if self.__test_sub_path in file_path:
                    self.__recorder.remove_test(method_name)
                elif self.__src_sub_path in file_path:
                    self.__recorder.remove_source(method_name)
            elif change.is_updated(method_name):
                if self.__test_sub_path in file_path: continue
                new_name = change.get_updated_value(method_name)
                self.__recorder.change_name(method_name, new_name)

    def __is_modify_only(self, mn_before_list: list, mn_after_list: list) -> bool:
        if len(mn_before_list) != len(mn_after_list): return False
        for method_name in mn_before_list:
            if method_name not in mn_after_list: return False
        return True
