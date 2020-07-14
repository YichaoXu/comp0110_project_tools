from datetime import datetime
from pydriller import RepositoryMining
from pydriller.domain.commit import Modification
from traceLinker.database import TableHandlerFactory, DbRecorder
from traceLinker.modification import ModificationAnalyser
from traceLinker.modification.utils import ChangeType


class Main(object):

    def __init__(
            self, tmp_data_dir: str, repos_path: str,
            start_date: datetime = None, end_date: datetime = None
    ):
        repos_name = repos_path.rpartition('/')[-1]
        self.__analyser = ModificationAnalyser(tmp_data_dir)
        self.__recorder = DbRecorder(TableHandlerFactory(tmp_data_dir, repos_name))
        self.__repository = RepositoryMining(repos_path, since=start_date, to=end_date)

    def mining(self, src_sub_path: str = 'src', test_sub_path: str = 'test'):
        for commit in self.__repository.traverse_commits():
            if self.__recorder.is_record_before(commit.hash): continue
            for changed_file in commit.modifications:
                path_before = changed_file.old_path
                path_after = changed_file.new_path
                if path_before is None: self.__create(changed_file, commit.hash)
                elif path_after is None: self.__delete(changed_file, commit.hash)
                elif path_before != path_after: self.__relocate(changed_file, commit.hash)
                else: self.__modify(changed_file, commit.hash)
            self.__recorder.record_git_commit(commit.hash, commit.author_date)

    def __create(self, file: Modification, commit_hash: str) -> None:
        extractor = self.__analyser.extract([method.name for method in file.methods])
        for class_name in extractor.get_all_class_names():
            for method_name in extractor.get_method_names_in(class_name):
                method_id = self.__recorder.get_method_id(method_name, class_name, file.new_path)
                self.__recorder.record_add_method(method_id, commit_hash)
        return None

    def __delete(self, file: Modification, commit_hash: str) -> None:
        extractor = self.__analyser.extract([method.name for method in file.methods_before])
        for class_name in extractor.get_all_class_names():
            for method_name in extractor.get_method_names_in(class_name):
                method_id = self.__recorder.get_method_id(method_name, class_name, file.old_path)
                self.__recorder.record_remove_method(method_id, commit_hash)
        return None

    def __relocate(self, file: Modification, commit_hash: str) -> None:
        self.__recorder.record_file_relocate(file.old_path, file.new_path)
        return self.__modify(file, commit_hash)

    def __modify(self, file: Modification, commit_hash: str) -> None:
        if set(file.methods_before) == set(file.methods):
            extractor = self.__analyser.extract([method.name for method in file.changed_methods])
            for class_name in extractor.get_all_class_names():
                for method_name in extractor.get_method_names_in(class_name):
                    method_id = self.__recorder.get_method_id(method_name, class_name, file.new_path)
                    self.__recorder.record_modify_method(method_id, commit_hash)
            return None
        suffix = file.filename.rpartition('.')[-1]
        extractor = self.__analyser.extract([method.name for method in file.changed_methods])
        report = self.__analyser.analyse(file.source_code_before, file.source_code, suffix)
        for class_name in extractor.get_all_class_names():
            change_type, change_name = report.get_change_type_and_details(class_name)
            possible_methods = set(extractor.get_method_names_in(class_name))
            if change_type is ChangeType.UPDATE:
                self.__recorder.record_rename_class(file.new_path, class_name, change_name)
                class_name = change_name
                possible_methods.update(extractor.get_method_names_in(class_name))
            for method_name in possible_methods:
                change_type, new_name = report.get_change_type_and_details(method_name)
                if change_type is not ChangeType.UPDATE: continue
                self.__recorder.record_rename_method(file.new_path, class_name, method_name, new_name)
                possible_methods.remove(method_name)
            for method_name in possible_methods:
                change_type, new_name = report.get_change_type_and_details(method_name)
                method_id = self.__recorder.get_method_id(method_name, class_name, file.new_path)
                if change_type is ChangeType.CREATE: self.__recorder.record_add_method(method_id, commit_hash)
                elif change_type is ChangeType.REMOVE: self.__recorder.record_remove_method(method_id, commit_hash)
                else: self.__recorder.record_modify_method(method_id, commit_hash)
