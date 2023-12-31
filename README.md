# Automata

Welcome! This is the companion repo to my [series][part-1] of blog posts on constructing [automata][automata] from regexes.

## Setup

In the root dir of this repo:

```bash
# to install
pip install -e ".[dev]"

# run tests
pytest

# test with coverage
pytest --cov=automata --cov-branch --cov-report=term
```

## Layout

This repo contains one package: `automata`, implemented in Python 3.11, which has the following layout.

- `tree.py` contains the Abstract Syntax Tree that we parse regex strings (e.g. `"a|b*"`) into.
- `parser.py` unsurprisingly contains this parser.
- `impl.py` includes an abstract base class for all the automata that we will define, along with concrete automata class implementations.

Expect the `main` branch of this repo to be updated as I publish more posts in the series. Each post which has companion code specific to that post will have it's own branch in the repo containing the code developed up to that point, not all posts will have companion code.

## Posts

- Part 1: [Understanding Position Automata][part-1] (no companion code)
- Part 2: [Implementing Position Automata][part-2] (`2-implementing-pos-automata`)
- Part 3: [Follow Automata][part-3] (`3-follow-automata`)
- Part 4: Mark Before Automata (`4-mark-before-automata`)

[automata]: https://en.wikipedia.org/wiki/Automata_theory
[part-1]: https://blog.mrcsd.com/2023/Aug/position-automata
[part-2]: https://blog.mrcsd.com/2023/Aug/implementing-pos-automata
[part-3]: https://blog.mrcsd.com/2023/Aug/follow-automata
