from typing import Dict, List, Tuple
from evaluator4link.measurements import AbstractMeasurement
from evaluator4link.measurements.utils import DatabaseMethodName


class CommitsDataMeasurement(AbstractMeasurement):
    __SELECT_ALL_CHANGED_COMMITS_OF_METHOD_SQL_STMT = '''
        SELECT simple_name, class_name, file_path, change_type, commit_hash FROM (
            changes INNER JOIN methods
            ON changes.target_method_id = methods.id
        )
    '''

    @property
    def package_name_x_table(self) -> Dict[str, int]:
        return self.__method_package_x_table

    @property
    def commit_hash_y_table(self) -> Dict[str, int]:
        return self.__commit_hash_y_table

    @property
    def change_type_z_table(self) -> Dict[str, int]:
        return self.__change_type_z_table

    @property
    def coordinates_for_test(self) -> List[Tuple[int, int, int]]:
        return self.__coordinates_for_test

    @property
    def coordinates_for_tested(self) -> List[Tuple[int, int, int]]:
        return self.__coordinates_for_tested


    def __init__(self, path_to_db: str):
        # Method_X, COMMIT_Y, ChangeType, FilePath
        self.__commit_hash_y_table: Dict[str, int] = dict()
        self.__method_package_x_table: Dict[str, int] = dict()
        self.__change_type_z_table: Dict[str, int] = {'ADD': 1, 'MODIFY': 2, 'RENAME': 3}
        self.__coordinates_for_test: List[Tuple[int, int, int]] = list()
        self.__coordinates_for_tested: List[Tuple[int, int, int]] = list()
        super().__init__(path_to_db)

    def _measure(self) -> None:
        exec_res = self._predict_database.cursor().execute(self.__SELECT_ALL_CHANGED_COMMITS_OF_METHOD_SQL_STMT)
        for signature, class_name, file_path, change_type, hash_value in exec_res:
            package_name = DatabaseMethodName(file_path, class_name, signature).package_name_with_signature
            x_val = self.__from_method_package_signature_to_x(package_name)
            y_val = self.__from_hash_to_y(hash_value)
            z_val = self.__from_hash_to_y(change_type)
            coordinates = self.__coordinates_for_test if self.__is_test(file_path) else self.__coordinates_for_tested
            coordinates.append((x_val, y_val, z_val))
        return None

    def __from_hash_to_y(self, hash: str) -> int:
        if hash not in self.__commit_hash_y_table:
            self.__commit_hash_y_table[hash] = len(self.__commit_hash_y_table) + 1
        return self.__commit_hash_y_table[hash]

    def __from_method_package_signature_to_x(self, package_name: str) -> int:
        if package_name not in self.__method_package_x_table:
            self.__method_package_x_table[package_name] = len(self.__method_package_x_table) + 1
        return self.__method_package_x_table[package_name]

    def __from_change_type_to_z(self, change_type: str) -> int:
        return self.__change_type_z_table[change_type]

    def __is_test(self, file_path: str) -> bool:
        return file_path.startswith('src/test/java/org/apache/commons/lang3')