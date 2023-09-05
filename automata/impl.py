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
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from typing import Generic, ParamSpec, Self, TypeVar

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
    @classmethod
    @abstractmethod
    def from_node(cls, node: Node) -> Self:
        raise NotImplementedError

    @abstractmethod
    def accepts(self, word: str) -> bool:
        raise NotImplementedError


class DFA(ABC):
    @property
    @abstractmethod
    def initial(self) -> T:
        raise NotImplementedError

    @property
    @abstractmethod
    def symbols(self) -> list[str]:
        raise NotImplementedError

    @abstractmethod
    def transition(self, state: T, symbol: str) -> T:
        raise NotImplementedError

    @method_cache
    def all_states(self) -> set[T]:
        states = {self.initial}
        to_check = {self.initial}
        while True:
            new_states = set()
            for state in to_check:
                for sym in self.symbols:
                    if (new := self.transition(state, sym)) not in states:
                        if len(new) != 0:
                            new_states.add(new)
            if len(new_states) == 0:
                break
            states |= new_states
            to_check = new_states
        return states

    def count_states(self) -> int:
        return len(self.all_states())


class PositionAutomata(Automata):
    def __init__(self, node: Node) -> None:
        self.pos = node.pos()
        self.first = node.first()
        self.last_0 = node.last_0()
        self.follow = node.follow()

    @classmethod
    def from_node(cls, node: Node) -> Self:
        return cls(node)

    @method_cache
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


class DeterministicPositionAutomata(PositionAutomata, DFA):
    def __init__(self, node: Node) -> None:
        super().__init__(node)

    @property
    def initial(self) -> frozenset[int]:
        return frozenset([0])

    @property
    def symbols(self) -> list[str]:
        return list(self.pos.values())

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


class McNaughtonYamadaAutomata(Automata, DFA):
    def __init__(self, node: Node) -> None:
        self.pos = node.pos()
        self.first = node.first()
        self.last_0 = node.last_0()
        self.follow = node.follow()

    @classmethod
    def from_node(cls, node: Node) -> Self:
        return cls(node)

    @property
    def initial(self) -> frozenset[int]:
        return frozenset([0])

    @property
    def symbols(self) -> list[str]:
        return list(self.pos.values())

    @method_cache
    def follow_i(self, idx: int) -> frozenset[int]:
        if idx == 0:
            return frozenset(self.first)
        return frozenset(j for i, j in self.follow if i == idx)

    @method_cache
    def follow_set(self, s: frozenset[int]) -> frozenset[int]:
        return frozenset(j for idx in s for j in self.follow_i(idx))

    @method_cache
    def transition(self, state: frozenset[int], symbol: str) -> frozenset[int]:
        return frozenset(i for i in self.follow_set(state) if self.pos[i] == symbol)

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


class FollowAutomata(Automata):
    def __init__(self, node: Node) -> None:
        self.pos = node.pos()
        self.first = node.first()
        self.last_0 = node.last_0()
        self.follow = node.follow()

        self.init = FollowState(follow=frozenset(self.first), final=0 in self.last_0)

        self.states = {0: self.init}
        for idx in node.pos():
            f_set = frozenset({j for i, j in self.follow if i == idx})
            self.states[idx] = FollowState(follow=f_set, final=idx in self.last_0)

    @classmethod
    def from_node(cls, node: Node) -> Self:
        return cls(node)

    @method_cache
    def transition(self, state: FollowState, symbol: str) -> set[FollowState]:
        select = {i for i in state if self.pos[i] == symbol}
        return {self.states[j] for j in select}

    def accepts(self, word: str) -> bool:
        states = {self.init}
        for symbol in word:
            if len(states) == 0:
                return False
            states = {t for s in states for t in self.transition(s, symbol)}
        return any(s.final for s in states)

    def count_states(self) -> int:
        return len(set(self.states.values()))


class DeterministicFollowAutomata(FollowAutomata, DFA):
    def __init__(self, node: Node) -> None:
        super().__init__(node)

    @property
    def initial(self) -> frozenset[FollowState]:
        return frozenset([self.init])

    @property
    def symbols(self) -> list[str]:
        return list(self.pos.values())

    @method_cache
    def transition(self, state: frozenset[FollowState], symbol: str) -> frozenset[FollowState]:
        return frozenset(
            q for s in state for q in FollowAutomata.transition(self, s, symbol)
        )

    def accepts(self, word: str) -> bool:
        state = frozenset([self.init])
        for symbol in word:
            if len(state) == 0:
                return False
            state = self.transition(state, symbol)
        return any(s.final for s in state)


class MarkBeforeAutomata(Automata, DFA):
    def __init__(self, node: Node) -> None:
        self.pos = node.pos()
        self.first = frozenset(node.first())
        self.last_0 = node.last_0()
        self.follow = node.follow()

    @classmethod
    def from_node(cls, node: Node) -> Self:
        return cls(node)

    @method_cache
    def follow_i(self, idx: int) -> frozenset[int]:
        # weird that mark before doesn't seem to need the 0 follow set...
        if idx == 0:
            return self.first
        return frozenset(j for i, j in self.follow if i == idx)

    @method_cache
    def follow_set(self, s: frozenset[int]) -> frozenset[int]:
        return frozenset(j for idx in s for j in self.follow_i(idx))

    @method_cache
    def set_finality(self, s: frozenset[int]) -> bool:
        return any(i in self.last_0 for i in s)

    @property
    def initial(self) -> FollowState:
        return FollowState(follow=self.first, final=0 in self.last_0)

    @property
    def symbols(self) -> list[str]:
        return list(self.pos.values())

    @method_cache
    def transition(self, state: FollowState, symbol: str) -> FollowState:
        select = frozenset(i for i in state if self.pos[i] == symbol)
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
    auto = engine.from_node(node)
    return auto.accepts(string)
