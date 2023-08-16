from automata.position import *


def test_concat_symbols_follow():
    rea = Concat(Symbol("a", 1), Symbol("b", 2))
    assert rea.follow() == {(1, 2)}


def test_concat_star_left_follow():
    rea = Concat(Star(Symbol("a", 1)), Symbol("b", 2))
    assert rea.follow() == {(1, 2), (1, 1)}


def test_concat_star_right_follow():
    rea = Concat(Symbol("a", 1), Star(Symbol("b", 2)))
    assert rea.follow() == {(1, 2), (2, 2)}


class TestExampleOne:
    regex_ast = Concat(
        Symbol("a", 1),
        Star(
            Concat(
                Symbol("b", 2),
                Concat(
                    Star(Symbol("a", 3)),
                    Symbol("b", 4)
                )
            )
        )
    )

    def test_nullable(self):
        assert self.regex_ast.nullable is False

    def test_first(self):
        assert self.regex_ast.first() == {1}

    def test_last_0(self):
        assert self.regex_ast.last_0() == {1, 4}

    def test_follow(self):
        assert self.regex_ast.follow() == {(1, 2), (2, 3), (2, 4), (3, 3), (3, 4), (4, 2)}

    def test_delta(self):
        assert self.regex_ast.delta_pos(2, "a") == {3}
