# Automata

Welcome! This is the companion repo to my [series][part-1] of blog posts on constructing [automata][automata] from regexes.

This repo contains one package: `automata`, implemented in Python 3.11, which has the following layout:

- `tree.py` contains the Abstract Syntax Tree that we parse regex strings (e.g. `"a|b*"`) into.
- `parser.py` unsurprisingly contains this parser.
- `automata.py` includes an abstract base class for all the automata that we will define, along with concrete automata class implementations.

Expect the `main` branch of this repo to be updated as I publish more posts in the series. Each post which has companion code specific to that post will have it's own branch in the repo containing the code developed up to that point, not all posts will have companion code.

## Posts

- Part 1: [Understanding Position Automata][part-1] (no companion code)
- Part 2: [Implementing Position Automata](https://blog.mrcsd.com/2023/Aug/implementing-pos-automata) (`2-implementing-pos-automata`)

[automata]: https://en.wikipedia.org/wiki/Automata_theory
[part-1]: https://blog.mrcsd.com/2023/Aug/position-automata
