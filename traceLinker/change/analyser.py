import os
import subprocess
from typing import Dict, List

from pydriller import Modification

from traceLinker.change import FileChangeIdentifier


class FileChangeAnalyser(object): # Factory Class for the identifier

    def __init__(self, tmp_path: str):
        os.makedirs(tmp_path, exist_ok=True)
        self.__tmp_path = tmp_path

    def analyse(self, file: Modification) -> FileChangeIdentifier:
        if file.new_path == None: # Delete;
        if file.old_path == None: # Add
        if file.new_path == file.old_path: # Modify
        if file.new_path != file.old_path: # Relocate
        methods_before = file.methods_before
        methods_after =

    def is_file_name_changed(self):



