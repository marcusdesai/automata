__all__ = ["Automata", "PositionAutomata"]

from abc import ABC, abstractmethod
from automata.tree import Node


class Automata(ABC):
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
    def __init__(self, regex: Node) -> None:
        self.pos = regex.pos()
        self.first = regex.first()
        self.last_0 = regex.last_0()
        self.follow = regex.follow()

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
