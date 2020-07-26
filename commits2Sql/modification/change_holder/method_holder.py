from typing import Optional, List

from pydriller.domain.commit import Method

from modification.change_holder.abstract_holder import AbstractHolder


class MethodHolder(AbstractHolder):

    def __init__(self):
        self.method_before: Optional[Method] = None
        self.method_current: Optional[Method] = None

    def is_new(self) -> bool:
        return (self.method_before is None) and (self.method_current is not None)

    def is_deleted(self) -> bool:
        return (self.method_before is not None) and (self.method_current is None)

    def is_renamed(self) -> bool:
        return (self.method_before is not None) and (self.method_current is not None) \
               and (self.method_before.long_name != self.method_current.long_name)

    def is_modified(self) -> bool:
        return (self.method_before is not None) and (self.method_current is not None) \
               and (self.method_before.long_name == self.method_current.long_name)

    def is_changed(self) -> bool:
        return (self.method_before is None) or (self.method_current is None) \
               or (self.method_before.long_name != self.method_current.long_name)


