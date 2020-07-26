from typing import Optional, Set

from modification.change_holder.abstract_holder import AbstractHolder
from modification.change_holder.class_holder import ClassHolder


class FileHolder(AbstractHolder):

    def __init__(self):
        self.path_before: Optional[str] = None
        self.path_current: Optional[str] = None
        self.classes: Set[ClassHolder] = set()

    def is_renamed(self) -> bool:
        return (self.path_before is not None) \
               and (self.path_current is not None) \
               and (self.path_before != self.path_current)
