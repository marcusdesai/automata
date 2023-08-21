import pytest
import random
import re
from automata.automata import *
from automata.parser import Parser
from automata.tree import *

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


def make_match(node: Node) -> str:
    match node:
        case Symbol(sym, _):
            return sym
        case Star(node):
            return "".join(make_match(node) for _ in range(random.randrange(10)))
        case Concat(left, right):
            return f"{make_match(left)}{make_match(right)}"
        case Alt(left, right):
            if random.randrange(2) == 0:
                return make_match(left)
            return make_match(right)


MADE_MATCHES = {
    "a": {"a"},
    "ab": {"ab"},
    "a|b": {"a", "b"},
    "a*": {"a" * i for i in range(10)},
    "a(b|c)d": {"abd", "acd"},
    "a(ba)*b|a": {"ab", "aa", "abab", "ababab", "abaa"},
}


@pytest.mark.parametrize("regex, matches", MADE_MATCHES.items())
def test_make_match(regex: str, matches: set[str]):
    node = Parser(regex).parse()
    # We've probably made enough examples in 100 iterations
    made_matches = {make_match(node) for _ in range(100)}
    assert matches.issubset(made_matches)


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

GENERATED_MATCHES = [
    (pattern, match) for pattern in PATTERNS
    for match in (make_match(Parser(pattern).parse()) for _ in range(10))
]

ENGINES = [PositionAutomata]

CHECKS = ((pat, match, eng) for pat, match in GENERATED_MATCHES for eng in ENGINES)


@pytest.mark.parametrize("pattern, match, engine", CHECKS)
def test_generated_matches(pattern: str, match: str, engine: type[Automata]):
    # Always check conformance to Python's stdlib regex matching
    assert re.match(pattern, match) is not None
    assert automata_match(pattern, match, engine=engine)
