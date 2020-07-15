from datetime import datetime

from pydriller import RepositoryMining
from pydriller.domain.commit import Modification
from commits2sql.database import TableHandlerFactory, DbRecorder
from commits2sql.modification import ModificationAnalyser
from commits2sql.modification.utils import ChangeType


class Main(object):

    def __init__(
            self, tmp_data_dir: str, repos_path: str,
            start_date: datetime = None, end_date: datetime = None
    ):
        repos_name = repos_path.rpartition('/')[-1]
        self.__analyser = ModificationAnalyser(tmp_data_dir)
        self.__recorder = DbRecorder(TableHandlerFactory(tmp_data_dir, repos_name))
        self.__repository = RepositoryMining(repos_path, since=start_date, to=end_date)

    def mining(self):
        for commit in self.__repository.traverse_commits():
            if self.__recorder.is_record_before(commit.hash): continue
            for changed_file in commit.modifications:
                if changed_file.old_path is None:
                    self.__create(changed_file, commit.hash)
                elif changed_file.new_path is None:
                    self.__delete(changed_file, commit.hash)
                elif changed_file.new_path != changed_file.old_path:
                    self.__relocate(changed_file, commit.hash)
                else:
                    self.__modify(changed_file, commit.hash)
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
        if set(file.methods) == set(file.methods_before):
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
            class_change_type, class_new_name = report.get_change_type_and_details(class_name)
            possible_methods = set(extractor.get_method_names_in(class_name))
            if class_change_type is ChangeType.UPDATE:
                self.__recorder.record_rename_class(file.new_path, class_name, class_new_name)
                possible_methods += extractor.get_method_names_in(class_new_name)
                class_name = class_new_name
            created, deleted, modified, renamed = set(), set(), set(), dict()
            for method_name in possible_methods:
                change_type, change_detail = report.get_change_type_and_details(method_name)
                if change_type is ChangeType.CREATE: created.add(method_name)
                elif change_type is ChangeType.REMOVE: deleted.add(method_name)
                elif change_type is ChangeType.UPDATE: renamed[method_name] = change_detail
                else: modified.add(method_name)
            modified -= set(renamed.values())
            for method_name in created:
                method_id = self.__recorder.get_method_id(method_name, class_name, file.new_path)
                self.__recorder.record_add_method(method_id, commit_hash)
            for method_name in deleted:
                method_id = self.__recorder.get_method_id(method_name, class_name, file.new_path)
                self.__recorder.record_remove_method(method_id, commit_hash)
            for method_name in modified:
                method_id = self.__recorder.get_method_id(method_name, class_name, file.new_path)
                self.__recorder.record_modify_method(method_id, commit_hash)
            for method_name in renamed.keys():
                method_id = self.__recorder.get_method_id(method_name, class_name, file.new_path)
                self.__recorder.record_rename_method(method_id, renamed[method_name], commit_hash)
        return None
