import pytest
import random
import re
from automata.automata import *
from automata.parser import Parser
from automata.tree import *
from collections.abc import Iterator

REGEX_MATCHES = {
    "a": ["a"],
    "ab": ["ab"],
    "a*": ["a", "aaaaaaaaaa"],
    "a|b": ["a", "b"],
    "(a*)*b": ["b", "ab", "aab"],
}


@pytest.mark.parametrize("regex, match", ((r, m) for r, ml in REGEX_MATCHES.items() for m in ml))
def test_regex_matches(regex: str, match: str):
    assert automata_match(regex, match)


REGEX_NON_MATCHES = {
    "a": ["b"],
    "ab": ["a"],
    "a*": ["b", "bbb"],
    "a|b": ["c", "ab"],
    "(a*)*b": ["a", "aa"],
}


@pytest.mark.parametrize("regex, non_match", ((r, m) for r, ml in REGEX_NON_MATCHES.items() for m in ml))
def test_regex_non_matches(regex: str, non_match: str):
    print(automata_match(regex, non_match))
    assert not automata_match(regex, non_match)


def make_match(node: Node, loops: int = 2) -> str:
    match node:
        case Symbol(sym, _):
            return sym
        case Star(node):
            iters = random.randrange(0, loops)
            return "".join(make_match(node, loops) for _ in range(iters))
        case Concat(left, right):
            return f"{make_match(left, loops)}{make_match(right, loops)}"
        case Alt(left, right):
            if random.randrange(2) == 0:
                return make_match(left, loops)
            return make_match(right, loops)


MADE_MATCHES = {
    "a": {"a"},
    "ab": {"ab"},
    "a|b": {"a", "b"},
    "a*": {"a" * i for i in range(3)},
    "a(b|c)d": {"abd", "acd"},
    "a(ba)*b|a": {"ab", "aa", "abab", "abaa", "ababab", "ababaa"},
}


@pytest.mark.parametrize("regex, matches", MADE_MATCHES.items())
def test_make_match(regex: str, matches: set[str]):
    node = Parser(regex).parse()
    # We've probably made enough examples in 100 iterations
    made_matches = {make_match(node, 3) for _ in range(100)}
    print(made_matches)
    assert made_matches.issubset(matches)


PATTERNS = [
    "a*b",
    "ba|b",
    "b|ab",
    "b|a|b",
    "b|a*|b",
    "((ab)c)",
    "(a(bc))",
    "a|(b*c)|a",
    "a(ba)*b|a",
    "a(ba*b)*",
    "a|b*a",
    "a*b*",
]

ENGINES = [PositionAutomata]


def generate_matches(amount: int = 10) -> Iterator[tuple[str, str, type[Automata]]]:
    for pattern in PATTERNS:
        for _ in range(amount):
            match = make_match(Parser(pattern).parse(), 5)
            for engine in ENGINES:
                yield pattern, match, engine


@pytest.mark.parametrize("pattern, match, engine", generate_matches())
def test_generated_matches(pattern: str, match: str, engine: type[Automata]):
    # Always check conformance to Python's stdlib regex matching
    assert re.match(pattern, match) is not None
    assert automata_match(pattern, match, engine=engine)


@pytest.mark.parametrize("engine", ENGINES)
def test_empty_pattern_match(engine: type[Automata]):
    assert automata_match("", "", engine=engine)
