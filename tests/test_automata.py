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
    assert match_re(regex, match)


def make_match(node: Node) -> str:
    match node:
        case Symbol(sym, _):
            return sym
        case Star(node):
            return ''.join(make_match(node) for _ in range(random.randrange(10)))
        case Concat(left, right):
            return f"{make_match(left)}{make_match(right)}"
        case Alt(left, right):
            if random.randrange(2) == 0:
                return make_match(left)
            return make_match(right)


MATCHES = {
    "a": {"a"},
    "ab": {"ab"},
    "a|b": {"a", "b"},
    "a*": {"a" * i for i in range(50)},
    "a(b|c)d": {"abd", "acd"},
}


@pytest.mark.parametrize("regex, matches", MATCHES.items())
def test_make_match(regex: str, matches: set[str]):
    node = Parser(regex).parse()
    made_matches = {make_match(node) for _ in range(10)}
    assert made_matches.issubset(matches)


REGEXES = [
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

AUTOMATED_MATCHES = (
    (r, m) for r in REGEXES
    for m in (make_match(Parser(r).parse()) for _ in range(10))
)


@pytest.mark.parametrize("regex, match", AUTOMATED_MATCHES)
def test_regex_matches_constructed(regex: str, match: str):
    assert re.match(regex, match) is not None
    assert match_re(regex, match)
