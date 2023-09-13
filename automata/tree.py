__all__ = ["Node", "Symbol", "Star", "Concat", "Alt"]

from abc import ABC, abstractmethod
from dataclasses import dataclass
from itertools import product
from typing import Self


@dataclass(frozen=True)
class Node(ABC):
    @abstractmethod
    def nullable(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def first(self) -> set[int]:
        raise NotImplementedError

    @abstractmethod
    def last(self) -> set[int]:
        raise NotImplementedError

    def last_0(self) -> set[int]:
        if self.nullable():
            return self.last() | {0}
        return self.last()

    @abstractmethod
    def follow(self) -> set[tuple[int, int]]:
        raise NotImplementedError

    @abstractmethod
    def pos(self) -> dict[int, str]:
        raise NotImplementedError

    @abstractmethod
    def reverse(self) -> Self:
        raise NotImplementedError


@dataclass(frozen=True)
class Symbol(Node):
    value: str
    index: int

    def nullable(self) -> bool:
        return False

    def first(self) -> set[int]:
        return {self.index}

    def last(self) -> set[int]:
        return {self.index}

    def follow(self) -> set[tuple[int, int]]:
        return set()

    def pos(self) -> dict[int, str]:
        return {self.index: self.value}

    def reverse(self) -> Self:
        return self


@dataclass(frozen=True)
class Star(Node):
    child: Node

    def nullable(self) -> bool:
        return True

    def first(self) -> set[int]:
        return self.child.first()

    def last(self) -> set[int]:
        return self.child.last()

    def follow(self) -> set[tuple[int, int]]:
        joined = set(product(self.last(), self.first()))
        return joined | self.child.follow()

    def pos(self) -> dict[int, str]:
        return self.child.pos()

    def reverse(self) -> Self:
        return Star(self.child.reverse())


@dataclass(frozen=True)
class Concat(Node):
    left: Node
    right: Node

    def nullable(self) -> bool:
        return self.left.nullable() and self.right.nullable()

    def first(self) -> set[int]:
        if self.left.nullable():
            return self.left.first() | self.right.first()
        return self.left.first()

    def last(self) -> set[int]:
        if self.right.nullable():
            return self.left.last() | self.right.last()
        return self.right.last()

    def follow(self) -> set[tuple[int, int]]:
        joined = set(product(self.left.last(), self.right.first()))
        return joined | self.left.follow() | self.right.follow()

    def pos(self) -> dict[int, str]:
        return self.left.pos() | self.right.pos()

    def reverse(self) -> Self:
        return Concat(self.right.reverse(), self.left.reverse())


@dataclass(frozen=True)
class Alt(Node):
    left: Node
    right: Node

    def nullable(self) -> bool:
        return self.left.nullable() or self.right.nullable()

    def first(self) -> set[int]:
        return self.left.first() | self.right.first()

    def last(self) -> set[int]:
        return self.left.last() | self.right.last()

    def follow(self) -> set[tuple[int, int]]:
        return self.left.follow() | self.right.follow()

    def pos(self) -> dict[int, str]:
        return self.left.pos() | self.right.pos()

    def reverse(self) -> Self:
        return Alt(self.right.reverse(), self.left.reverse())
