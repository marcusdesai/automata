__all__ = ["Parser"]

from automata.tree import Alt, Concat, Node, Star, Symbol
from typing import Final

ERR_MSG: Final[str] = "expected: {} at index: {}, found: {}"


class Parser:
    """
    Implements the following grammar:

    <expr>   ::= <binary> | <binary> <expr>
    <binary> ::= <unary>  | <unary> "|" <binary>
    <unary>  ::= <atom>   | <atom> "*"
    <atom>   ::= <char>   | "(" <expr> ")"

    The entrypoint is Parser.parse. This function must only be called once per
    instance of parser. Multiple calls will result in incorrect results beyond
    the first call.
    """

    def __init__(self, string: str) -> None:
        self.pos = 0
        self.tokens = list(string)
        self.symbol_count = 1
        self.paren_count = 0

    def _inc(self) -> None:
        self.pos += 1

    def _next(self) -> str | None:
        return None if self.pos >= len(self.tokens) else self.tokens[self.pos]

    def _symbol_index(self) -> int:
        """Provides a unique number for a symbol index when called."""
        index = self.symbol_count
        self.symbol_count += 1
        return index

    def _parse_atom(self) -> Node:
        char = self._next()
        self._inc()

        # "(" <expr> ")"
        if char == "(":
            self.paren_count += 1
            expr = self.parse()
            if (char := self._next()) != ")":
                raise SyntaxError(ERR_MSG.format("')'", self.pos, char))
            self.paren_count -= 1
            self._inc()
            return expr

        if char in {")", "|", "*"}:
            raise SyntaxError(ERR_MSG.format("symbol", self.pos, f"'{char}'"))
        if char is None:
            raise SyntaxError(ERR_MSG.format("symbol", self.pos, "empty string"))

        # <char>
        return Symbol(char, self._symbol_index())

    def _parse_unary(self) -> Node:
        atom = self._parse_atom()

        # <atom> "*"
        if self._next() == "*":
            self._inc()
            return Star(atom)

        # <atom>
        return atom

    def _parse_binary(self) -> Node:
        unary = self._parse_unary()

        # <unary> "|" <binary>
        if self._next() == "|":
            self._inc()
            return Alt(unary, self._parse_binary())

        # <unary>
        return unary

    def parse(self) -> Node:
        """
        Parses the string given to the Parser. Multiple calls to this function
        will result in incorrect results beyond the first call.
        """
        binary = self._parse_binary()
        if self._next() == ")" and self.paren_count == 0:
            msg = f"unexpected close paren at index: {self.pos}"
            raise SyntaxError(msg)

        # <binary> <expr>
        if self._next() not in {"|", ")", None}:
            return Concat(binary, self.parse())

        # <binary>
        return binary
