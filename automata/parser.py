from automata.tree import Alt, Concat, Node, Star, Symbol
from typing import Final

ERR_MSG: Final[str] = "expected: {} at index: {}, found: '{}'"


class Parser:
    def __init__(self, string: str) -> None:
        self.pos = 0
        self.tokens = list(string)
        self.symbol_count = 1

    def inc(self) -> None:
        self.pos += 1

    def next(self) -> str | None:
        return None if self.pos >= len(self.tokens) else self.tokens[self.pos]

    def symbol_index(self) -> int:
        index = self.symbol_count
        self.symbol_count += 1
        return index

    def parse(self) -> Node:
        if self.next() == "(":
            self.inc()
            left = self.parse()
            if (char := self.next()) != ")":
                raise SyntaxError(ERR_MSG.format("')'", self.pos, char))
            self.inc()
        else:
            if (sym := self.next()) in {")", "|", "*"}:
                raise SyntaxError(ERR_MSG.format("symbol", self.pos, sym))
            self.inc()
            left = Symbol(sym, self.symbol_index())
        if self.next() == "*":
            self.inc()
            left = Star(left)
        if self.next() not in {"|", ")", None}:
            left = Concat(left, self.parse())
        if self.next() == "|":
            self.inc()
            left = Alt(left, self.parse())
        return left


if __name__ == "__main__":
    zz = Parser("a(ba)*b|a")
    e = zz.parse()
    print(e)

    result = Concat(
        Symbol("a", 1),
        Concat(
            Star(Concat(Symbol("b", 2), Symbol("a", 3))),
            Alt(Symbol("b", 4), Symbol("a", 5))
        )
    )
    print(result == e)
