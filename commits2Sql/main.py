from datetime import datetime

from pydriller import RepositoryMining
from pydriller.domain.commit import Modification
from commits2sql.database import TableHandlerFactory, Recorder
from commits2sql.modification import ModificationAnalyser
from modification.change_classfier.change_type import ChangeType


class Main(object):

    def __init__(
            self, tmp_data_dir: str, repos_path: str,
            start_date: datetime = None, end_date: datetime = None
    ):
        repos_name = repos_path.rpartition('/')[-1]
        self.__analyser = ModificationAnalyser(tmp_data_dir)
        self.__recorder = Recorder(TableHandlerFactory(tmp_data_dir, repos_name))
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
        extractor = self.__analyser.extract({method.name for method in file.methods})
        for class_name in extractor.get_all_class_names():
            for method_name in extractor.get_method_names_in(class_name):
                method_id = self.__recorder.get_method_id(method_name, class_name, file.new_path)
                self.__recorder.record_add_method(method_id, commit_hash)
        return None

    def __delete(self, file: Modification, commit_hash: str) -> None:
        extractor = self.__analyser.extract({method.name for method in file.methods_before})
        for class_name in extractor.get_all_class_names():
            for method_name in extractor.get_method_names_in(class_name):
                method_id = self.__recorder.get_method_id(method_name, class_name, file.old_path)
                self.__recorder.record_remove_method(method_id, commit_hash)
        return None

    def __relocate(self, file: Modification, commit_hash: str) -> None:
        self.__recorder.record_file_relocate(file.old_path, file.new_path)
        return self.__modify(file, commit_hash)

    def __modify(self, file: Modification, commit_hash: str) -> None:
        set_after = {method.name for method in file.methods}
        set_before = {method.name for method in file.methods_before}

        modified = set_after.intersection(set_before)
        modified_extractor = self.__analyser.extract(modified)
        for class_name in modified_extractor.get_all_class_names():
            for method_name in modified_extractor.get_method_names_in(class_name):
                method_id = self.__recorder.get_method_id(method_name, class_name, file.new_path)
                self.__recorder.record_modify_method(method_id, commit_hash)

        if set_after == set_before: return
        suffix = file.filename.rpartition('.')[-1]
        report = self.__analyser.analyse(file.source_code_before, file.source_code, suffix)

        previous_and_removed = set_before.difference(modified)
        removed_extractor = self.__analyser.extract(previous_and_removed)
        for class_name in removed_extractor.get_all_class_names():
            class_change_type, class_new_name = report.get_change_type_and_details(class_name)
            if class_change_type is ChangeType.UPDATE:
                try:
                    self.__recorder.record_rename_class(file.new_path, class_name, class_new_name)
                    class_name = class_new_name
                except:
                    print(f'COLLISION FOR CLASS NAME:{class_name} IN COMMIT:{commit_hash}')
            for method_name in removed_extractor.get_method_names_in(class_name):
                change_type, change_detail = report.get_change_type_and_details(method_name)
                if change_type is not ChangeType.REMOVE: continue
                previous_and_removed.remove(f'{class_name}::{method_name}')
                method_id = self.__recorder.get_method_id(method_name, class_name, file.new_path)
                self.__recorder.record_remove_method(method_id, commit_hash)

        current_and_added = set_after.difference(modified)
        added_extractor = self.__analyser.extract(current_and_added)
        for class_name in added_extractor.get_all_class_names():
            for method_name in added_extractor.get_method_names_in(class_name):
                change_type, change_detail = report.get_change_type_and_details(method_name)
                if change_type is not ChangeType.CREATE: continue
                current_and_added.remove(f'{class_name}::{method_name}')
                method_id = self.__recorder.get_method_id(method_name, class_name, file.new_path)
                self.__recorder.record_add_method(method_id, commit_hash)

        rename_extractor = self.__analyser.extract(previous_and_removed)
        for class_name in rename_extractor.get_all_class_names():
            for method_name in rename_extractor.get_method_names_in(class_name):
                change_type, change_detail = report.get_change_type_and_details(method_name)
                if change_type is not ChangeType.UPDATE: continue
                if f'{class_name}::{change_detail}' not in current_and_added: continue
                method_id = self.__recorder.get_method_id(method_name, class_name, file.new_path)
                try: self.__recorder.record_rename_method(method_id, change_detail, commit_hash)
                except: print(f'COLLISION FOR METHOD ID:{method_id} IN COMMIT:{commit_hash}')
