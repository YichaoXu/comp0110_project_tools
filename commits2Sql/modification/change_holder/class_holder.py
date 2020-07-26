from typing import Optional, Set

from modification.change_holder.abstract_holder import AbstractHolder
from modification.change_holder.method_holder import MethodHolder


class ClassHolder(AbstractHolder):

    def __init__(self):
        self.name_before: Optional[str] = None
        self.name_current: Optional[str] = None
        self.methods: Set[MethodHolder] = set()

    def is_new(self) -> bool:
        return (self.name_before is None) and (self.name_current is not None)

    def is_deleted(self) -> bool:
        return (self.name_before is not None) and (self.name_current is None)

    def is_renamed(self) -> bool:
        return (self.name_before is not None) and (self.name_current is not None) \
               and (self.name_before != self.name_current)

    def is_modified(self) -> bool:
        for method in self.methods:
            if method.is_changed(): return True
        return False
