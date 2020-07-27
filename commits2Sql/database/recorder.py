from datetime import datetime
from typing import Any
from database import TableHandlerFactory


class Recorder(object):

    def __init__(self, handler_factory: TableHandlerFactory):
        self.__table_handler = handler_factory

    def is_record_before(self, commit_hash: str) -> bool:
        return self.__table_handler.for_commits_table.is_hash_exist(commit_hash)

    def record_git_commit(self, commit_hash: str, commit_date: datetime) -> Any:
        result = self.__table_handler.for_commits_table.insert_new_commit(commit_hash, commit_date)
        self.__table_handler.for_commits_table.flash()
        return result

    def record_file_relocate(self, old_path: str, new_path: str) -> None:
        id_pairs = self.__table_handler.for_methods_table.find_crash_rows_of_relocate(old_path, new_path)
        for old_id, new_id in id_pairs:
            self.__table_handler.for_changes_table.update_target_method(new_id, old_id)
            self.__table_handler.for_methods_table.delete_methods_by_id(new_id)
        self.__table_handler.for_methods_table.update_path(old_path, new_path)
        self.__table_handler.for_methods_table.flash()
        return None

    def record_rename_class(self, path: str, old_class: str, new_class: str) -> None:
        methods_table = self.__table_handler.for_methods_table
        change_table = self.__table_handler.for_changes_table
        id_pairs = methods_table.find_crash_rows_of_class_rename(path, old_class, new_class)
        for old_id, new_id in id_pairs:
            change_table.update_target_method(new_id, old_id)
            methods_table.delete_methods_by_id(new_id)
        self.__table_handler.for_methods_table.update_class(path, old_class, new_class)
        self.__table_handler.for_methods_table.flash()
        return None

    def record_rename_method(self, method_id: int, new_name: str, commit_hash: str) -> None:
        methods_table = self.__table_handler.for_methods_table
        change_table = self.__table_handler.for_changes_table
        id_pairs = methods_table.find_crash_rows_of_method_rename(method_id, new_name)
        for old_id, new_id in id_pairs:
            change_table.update_target_method(new_id, old_id)
            methods_table.delete_methods_by_id(new_id)
        self.__table_handler.for_changes_table.insert_new_change("RENAME", method_id, commit_hash)
        self.__table_handler.for_methods_table.update_name(method_id, new_name)
        self.__table_handler.for_methods_table.flash()
        return None

    def get_method_id(self, method_name: str, class_name:str, path: str) -> int:
        return self.__table_handler.for_methods_table.select_method_id(method_name, class_name, path)

    def record_remove_method(self, method_id: int, commit_hash: str) -> int:
        change_table = self.__table_handler.for_changes_table
        return change_table.insert_new_change('REMOVE', method_id, commit_hash)

    def record_add_method(self, method_id: int, commit_hash: str) -> int:
        change_table = self.__table_handler.for_changes_table
        return change_table.insert_new_change('ADD', method_id, commit_hash)

    def record_modify_method(self, method_id: int, commit_hash: str) -> int:
        change_table = self.__table_handler.for_changes_table
        return change_table.insert_new_change('MODIFY', method_id, commit_hash)