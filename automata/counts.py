from automata.impl import (
    DetFollowAutomata,
    DetPositionAutomata,
    FollowAutomata,
    MarkBeforeAutomata,
    McNaughtonYamadaAutomata,
)
from automata.parser import Parser
from random import Random
from string import ascii_lowercase


def make_regex(
    length: int,
    ab_count: int = 0,
    star_chance: float = 0.1,
    alt_chance: float = 0.1,
    group_chance: float = 0.05,
    seed: int | None = None
) -> str:
    rng = Random(seed)

    alphabet = list(ascii_lowercase)
    if ab_count > 0:
        while len(alphabet) > ab_count:
            idx = rng.randrange(len(alphabet))
            alphabet.pop(idx)

    def _maker(_length: int) -> str:
        star = rng.random() < star_chance

        if _length == 1:
            char = alphabet[rng.randrange(len(alphabet))]
            return f"{char}*" if star else char

        len_left = rng.randrange(1, _length - 1) if _length > 2 else 1
        left = _maker(len_left)
        right = _maker(_length - len_left)

        alt = rng.random() < alt_chance
        grouped = rng.random() < group_chance

        binary = f"{left}|{right}" if alt else f"{left}{right}"
        grouped = f"({binary})" if alt and grouped and not star else binary
        return f"({grouped})*" if star else grouped

    return _maker(length)


if __name__ == "__main__":
    rg = make_regex(
        length=100,
        ab_count=2,
        star_chance=0.15,
        alt_chance=0.05,
        group_chance=0.05,
    )
    print(rg)
    print()

    # n = Parser("(b|ab)*|b*").parse()
    n = Parser(rg).parse()
    print(max(n.pos()), len(set(n.pos().values())), set(n.pos().values()))

    print(FollowAutomata(n).count_states())
    print(MarkBeforeAutomata(n).count_states())
    print(DetFollowAutomata(n).count_states())
    print(DetPositionAutomata(n).count_states())
    print(McNaughtonYamadaAutomata(n).count_states())
