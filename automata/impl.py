__all__ = [
    "Automata",
    "FollowAutomata",
    "MarkBeforeAutomata",
    "McNaughtonYamadaAutomata",
    "PositionAutomata",
]

from abc import ABC, abstractmethod
from automata.tree import Node
from collections.abc import Callable, Iterable, Iterator
from dataclasses import dataclass
from itertools import product
from typing import Generic, ParamSpec, TypeVar

T = TypeVar("T")
P = ParamSpec('P')


def method_cache(func: Callable[..., T]) -> Callable[..., T]:
    cache_name = f"_{func.__name__}_cache"

    def wrapper(self: object, *args: P.args) -> T:
        if cache_name not in self.__dict__:
            self.__dict__[cache_name] = {}
        if args not in self.__dict__[cache_name]:
            self.__dict__[cache_name][args] = func(self, *args)
        return self.__dict__[cache_name][args]

    return wrapper


class FromNode(ABC, Generic[T]):
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
    def is_final(self, state: T) -> bool:
        raise NotImplementedError

    @staticmethod
    def states() -> set[T] | None:
        return None


class FromNodeNFA(FromNode[T], ABC):
    @abstractmethod
    def initial(self) -> frozenset[T]:
        raise NotImplementedError

    @abstractmethod
    def transition(self, state: T, symbol: str) -> frozenset[T]:
        raise NotImplementedError

    def nfa(self) -> 'NFA':
        return NFA(
            symbols=self.symbols,
            initial=self.initial,
            is_final=self.is_final,
            transition=self.transition,
            states=self.states(),
        )

    @classmethod
    def minimize(cls, node: Node) -> 'DFA':
        self = cls(node.reverse())
        return self.nfa().subset_determinise().reverse().subset_determinise()


class FromNodeDFA(FromNode[T], ABC):
    @abstractmethod
    def initial(self) -> T:
        raise NotImplementedError

    @abstractmethod
    def transition(self, state: T, symbol: str) -> T:
        raise NotImplementedError

    def dfa(self) -> 'DFA':
        return DFA(
            symbols=self.symbols,
            initial=self.initial,
            is_final=self.is_final,
            transition=self.transition,
            states=self.states(),
        )

    @classmethod
    def minimize(cls, node: Node) -> 'DFA':
        return cls(node.reverse()).dfa().reverse().subset_determinise()


class Automata(ABC, Generic[T]):
    @abstractmethod
    def accepts(self, word: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def all_states(self) -> set[T]:
        raise NotImplementedError

    def count_states(self) -> int:
        return len(self.all_states())


@dataclass
class NFA(Automata[T]):
    symbols: list[str]
    initial: Callable[[], frozenset[T]]
    is_final: Callable[[T], bool]
    transition: Callable[[T, str], frozenset[T]]
    states: set[T] | None = None

    @method_cache
    def all_states(self) -> set[T]:
        if self.states is not None:
            return self.states
        states = set(self.initial())
        to_check = set(self.initial())
        while len(to_check) != 0:
            new_states = set()
            for state, symbol in product(to_check, self.symbols):
                transition_states = self.transition(state, symbol)
                for new in transition_states:
                    if new not in states:
                        new_states.add(new)
            states |= new_states
            to_check = new_states
        return states

    def accepts(self, word: str) -> bool:
        states = self.initial()
        for symbol in word:
            if len(states) == 0:
                return False
            states = {t for s in states for t in self.transition(s, symbol)}
        return any(self.is_final(s) for s in states)

    @method_cache
    def determinised_initial(self) -> frozenset[T]:
        return frozenset(self.initial())

    @method_cache
    def determinised_transition(self, state: frozenset[T], symbol: str) -> frozenset[T]:
        return frozenset(q for s in state for q in self.transition(s, symbol))

    @method_cache
    def determinised_is_final(self, state: frozenset[T]) -> bool:
        return any(self.is_final(s) for s in state)

    def subset_determinise(self) -> 'DFA':
        return DFA(
            symbols=self.symbols,
            initial=self.determinised_initial,
            is_final=self.determinised_is_final,
            transition=self.determinised_transition,
        )


@dataclass
class DFA(Automata[T]):
    symbols: list[str]
    initial: Callable[[], T]
    is_final: Callable[[T], bool]
    transition: Callable[[T, str], T]
    states: set[T] | None = None

    @method_cache
    def all_states(self) -> set[T]:
        if self.states is not None:
            return self.states
        states = {self.initial()}
        to_check = {self.initial()}
        while len(to_check) != 0:
            new_states = set()
            for state, symbol in product(to_check, self.symbols):
                new = self.transition(state, symbol)
                if new not in states and (len(new) != 0 or self.is_final(new)):
                    new_states.add(new)
            states |= new_states
            to_check = new_states
        return states

    def accepts(self, word: str) -> bool:
        state = self.initial()
        for symbol in word:
            if len(state) == 0:
                return False
            state = self.transition(state, symbol)
        return self.is_final(state)

    @method_cache
    def reverse_is_final(self, state: T) -> bool:
        return state == self.initial()

    @method_cache
    def reverse_transition(self, state: T, symbol: str) -> frozenset[T]:
        return frozenset(s for s in self.all_states() if self.transition(s, symbol) == state)

    @method_cache
    def final_set(self) -> frozenset[T]:
        return frozenset(s for s in self.all_states() if self.is_final(s))

    def reverse(self) -> NFA:
        return NFA(
            symbols=self.symbols,
            initial=self.final_set,
            is_final=self.reverse_is_final,
            transition=self.reverse_transition,
            states=self.states,
        )


class PositionAutomata(FromNodeNFA):
    def initial(self) -> frozenset[int]:
        return frozenset([0])

    @method_cache
    def transition(self, state: int, symbol: str) -> frozenset[int]:
        return self.select(self.follow_i(state), symbol)

    def is_final(self, state: int) -> bool:
        return state in self.last_0

    def states(self) -> set[T] | None:
        return set(self.pos)


class McNaughtonYamadaAutomata(FromNodeDFA):
    def initial(self) -> frozenset[int]:
        return frozenset([0])

    @method_cache
    def transition(self, state: frozenset[int], symbol: str) -> frozenset[int]:
        return self.select(self.follow_set(state), symbol)

    def is_final(self, state: frozenset[int]) -> bool:
        return any(s in self.last_0 for s in state)


@dataclass(frozen=True)
class FollowState:
    follow: frozenset[int]
    final: bool

    def __len__(self) -> int:
        return len(self.follow)

    def __iter__(self) -> Iterator[int]:
        return iter(self.follow)


class FollowAutomata(FromNodeNFA):
    @method_cache
    def follow_state(self, idx: int) -> FollowState:
        return FollowState(follow=self.follow_i(idx), final=idx in self.last_0)

    def initial(self) -> frozenset[FollowState]:
        return frozenset([self.follow_state(0)])

    @method_cache
    def transition(self, state: FollowState, symbol: str) -> frozenset[FollowState]:
        return frozenset(self.follow_state(j) for j in self.select(state, symbol))

    def is_final(self, state: FollowState) -> bool:
        return state.final

    @method_cache
    def states(self) -> set[FollowState]:
        return {self.follow_state(i) for i in [0, *self.pos]}


class MarkBeforeAutomata(FromNodeDFA):
    @method_cache
    def set_finality(self, s: frozenset[int]) -> bool:
        return any(i in self.last_0 for i in s)

    def initial(self) -> FollowState:
        return FollowState(follow=frozenset(self.first), final=0 in self.last_0)

    @method_cache
    def transition(self, state: FollowState, symbol: str) -> FollowState:
        select = self.select(state, symbol)
        return FollowState(follow=self.follow_set(select), final=self.set_finality(select))

    def is_final(self, state: FollowState) -> bool:
        return state.final
