__all__ = ["Parser"]

from automata.tree import Alt, Concat, Node, Star, Symbol
from typing import Final

ERR_MSG: Final[str] = "expected: {} at index: {}, found: {}"


class Parser:
    """
    Implements the following grammar:

    <alt>    ::= <concat> | <concat> "|" <alt>
    <concat> ::= <star>   | <star> <concat>
    <star>   ::= <atom>   | <atom> "*"
    <atom>   ::= <char>   | "(" <alt> ")"
    """

    def __init__(self, string: str) -> None:
        self._pos = 0
        self._tokens = list(string)
        self._symbol_count = 1
        self._paren_count = 0
        self._parsed: Node | None = None

    def _inc(self) -> None:
        self._pos += 1

    def _next(self) -> str | None:
        return None if self._pos >= len(self._tokens) else self._tokens[self._pos]

    def _symbol_index(self) -> int:
        """Provides a unique number for a symbol index when called."""
        index = self._symbol_count
        self._symbol_count += 1
        return index

    def _parse_atom(self) -> Node:
        char = self._next()
        self._inc()

        # "(" <alt> ")"
        if char == "(":
            self._paren_count += 1
            alt = self._parse_alt()
            if (char := self._next()) != ")":
                raise SyntaxError(ERR_MSG.format("')'", self._pos, char))
            self._paren_count -= 1
            self._inc()
            return alt

        if char in {")", "|", "*"}:
            raise SyntaxError(ERR_MSG.format("symbol", self._pos, f"'{char}'"))
        if char is None:
            raise SyntaxError(ERR_MSG.format("symbol", self._pos, "empty string"))

        # <char>
        return Symbol(char, self._symbol_index())

    def _parse_star(self) -> Node:
        atom = self._parse_atom()

        # <atom> "*"
        if self._next() == "*":
            self._inc()
            return Star(atom)

        # <atom>
        return atom

    def _parse_concat(self) -> Node:
        star = self._parse_star()

        # <star> <concat>
        if self._next() not in {"|", ")", None}:
            return Concat(star, self._parse_concat())

        # <star>
        return star

    def _parse_alt(self) -> Node:
        concat = self._parse_concat()
        if self._next() == ")" and self._paren_count == 0:
            msg = f"unexpected close paren at index: {self._pos}"
            raise SyntaxError(msg)

        # <concat> "|" <alt>
        if self._next() == "|":
            self._inc()
            return Alt(concat, self._parse_alt())

        # <concat>
        return concat

    def parse(self) -> Node:
        """Returns the `Node` parsed from the given string."""
        # since multiple calls to _parse_alt would fail after the first, we
        # cache the result and return that on subsequent calls.
        if self._parsed is None:
            self._parsed = self._parse_alt()
        return self._parsed
