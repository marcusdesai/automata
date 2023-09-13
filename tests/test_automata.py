import pytest
import random
import re
from automata.impl import *
from automata.parser import Parser
from automata.tree import *
from collections.abc import Iterator

# noinspection DuplicatedCode
ENGINES = {
    "Position": lambda n: PositionAutomata(n).nfa(),
    "PositionDeterminised": lambda n: PositionAutomata(n).nfa().subset_determinise(),
    "PositionMinimized": lambda n: PositionAutomata.minimize(n),
    "McNaughtonYamada": lambda n: McNaughtonYamadaAutomata(n).dfa(),
    "McNaughtonYamadaMinimized": lambda n: McNaughtonYamadaAutomata.minimize(n),
    "Follow": lambda n: FollowAutomata(n).nfa(),
    "FollowDeterminised": lambda n: FollowAutomata(n).nfa().subset_determinise(),
    "FollowMinimized": lambda n: FollowAutomata.minimize(n),
    "MarkBefore": lambda n: MarkBeforeAutomata(n).dfa(),
    "MarkBeforeMinimized": lambda n: MarkBeforeAutomata.minimize(n),
}

REGEX_NON_MATCHES = {
    "a": ["b"],
    "ab": ["a"],
    "a*": ["b", "bbb"],
    "a|b": ["c", "ab"],
    "(a*)*b": ["a", "aa"],
}


def generate_non_matches() -> Iterator[tuple[str, str, str, Automata]]:
    for pattern, matches in REGEX_NON_MATCHES.items():
        node = Parser(pattern).parse()
        for match in matches:
            for name, make_automata in ENGINES.items():
                yield pattern, match, name, make_automata(node)


@pytest.mark.parametrize("pattern, non_match, name, automata", generate_non_matches())
def test_non_matches(pattern: str, non_match: str, name: str, automata: Automata):
    assert not automata.accepts(non_match)


PATTERNS = {
    "a",
    "ab",
    "a*",
    "a|b",
    "(a*)*b",
    "a*b",
    "ba|b",
    "b|ab",
    "b|a|b",
    "b|ab|b",
    "b|a*|b",
    "((ab)c)",
    "(a(bc))",
    "a|(b*c)|a",
    "a(ba)*b|a",
    "a(ba*b)*",
    "a|b*a",
    "a*b*",
    "(ac*)*|b*ac",
    "ae|bf|cg|dh",
    "(a|b)(a*|ba*|b*)*",
}


def generate_matches(amount: int) -> Iterator[tuple[str, str, str, Automata]]:
    for pattern in PATTERNS:
        node = Parser(pattern).parse()
        for match in {make_match(node, 5) for _ in range(amount)}:
            for name, make_automata in ENGINES.items():
                yield pattern, match, name, make_automata(node)


@pytest.mark.parametrize("pattern, match, name, automata", generate_matches(10))
def test_generated_matches(pattern: str, match: str, name: str, automata: Automata):
    # Always check conformance to Python's stdlib regex matching
    assert re.match(pattern, match) is not None
    assert automata.accepts(match)


# Utils and tests for them

def make_match(node: Node, loops: int = 2) -> str:
    match node:
        case Symbol(sym, _):
            return sym
        case Star(node):
            iters = random.randrange(loops)
            return "".join(make_match(node, loops) for _ in range(iters))
        case Concat(left, right):
            return f"{make_match(left, loops)}{make_match(right, loops)}"
        case Alt(left, right):
            if random.randint(1, 2) == 1:
                return make_match(left, loops)
            return make_match(right, loops)


MADE_MATCHES = {
    "a": {"a"},
    "ab": {"ab"},
    "a|b": {"a", "b"},
    "a*": {"a" * i for i in range(3)},
    "a(b|c)d": {"abd", "acd"},
    "a(ba)*b|a": {"a", "ab", "aa", "abab", "abaa", "ababab", "ababaa"},
}


@pytest.mark.parametrize("regex, matches", MADE_MATCHES.items())
def test_make_match(regex: str, matches: set[str]):
    node = Parser(regex).parse()
    # We've probably made enough examples in 100 iterations
    made_matches = {make_match(node, 3) for _ in range(100)}
    assert made_matches.issubset(matches)
