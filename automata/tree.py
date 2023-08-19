__all__ = ["Node", "Symbol", "Star", "Concat", "Alt"]

from abc import ABC, abstractmethod
from dataclasses import dataclass
from itertools import product


@dataclass
class Node(ABC):
    @property
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
        if self.nullable:
            return self.last() | {0}
        return self.last()

    @abstractmethod
    def follow(self) -> set[tuple[int, int]]:
        raise NotImplementedError

    @abstractmethod
    def pos(self) -> dict[int, str]:
        raise NotImplementedError


@dataclass
class Symbol(Node):
    value: str
    index: int

    @property
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


@dataclass
class Star(Node):
    child: Node

    @property
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


@dataclass
class Concat(Node):
    left: Node
    right: Node

    @property
    def nullable(self) -> bool:
        return self.left.nullable and self.right.nullable

    def first(self) -> set[int]:
        if self.left.nullable:
            return self.left.first() | self.right.first()
        return self.left.first()

    def last(self) -> set[int]:
        if self.right.nullable:
            return self.left.last() | self.right.last()
        return self.right.last()

    def follow(self) -> set[tuple[int, int]]:
        joined = set(product(self.left.last(), self.right.first()))
        return joined | self.left.follow() | self.right.follow()

    def pos(self) -> dict[int, str]:
        return self.left.pos() | self.right.pos()


@dataclass
class Alt(Node):
    left: Node
    right: Node

    @property
    def nullable(self) -> bool:
        return self.left.nullable or self.right.nullable

    def first(self) -> set[int]:
        return self.left.first() | self.right.first()

    def last(self) -> set[int]:
        return self.left.last() | self.right.last()

    def follow(self) -> set[tuple[int, int]]:
        return self.left.follow() | self.right.follow()

    def pos(self) -> dict[int, str]:
        return self.left.pos() | self.right.pos()
