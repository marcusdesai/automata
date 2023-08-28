__all__ = ["Automata", "FollowAutomata", "PositionAutomata", "automata_match"]

from abc import ABC, abstractmethod
from automata.parser import Parser
from automata.tree import Node
from typing import Generic, Self, TypeAlias, TypeVar

T = TypeVar("T")


class Automata(ABC, Generic[T]):
    @classmethod
    @abstractmethod
    def from_node(cls, node: Node) -> Self:
        raise NotImplementedError

    @property
    @abstractmethod
    def final(self) -> set[T]:
        raise NotImplementedError

    @property
    @abstractmethod
    def initial(self) -> set[T]:
        raise NotImplementedError

    @abstractmethod
    def transition(self, state: T, symbol: str) -> set[T]:
        raise NotImplementedError

    def accepts(self, word: str) -> bool:
        states = self.initial
        for symbol in word:
            if len(states) == 0:
                return False
            states = {t for s in states for t in self.transition(s, symbol)}
        return len(states.intersection(self.final)) > 0


class PositionAutomata(Automata):
    def __init__(self, node: Node) -> None:
        self.pos = node.pos()
        self.first = node.first()
        self.last_0 = node.last_0()
        self.follow = node.follow()

    @classmethod
    def from_node(cls, node: Node) -> Self:
        return cls(node)

    @property
    def initial(self) -> set[int]:
        return {0}

    @property
    def final(self) -> set[int]:
        return self.last_0

    def transition(self, state: int, symbol: str) -> set[int]:
        if state == 0:
            follow_i = self.first
        else:
            follow_i = {j for i, j in self.follow if i == state}
        return {j for j in follow_i if self.pos[j] == symbol}


FollowState: TypeAlias = tuple[frozenset[int], bool]


class FollowAutomata(Automata):
    def __init__(self, node: Node) -> None:
        self.pos = node.pos()
        self.first = node.first()
        self.last_0 = node.last_0()
        self.follow = node.follow()

        self.init = (frozenset(self.first), 0 in self.last_0)

        self.states = {0: self.init}
        for idx in node.pos():
            f_set = frozenset({j for i, j in self.follow if i == idx})
            self.states[idx] = (f_set, idx in self.last_0)

        self.final_set = {(s, fin) for s, fin in self.states.values() if fin}

    @classmethod
    def from_node(cls, node: Node) -> Self:
        return cls(node)

    @property
    def final(self) -> set[FollowState]:
        return self.final_set

    @property
    def initial(self) -> set[FollowState]:
        return {self.init}

    def transition(self, state: FollowState, symbol: str) -> set[FollowState]:
        select = {i for i in state[0] if self.pos[i] == symbol}
        return {self.states[j] for j in select}


def automata_match(pattern: str, string: str, engine: type[Automata]) -> bool:
    # special case empty pattern, we cannot parse empty strings
    if pattern == "":
        return string == ""
    node = Parser(pattern).parse()
    auto = engine.from_node(node)
    return auto.accepts(string)
