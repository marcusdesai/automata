__all__ = ["Automata", "PositionAutomata", "match_re"]

from abc import ABC, abstractmethod
from automata.parser import Parser
from automata.tree import Node
from typing import Self


class Automata(ABC):
    @classmethod
    @abstractmethod
    def from_node(cls, node: Node) -> Self:
        raise NotImplementedError

    @property
    @abstractmethod
    def final(self) -> set[int]:
        raise NotImplementedError

    @property
    @abstractmethod
    def initial(self) -> set[int]:
        raise NotImplementedError

    @abstractmethod
    def transition(self, index: int, symbol: str) -> set[int]:
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

    def transition(self, index: int, symbol: str) -> set[int]:
        if index == 0:
            return self.first
        return {j for i, j in self.follow if i == index and self.pos[j] == symbol}


def match_re(pattern: str, string: str, engine: type[Automata] = PositionAutomata) -> bool:
    node = Parser(pattern).parse()
    auto = engine.from_node(node)
    return auto.accepts(string)
