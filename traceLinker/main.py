import re
from datetime import datetime
from typing import List, Dict

from pydriller import RepositoryMining
from pydriller.domain.commit import Method, Modification

from traceLinker.change import cType, ModificationAnalyser
from traceLinker.record import RecorderFactory


class Main(object):

    def __init__(
            self, tmp_data_dir: str, repos_path: str,
            start_date: datetime = None, end_date: datetime = None
    ):
        repos_path = repos_path
        self.__repository = RepositoryMining(repos_path, since=start_date, to=end_date)
        self.__analyser = ModificationAnalyser(tmp_data_dir)
        self.__recorder = RecorderFactory(tmp_data_dir, repos_path.rpartition('/')[-1])

    def mining(self, src_sub_path: str = 'src', test_sub_path: str = 'test'):
        recorder = self.__recorder
        repository = self.__repository
        for commit in repository.traverse_commits():
            recorder.for_commit.start_record(commit.hash, commit.author_date)
            if recorder.for_commit.is_recorded_before():
                recorder.for_commit.end_record()
                continue
            for changed_file in commit.modifications:
                path_before = changed_file.old_path
                path_after = changed_file.new_path
                if path_before is None:  # Created new file
                    if test_sub_path not in path_after and src_sub_path not in path_after: continue
                    file_id = recorder.for_file.new(path_after)
                    self.__handle_create_or_remove_file(commit.hash, file_id, changed_file, cType.CREATE)
                elif path_after is None:  # Removed previous file
                    if test_sub_path not in path_before and src_sub_path not in path_before: continue
                    file_id = recorder.for_file.new(path_before)
                    self.__handle_create_or_remove_file(commit.hash, file_id, changed_file, cType.REMOVE)
                elif path_before != path_after:  # Relocated file paths
                    if test_sub_path not in path_after and src_sub_path not in path_after: continue
                    file_id = recorder.for_file.record_relocate(path_before, path_after)
                    self.__handle_file_modify(commit.hash, file_id, changed_file)
                else:  # Path did not changed
                    if test_sub_path not in path_after and src_sub_path not in path_after: continue
                    file_id = recorder.for_file.new(path_before)
                    self.__handle_file_modify(commit.hash, file_id, changed_file)
            recorder.for_commit.end_record()

    def __handle_create_or_remove_file(self, hash: str, file_id: int, file: Modification, change_type: cType):
        recorder = self.__recorder
        class_extractor = Main.ClassExtractor(file)
        for class_name in class_extractor.get_all_class_names():
            class_id = recorder.for_class.new(class_name, file_id)
            for method_name in class_extractor.get_method_names_in(class_name):
                method_id = recorder.for_method.new(method_name, class_id)
                recorder.for_method.change(str(change_type), method_id, hash)

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
                class_id = recorder.for_class.new(class_name, file_id)
            for method_name in class_extractor.get_method_names_in(class_name):
                change_type, change_detail = identifier.get_method_change_type(method_name)
                if change_type == str(cType.NOCHANGE): continue
                if change_type == str(cType.UPDATE):
                    method_id = recorder.for_method.rename(method_name, change_detail, class_id)
                else:
                    method_id = recorder.for_method.new(method_name, class_id)
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
