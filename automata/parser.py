__all__ = ["Parser"]

from automata.tree import Alt, Concat, Node, Star, Symbol
from typing import Final

ERR_MSG: Final[str] = "expected: {} at index: {}, found: {}"


class Parser:
    def __init__(self, string: str) -> None:
        self.pos = 0
        self.tokens = list(string)
        self.symbol_count = 1
        self.paren_count = 0

    def inc(self) -> None:
        self.pos += 1

    def next(self) -> str | None:
        return None if self.pos >= len(self.tokens) else self.tokens[self.pos]

    def symbol_index(self) -> int:
        index = self.symbol_count
        self.symbol_count += 1
        return index

    def parse_atom(self) -> Node:
        if self.next() == "(":
            self.paren_count += 1
            self.inc()
            expr = self.parse()
            if (char := self.next()) != ")":
                raise SyntaxError(ERR_MSG.format("')'", self.pos, char))
            self.paren_count -= 1
            self.inc()
            return expr

        if (sym := self.next()) in {")", "|", "*"}:
            raise SyntaxError(ERR_MSG.format("symbol", self.pos, f"'{sym}'"))
        if sym is None:
            raise SyntaxError(ERR_MSG.format("symbol", self.pos, "empty string"))
        self.inc()
        return Symbol(sym, self.symbol_index())

    def parse_unary(self) -> Node:
        atom = self.parse_atom()
        if self.next() == "*":
            self.inc()
            return Star(atom)
        return atom

    def parse_binary(self) -> Node:
        left = self.parse_unary()
        if self.next() == "|":
            self.inc()
            return Alt(left, self.parse_binary())
        return left

    def parse(self) -> Node:
        left = self.parse_binary()
        if self.next() == ")" and self.paren_count == 0:
            msg = f"unexpected close paren at index: {self.pos}"
            raise SyntaxError(msg)
        if self.next() not in {"|", ")", None}:
            return Concat(left, self.parse())
        return left
