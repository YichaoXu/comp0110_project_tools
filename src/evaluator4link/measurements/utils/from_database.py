import re
from evaluator4link.measurements.utils import AbsMethodNameExtractor


class DatabaseMethodName(AbsMethodNameExtractor):

    __FINAL_KEYWORDS_SUB_REGEX = (
        r'final\s', ''
    )
    __INHERITANCE_KEYWORDS_SUB_REGEX = (
        r'(extends|implements)\s\w+', ''
    )
    __VAR_LENGTH_PARAMETER_SUB_REGEX = (
        r'(\.{3})', '[]'
    )
    __PARAMETER_NAMES_SUB_REGEX = (
        r'(\s+[a-z]\S+\s*)(,|\))', '\\2'
    )
    __SIMPLE_NAME_MATCH_REGEX = r'(?P<name>\w+(<.+>)?)\('

    def __init__(self, long_name):
        signature = re.sub(self.__FINAL_KEYWORDS_SUB_REGEX[0], self.__FINAL_KEYWORDS_SUB_REGEX[1], long_name)
        signature = re.sub(self.__INHERITANCE_KEYWORDS_SUB_REGEX[0], self.__INHERITANCE_KEYWORDS_SUB_REGEX[1],signature)
        signature = re.sub(self.__PARAMETER_NAMES_SUB_REGEX[0], self.__PARAMETER_NAMES_SUB_REGEX[1],signature)
        signature = re.sub(self.__VAR_LENGTH_PARAMETER_SUB_REGEX[0], self.__VAR_LENGTH_PARAMETER_SUB_REGEX[1],signature)
        signature = signature.replace(' ', '')
        self.__signature = signature
        self.__simple_name = re.match(self.__SIMPLE_NAME_MATCH_REGEX, signature).group('name')

    @property
    def simple_name(self) -> str:
        return self.__simple_name

    @property
    def signature(self) -> str:
        return self.__signature
