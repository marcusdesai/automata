__all__ = [
    "Automata",
    "DeterministicFollowAutomata",
    "DeterministicPositionAutomata",
    "FollowAutomata",
    "MarkBeforeAutomata",
    "McNaughtonYamadaAutomata",
    "PositionAutomata",
    "automata_match",
]

from abc import ABC, abstractmethod
from automata.parser import Parser
from automata.tree import Node
from collections.abc import Callable, Iterable, Iterator
from dataclasses import dataclass
from itertools import product
from typing import Generic, ParamSpec, TypeVar

T = TypeVar("T")
P = ParamSpec('P')


def method_cache(func: Callable[P, T]) -> Callable[P, T]:
    cache_name = f"_{func.__name__}_cache"

    def wraps(self: object, *args: P.args) -> T:
        if cache_name not in self.__dict__:
            self.__dict__[cache_name] = {}
        if args not in self.__dict__[cache_name]:
            self.__dict__[cache_name][args] = func(self, *args)
        return self.__dict__[cache_name][args]

    return wraps


class Automata(ABC, Generic[T]):
    def __init__(self, node: Node) -> None:
        self.pos = node.pos()
        self.first = node.first()
        self.last_0 = node.last_0()
        self.follow = node.follow()

    @property
    def symbols(self) -> list[str]:
        return list(self.pos.values())

    @method_cache
    def follow_i(self, idx: int) -> frozenset[int]:
        if idx == 0:
            return frozenset(self.first)
        return frozenset(j for i, j in self.follow if i == idx)

    @method_cache
    def follow_set(self, s: Iterable[int]) -> frozenset[int]:
        return frozenset(j for idx in s for j in self.follow_i(idx))

    @method_cache
    def select(self, s: Iterable[int], symbol: str) -> frozenset[int]:
        return frozenset(i for i in s if self.pos[i] == symbol)

    @abstractmethod
    def accepts(self, word: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def count_states(self) -> int:
        raise NotImplementedError


class DFA(Automata[T], ABC):
    @property
    @abstractmethod
    def initial(self) -> T:
        raise NotImplementedError

    @abstractmethod
    def transition(self, state: T, symbol: str) -> T:
        raise NotImplementedError

    @method_cache
    def all_states(self) -> set[T]:
        states = {self.initial}
        to_check = {self.initial}
        while len(to_check) != 0:
            new_states = set()
            for state, symbol in product(to_check, self.symbols):
                new = self.transition(state, symbol)
                if new not in states and len(new) != 0:
                    new_states.add(new)
            states |= new_states
            to_check = new_states
        return states

    def count_states(self) -> int:
        return len(self.all_states())


class PositionAutomata(Automata[int]):
    @method_cache
    def transition(self, state: int, symbol: str) -> frozenset[int]:
        return self.select(self.follow_i(state), symbol)

    def count_states(self) -> int:
        return max(self.pos)

    def accepts(self, word: str) -> bool:
        states = {0}
        for symbol in word:
            if len(states) == 0:
                return False
            states = {t for s in states for t in self.transition(s, symbol)}
        return len(states.intersection(self.last_0)) > 0


class DeterministicPositionAutomata(DFA[frozenset[int]]):
    @property
    def initial(self) -> frozenset[int]:
        return frozenset([0])

    @method_cache
    def transition(self, state: frozenset[int], symbol: str) -> frozenset[int]:
        return frozenset(
            q for s in state for q in PositionAutomata.transition(self, s, symbol)
        )

    def accepts(self, word: str) -> bool:
        state = self.initial
        for symbol in word:
            if len(state) == 0:
                return False
            state = self.transition(state, symbol)
        return any(s in self.last_0 for s in state)


class McNaughtonYamadaAutomata(DFA[frozenset[int]]):
    @property
    def initial(self) -> frozenset[int]:
        return frozenset([0])

    @method_cache
    def transition(self, state: frozenset[int], symbol: str) -> frozenset[int]:
        return self.select(self.follow_set(state), symbol)

    def accepts(self, word: str) -> bool:
        state = self.initial
        for symbol in word:
            if len(state) == 0:
                return False
            state = self.transition(state, symbol)
        return any(i in self.last_0 for i in state)


@dataclass(frozen=True)
class FollowState:
    follow: frozenset[int]
    final: bool

    def __len__(self) -> int:
        return len(self.follow)

    def __iter__(self) -> Iterator[int]:
        return iter(self.follow)


class FollowAutomata(Automata[FollowState]):
    @method_cache
    def follow_state(self, idx: int) -> FollowState:
        return FollowState(follow=self.follow_i(idx), final=idx in self.last_0)

    @method_cache
    def transition(self, state: FollowState, symbol: str) -> set[FollowState]:
        return {self.follow_state(j) for j in self.select(state, symbol)}

    def accepts(self, word: str) -> bool:
        states = {self.follow_state(0)}
        for symbol in word:
            if len(states) == 0:
                return False
            states = {t for s in states for t in self.transition(s, symbol)}
        return any(s.final for s in states)

    @method_cache
    def all_states(self) -> set[FollowState]:
        return {self.follow_state(i) for i in [0, *self.pos]}

    def count_states(self) -> int:
        return len(self.all_states())


class DeterministicFollowAutomata(DFA[frozenset[FollowState]], FollowAutomata):
    @property
    def initial(self) -> frozenset[FollowState]:
        return frozenset([self.follow_state(0)])

    @method_cache
    def transition(self, state: frozenset[FollowState], symbol: str) -> frozenset[FollowState]:
        return frozenset(
            q for s in state for q in FollowAutomata.transition(self, s, symbol)
        )

    def accepts(self, word: str) -> bool:
        state = self.initial
        for symbol in word:
            if len(state) == 0:
                return False
            state = self.transition(state, symbol)
        return any(s.final for s in state)


class MarkBeforeAutomata(DFA[FollowState]):
    @method_cache
    def set_finality(self, s: frozenset[int]) -> bool:
        return any(i in self.last_0 for i in s)

    @property
    def initial(self) -> FollowState:
        return FollowState(follow=frozenset(self.first), final=0 in self.last_0)

    @method_cache
    def transition(self, state: FollowState, symbol: str) -> FollowState:
        select = self.select(state, symbol)
        return FollowState(follow=self.follow_set(select), final=self.set_finality(select))

    def accepts(self, word: str) -> bool:
        state = self.initial
        for symbol in word:
            if len(state) == 0:
                return False
            state = self.transition(state, symbol)
        return state.final


def automata_match(pattern: str, string: str, engine: type[Automata]) -> bool:
    # special case empty pattern, we cannot parse empty strings
    if pattern == "":
        return string == ""
    node = Parser(pattern).parse()
    auto = engine(node)
    return auto.accepts(string)
