import csv
from automata.impl import (
    Automata,
    DeterministicFollowAutomata,
    DeterministicPositionAutomata,
    FollowAutomata,
    MarkBeforeAutomata,
    # McNaughtonYamadaAutomata,
    PositionAutomata,
)
from automata.parser import Parser
from collections.abc import Iterator
from random import Random
from string import ascii_lowercase
from typing import Final


def make_regex(
    length: int,
    ab_count: int = 0,
    star_chance: float = 0.1,
    alt_chance: float = 0.1,
    group_chance: float = 0.05,
    seed: int | None = None
) -> str:
    """
    Create a regex pattern string with the given parameters. All symbols are
    drawn from the `ascii_lowercase` alphabet, i.e., [a..z].

    :param length: The total number of symbol occurrences contained in the
        pattern. Unique symbols may be included multiple times such that any
        regex has exactly this many symbols.
    :param ab_count: The maximum number of unique symbols this pattern may include.
    :param star_chance: The probability that "*" is generated
    :param alt_chance: The probability that "|" (alt) rather than concat is generated.
    :param group_chance: The probability that an alt node is grouped by
        parenthesis if it is not already starred,
    :param seed: Seed for controlling random generation.
    :return: Regex pattern string.
    """
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


CHARACTERISTICS: Final[list[dict[str, float]]] = [
    dict(ab_count=0, star_chance=0.05, alt_chance=0.05, group_chance=0.05),
    dict(ab_count=0, star_chance=0.0, alt_chance=0.15, group_chance=0.05),
    dict(ab_count=0, star_chance=0.15, alt_chance=0.0, group_chance=0.0),
    dict(ab_count=0, star_chance=0.15, alt_chance=0.15, group_chance=0.15),
    # often inflates state counts for Mark Before, DetPosition & McNaughtonYamada
    dict(ab_count=2, star_chance=0.15, alt_chance=0.05, group_chance=0.05),
    dict(ab_count=5, star_chance=0.15, alt_chance=0.05, group_chance=0.05),
    dict(ab_count=10, star_chance=0.15, alt_chance=0.05, group_chance=0.05),
    # increasing alt or group chance offsets this inflation
    dict(ab_count=2, star_chance=0.15, alt_chance=0.15, group_chance=0.15),
    dict(ab_count=5, star_chance=0.15, alt_chance=0.15, group_chance=0.15),
    dict(ab_count=10, star_chance=0.15, alt_chance=0.15, group_chance=0.15),
]

LENGTHS: Final[list[int]] = [5, 10, 20, 50, 100, 200]

ENGINES: Final[list[type[Automata]]] = [
    PositionAutomata,
    DeterministicFollowAutomata,
    DeterministicPositionAutomata,
    FollowAutomata,
    MarkBeforeAutomata,
    # McNaughtonYamadaAutomata
]


def collect_state_counts() -> Iterator[dict]:
    for length in LENGTHS:
        for kwargs in CHARACTERISTICS:
            for _ in range(10):
                pattern = make_regex(length, **kwargs)
                node = Parser(pattern).parse()
                results = {"pattern": pattern}
                for engine in ENGINES:
                    auto = engine(node)
                    name = engine.__name__.replace("Automata", "")
                    results[name] = auto.count_states()

                yield results


def write_state_counts(file: str) -> None:
    with open(file, mode="w") as f:
        counts = collect_state_counts()
        first = next(counts)

        writer = csv.DictWriter(f, first.keys())
        writer.writeheader()
        writer.writerow(first)
        writer.writerows(counts)


if __name__ == "__main__":
    rg = make_regex(
        length=100,
        ab_count=0,
        star_chance=0.15,
        alt_chance=0.15,
        group_chance=0.15,
    )
    print(rg)
    print()
    n = Parser(rg).parse()
    print(max(n.pos()), len(set(n.pos().values())), set(n.pos().values()))

    print(FollowAutomata(n).count_states())
    print(MarkBeforeAutomata(n).count_states())
    print(DeterministicFollowAutomata(n).count_states())
    print(DeterministicPositionAutomata(n).count_states())
    # print(McNaughtonYamadaAutomata(n).count_states())

    # write_state_counts("../state_counts.csv")
