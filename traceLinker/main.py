import re
from datetime import datetime
from pydriller import RepositoryMining

from traceLinker.change import ChangeIdentifier
from traceLinker.record import DataRecorder


class Main(object):

    def __init__(self, tmp_data_dir: str):
        self.__tmp_data_dir = tmp_data_dir

    def mining(
            self, repos_root_path: str, repos_name: str,
            start_date: datetime = None, end_date: datetime = None,
            src_sub_path: str = 'src', test_sub_path: str = 'test'
    ):
        repos_path = f'{repos_root_path}/{repos_name}'
        repository = RepositoryMining(repos_path, since=start_date, to=end_date)
        identifier = ChangeIdentifier(self.__tmp_data_dir)
        recorder = DataRecorder(self.__tmp_data_dir, repos_name)
        for commit in repository.traverse_commits():
            if recorder.is_recorded(commit.hash): continue
            recorder.start_commit(commit.hash, commit.author_date)
            for changed_file in commit.modifications:
                recorder.for_file(changed_file)
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
