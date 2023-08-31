__all__ = [
    "Automata",
    "FollowAutomata",
    "MarkBeforeAutomata",
    "PositionAutomata",
    "automata_match",
]

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

    @abstractmethod
    def accepts(self, word: str) -> bool:
        raise NotImplementedError


class PositionAutomata(Automata):
    def __init__(self, node: Node) -> None:
        self.pos = node.pos()
        self.first = node.first()
        self.last_0 = node.last_0()
        self.follow = node.follow()

    @classmethod
    def from_node(cls, node: Node) -> Self:
        return cls(node)

    def transition(self, state: int, symbol: str) -> set[int]:
        if state == 0:
            follow_i = self.first
        else:
            follow_i = {j for i, j in self.follow if i == state}
        return {j for j in follow_i if self.pos[j] == symbol}

    def accepts(self, word: str) -> bool:
        states = {0}
        for symbol in word:
            if len(states) == 0:
                return False
            states = {t for s in states for t in self.transition(s, symbol)}
        return len(states.intersection(self.last_0)) > 0


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

    def transition(self, state: FollowState, symbol: str) -> set[FollowState]:
        select = {i for i in state[0] if self.pos[i] == symbol}
        return {self.states[j] for j in select}

    def accepts(self, word: str) -> bool:
        states = {self.init}
        for symbol in word:
            if len(states) == 0:
                return False
            states = {t for s in states for t in self.transition(s, symbol)}
        return len(states.intersection(self.final_set)) > 0


MBState: TypeAlias = tuple[set[int], bool]


class MarkBeforeAutomata(Automata):
    def __init__(self, node: Node) -> None:
        self.pos = node.pos()
        self.first = node.first()
        self.last_0 = node.last_0()
        self.follow = node.follow()

    @classmethod
    def from_node(cls, node: Node) -> Self:
        return cls(node)

    def follow_i(self, idx: int) -> set[int]:
        return {j for i, j in self.follow if i == idx}

    def follow_set(self, s: set[int]) -> set[int]:
        return {j for idx in s for j in self.follow_i(idx)}

    def set_finality(self, s: set[int]) -> bool:
        return any(i in self.last_0 for i in s)

    def transition(self, state: MBState, symbol: str) -> MBState:
        select = {i for i in state[0] if self.pos[i] == symbol}
        return self.follow_set(select), self.set_finality(select)

    def accepts(self, word: str) -> bool:
        follow_set, final = self.first, 0 in self.last_0
        for symbol in word:
            if len(follow_set) == 0:
                return False
            follow_set, final = self.transition((follow_set, final), symbol)
        return final


def automata_match(pattern: str, string: str, engine: type[Automata]) -> bool:
    # special case empty pattern, we cannot parse empty strings
    if pattern == "":
        return string == ""
    node = Parser(pattern).parse()
    auto = engine.from_node(node)
    return auto.accepts(string)
