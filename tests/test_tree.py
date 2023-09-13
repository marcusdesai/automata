import pytest
from automata.tree import *

TREES = {
    # ab
    Concat(Symbol("a", 1), Symbol("b", 2)): {
        "nullable": False,
        "first": {1},
        "last_0": {2},
        "follow": {(1, 2)},
        "pos": {1: "a", 2: "b"},
        "reverse": Concat(Symbol("b", 2), Symbol("a", 1)),
    },

    # a*b
    Concat(Star(Symbol("a", 1)), Symbol("b", 2)): {
        "nullable": False,
        "first": {1, 2},
        "last_0": {2},
        "follow": {(1, 1), (1, 2)},
        "pos": {1: "a", 2: "b"},
        "reverse": Concat(Symbol("b", 2), Star(Symbol("a", 1))),
    },

    # ab*
    Concat(Symbol("a", 1), Star(Symbol("b", 2))): {
        "nullable": False,
        "first": {1},
        "last_0": {1, 2},
        "follow": {(1, 2), (2, 2)},
        "pos": {1: "a", 2: "b"},
        "reverse": Concat(Star(Symbol("b", 2)), Symbol("a", 1)),
    },

    # a|b
    Alt(Symbol("a", 1), Symbol("b", 2)): {
        "nullable": False,
        "first": {1, 2},
        "last_0": {1, 2},
        "follow": set(),
        "pos": {1: "a", 2: "b"},
        "reverse": Alt(Symbol("b", 2), Symbol("a", 1)),
    },

    # a(ba*b)*
    Concat(
        Symbol("a", 1),
        Star(Concat(Symbol("b", 2), Concat(Star(Symbol("a", 3)), Symbol("b", 4))))
    ): {
        "nullable": False,
        "first": {1},
        "last_0": {1, 4},
        "follow": {
            (1, 2), (2, 3), (2, 4), (3, 3), (3, 4), (4, 2)
        },
        "pos": {1: "a", 2: "b", 3: "a", 4: "b"},
        "reverse": Concat(
            Star(Concat(Concat(Symbol("b", 4), Star(Symbol("a", 3))), Symbol("b", 2))),
            Symbol("a", 1)
        ),
    },

    # a|b*a
    Concat(Alt(Symbol("a", 1), Star(Symbol("b", 2))), Symbol("a", 3)): {
        "nullable": False,
        "first": {1, 2, 3},
        "last_0": {3},
        "follow": {(1, 3), (2, 2), (2, 3)},
        "pos": {1: "a", 2: "b", 3: "a"},
        "reverse": Concat(Symbol("a", 3), Alt(Star(Symbol("b", 2)), Symbol("a", 1))),
    },

    # a*b*
    Concat(Star(Symbol("a", 1)), Star(Symbol("b", 2))): {
        "nullable": True,
        "first": {1, 2},
        "last_0": {0, 1, 2},
        "follow": {(1, 1), (1, 2), (2, 2)},
        "pos": {1: "a", 2: "b"},
        "reverse": Concat(Star(Symbol("b", 2)), Star(Symbol("a", 1))),
    },
}


class Tests:
    @pytest.mark.parametrize("node, nullable", ((n, d["nullable"]) for n, d in TREES.items()))
    def test_nullable(self, node: Node, nullable: bool):
        assert node.nullable() is nullable

    @pytest.mark.parametrize("node, first", ((n, d["first"]) for n, d in TREES.items()))
    def test_first(self, node: Node, first: set[int]):
        assert node.first() == first

    @pytest.mark.parametrize("node, last_0", ((n, d["last_0"]) for n, d in TREES.items()))
    def test_last_0(self, node: Node, last_0: set[int]):
        assert node.last_0() == last_0

    @pytest.mark.parametrize("node, follow", ((n, d["follow"]) for n, d in TREES.items()))
    def test_follow(self, node: Node, follow: set[tuple[int, int]]):
        assert node.follow() == follow

    @pytest.mark.parametrize("node, pos", ((n, d["pos"]) for n, d in TREES.items()))
    def test_pos(self, node: Node, pos: dict[int, str]):
        assert node.pos() == pos

    @pytest.mark.parametrize("node, reverse", ((n, d["reverse"]) for n, d in TREES.items()))
    def test_reverse(self, node: Node, reverse: Node):
        assert node.reverse() == reverse
