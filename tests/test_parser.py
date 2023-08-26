import pytest
from automata.parser import *
from automata.tree import *

PARSE_SUCCEEDS = {
    "a": Symbol("a", 1),
    "(a)": Symbol("a", 1),
    "((a))": Symbol("a", 1),
    "ab": Concat(Symbol("a", 1), Symbol("b", 2)),
    "a*": Star(Symbol("a", 1)),
    "a|b": Alt(Symbol("a", 1), Symbol("b", 2)),
    "aa": Concat(Symbol("a", 1), Symbol("a", 2)),
    "a*b": Concat(Star(Symbol("a", 1)), Symbol("b", 2)),
    "ba|b": Alt(Concat(Symbol("b", 1), Symbol("a", 2)), Symbol("b", 3)),
    "b|ab": Alt(Symbol("b", 1), Concat(Symbol("a", 2), Symbol("b", 3))),
    "b|a|b": Alt(Symbol("b", 1), Alt(Symbol("a", 2), Symbol("b", 3))),
    "b|a*|b": Alt(Symbol("b", 1), Alt(Star(Symbol("a", 2)), Symbol("b", 3))),

    "((ab)c)": Concat(Concat(Symbol("a", 1), Symbol("b", 2)), Symbol("c", 3)),
    "(a(bc))": Concat(Symbol("a", 1), Concat(Symbol("b", 2), Symbol("c", 3))),

    "a|(b*c)|a": Alt(
        Symbol("a", 1),
        Alt(Concat(Star(Symbol("b", 2)), Symbol("c", 3)), Symbol("a", 4))
    ),

    "a(ba)*b|a": Alt(
        Concat(
            Symbol("a", 1),
            Concat(
                Star(Concat(Symbol("b", 2), Symbol("a", 3))),
                Symbol("b", 4))),
        Symbol("a", 5)
    ),

    "a(ba*b)*": Concat(
        Symbol("a", 1),
        Star(Concat(
            Symbol("b", 2),
            Concat(
                Star(Symbol("a", 3)),
                Symbol("b", 4)
            )
        ))
    ),

    "a|b*a": Alt(
        Symbol("a", 1),
        Concat(Star(Symbol("b", 2)), Symbol("a", 3)),
    ),

    "a*b*": Concat(Star(Symbol("a", 1)), Star(Symbol("b", 2))),

    "ae|bf|cg|dh": Alt(
        Concat(Symbol("a", 1), Symbol("e", 2)),
        Alt(
            Concat(Symbol("b", 3), Symbol("f", 4)),
            Alt(
                Concat(Symbol("c", 5), Symbol("g", 6)),
                Concat(Symbol("d", 7), Symbol("h", 8))
            )
        )
    ),
}


@pytest.mark.parametrize("string, result", PARSE_SUCCEEDS.items())
def test_parse_success(string: str, result: Node):
    assert Parser(string).parse() == result


PARSE_FAILS = [
    "",
    "(",
    ")",
    "*",
    "|",
    "*a",
    "|a",
    "()",
    "a|)",
    "a)",
    "(a|",
    "(a",
    "a|*",
    "a(bc)*)*",
    "a||b",
    "a**",
    "a|()",
    "(((a))))",
    "((((a)))",
]


@pytest.mark.parametrize("string", PARSE_FAILS)
def test_parse_fail(string: str):
    with pytest.raises(SyntaxError):
        Parser(string).parse()


def test_parse_cache():
    pattern = "a*b|c(aa)*d|a|z"
    parser = Parser(pattern)
    assert parser.parse() is parser.parse()
