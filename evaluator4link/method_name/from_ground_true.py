import re

from evaluator4link.method_name.abs_extractor import AbsMethodNameExtractor


class GroundTruthMethodName(AbsMethodNameExtractor):

    __GT_CLASS_METHOD_NAME_REGEX = r'^(?P<sub_path>[a-z.\d]+)\.' \
                                 r'(?P<class_names>[\w.]+)\.' \
                                 r'(?P<method_signature>(?P<simple_name>\w+)?(?:<.+>)?\(.*\))'
    __GT_SUPER_PACKAGE_NAME_REGEX = r'(?P<super_name>[^,(<>]*\.)'

    def __init__(self, long_name: str):
        match = re.match(self.__GT_CLASS_METHOD_NAME_REGEX, long_name)
        match_names = match.groupdict()
        self.__file_path = match_names['sub_path'].replace('.', '/')
        self.__class_name = match_names['class_names'].replace('.', '::')
        signature_match = re.sub(self.__GT_SUPER_PACKAGE_NAME_REGEX, '', match_names['method_signature'])
        self.__signature = signature_match.replace(' ', '')
        self.__simple_name = match_names['simple_name']

    @property
    def file_path(self) -> str:
        return self.__file_path

    @property
    def class_name(self) -> str:
        return self.__class_name

    @property
    def simple_name(self) -> str:
        return self.__simple_name

    @property
    def signature(self) -> str:
        return self.__signature
