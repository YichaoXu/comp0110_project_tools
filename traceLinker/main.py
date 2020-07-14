import re
from datetime import datetime
from typing import List, Dict

from pydriller import RepositoryMining
from pydriller.domain.commit import Method, Modification

from traceLinker.change import cType, FileChangeAnalyser
from traceLinker.database import TableHandlerFactory, Recorder


class Main(object):

    def __init__(
            self, tmp_data_dir: str, repos_path: str,
            start_date: datetime = None, end_date: datetime = None
    ):
        repos_name = repos_path.rpartition('/')[-1]
        self.__recorder = Recorder(TableHandlerFactory(tmp_data_dir, repos_name))
        self.__repository = RepositoryMining(repos_path, since=start_date, to=end_date)
        self.__analyser = FileChangeAnalyser(tmp_data_dir)

    def mining(self, src_sub_path: str = 'src', test_sub_path: str = 'test'):
        for commit in self.__repository.traverse_commits():
            if self.__recorder.is_record_before(commit.hash): continue
            for changed_file in commit.modifications:
                path_before = changed_file.old_path
                path_after = changed_file.new_path
                if test_sub_path not in path_after and src_sub_path not in path_after: continue
                if path_before is None: self.__create(changed_file, commit.hash)
                elif path_after is None: self.__delete(changed_file, commit.hash)
                elif path_before != path_after:  # Relocated file paths
                    self.__handle_file_modify(commit.hash, changed_file)
                else:  # Path did not changed
                    self.__handle_file_modify(commit.hash, changed_file)
            self.__recorder.record_git_commit(commit.hash, commit.author_date)

    def __create(self, file: Modification, commit_hash: str) -> None:
        class_extractor = Main.ClassExtractor(file)
        for class_name in class_extractor.get_all_class_names():
            for method_name in class_extractor.get_method_names_in(class_name):
                method_id = self.__recorder.get_method_id(method_name, class_name, file.new_path)
                self.__recorder.record_add_method(method_id, commit_hash)
        return None

    def __delete(self, file: Modification, commit_hash: str) -> None:
        class_extractor = Main.ClassExtractor(file)
        for class_name in class_extractor.get_all_class_names():
            for method_name in class_extractor.get_method_names_in(class_name):
                method_id = self.__recorder.get_method_id(method_name, class_name, file.new_path)
                self.__recorder.record_remove_method(method_id, commit_hash)
        return None

    def __relocate(self, file: Modification, commit_hash: str) -> None:
        self.__recorder.record_file_relocate(file.old_path, file.new_path)
        class_extractor = Main.ClassExtractor(file)
        file_suffix = file.filename.rpartition('.')[-1]
        identifier = self.__analyser.analyse(file.source_code_before, file.source_code, file_suffix)
        for class_name in class_extractor.get_all_class_names():
            identifier.get_method_change_type()
            for method_name in class_extractor.get_method_names_in(class_name):
                method_id = self.__recorder.get_method_id(method_name, class_name, file.new_path)
                self.__recorder.record_remove_method(method_id, commit_hash)
        return None

    def __handle_file_modify(self, hash: str, file_id: int, file: Modification):
        recorder = self.__recorder
        analyser = self.__analyser
        if set(file.methods_before) == set(file.methods): return
        identifier = analyser.analyse(file.source_code_before, file.source_code, file.filename.rpartition('.')[-1])
        class_extractor = Main.ClassExtractor(file)
        for class_name in class_extractor.get_all_class_names():
            change_type, change_detail = identifier.get_method_change_type(class_name)
            if change_type == str(cType.UPDATE):
                class_id = recorder.for_class.rename(class_name, change_detail, file_id)
            else:
                class_id = recorder.for_class.start(class_name, file_id)
            for method_name in class_extractor.get_method_names_in(class_name):
                change_type, change_detail = identifier.get_method_change_type(method_name)
                if change_type == str(cType.NOCHANGE): continue
                if change_type == str(cType.UPDATE):
                    method_id = recorder.for_method.rename(method_name, change_detail, class_id)
                else:
                    method_id = recorder.for_method.start(method_name, class_id)
                recorder.for_method.change(change_type, method_id, hash)

    class ClassExtractor(object):

        def __init__(self, modified_file: Modification):
            core_dict: Dict[str, List[str]] = {}
            for method in modified_file.changed_methods:
                class_name, _, method_name = str(method.name).rpartition('::')
                if not class_name or not method_name: continue
                core_dict.setdefault(class_name, []).append(method_name)
            self.__core_dict = core_dict

        def get_all_class_names(self) -> List[str]:
            return list(self.__core_dict.keys())

        def get_method_names_in(self, class_name: str) -> List[str]:
            return self.__core_dict.setdefault(class_name, [])
