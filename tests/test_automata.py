from automata.automata import *
from automata.parser import Parser


def test_simple():
    auto = PositionAutomata(Parser("(a*)*b").parse())
    assert auto.accepts("b")
    assert auto.accepts("ab")
    assert auto.accepts("aaaaaaaab")
    assert not auto.accepts("aaaaaaaaaaac")
