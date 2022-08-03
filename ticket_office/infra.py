from functools import total_ordering
from typing import Any, Generic, TypeVar

from typing_extensions import Protocol

# Note the following two classes are mostly here to please mypy
#
# The complexity lies because we want value objects to be comparable, hashable
# (to put them in dicts) and sortable, so we need : a mypy Protocal (Comparable)
# and a generic type var: ValueObject
#
# But hey!, it warks
C = TypeVar("C")


class Comparable(Protocol):
    def __eq__(self, other: Any) -> bool:
        pass

    def __lt__(self: C, other: C) -> bool:
        pass

    def __gt__(self: C, other: C) -> bool:
        pass

    def __le__(self: C, other: C) -> bool:
        pass

    def __ge__(self: C, other: C) -> bool:
        pass


T = TypeVar("T", bound=Comparable)


@total_ordering
class ValueObject(Generic[T]):
    def __init__(self, value: T):
        self._value = value

    def __eq__(self, o: Any) -> bool:
        if not isinstance(o, self.__class__):
            return False
        return self._value == o._value

    def __lt__(self, o: "ValueObject[T]") -> bool:
        return self._value < o._value

    def __str__(self) -> str:
        return str(self._value)

    def __repr__(self) -> str:
        class_name = self.__class__.__name__
        return f"{class_name}({self})"

    def __hash__(self) -> int:
        return hash(self._value)
