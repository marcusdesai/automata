import csv
from automata.impl import ENGINES
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


def collect_state_counts() -> Iterator[dict]:
    for length in LENGTHS:
        for kwargs in CHARACTERISTICS:
            for _ in range(10):
                pattern = make_regex(length, **kwargs)
                node = Parser(pattern).parse()
                results = {"pattern": pattern}
                for name, make_automata in ENGINES.items():
                    results[name] = make_automata(node).count_states()
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
        length=200,
        ab_count=0,
        star_chance=0.15,
        alt_chance=0.15,
        group_chance=0.15,
    )
    print(rg)
    print()
    nd = Parser(rg).parse()
    print(max(nd.pos()), len(set(nd.pos().values())), set(nd.pos().values()))

    for _name, _make_automata in ENGINES.items():
        if _name in {
            "Position",
            "PositionDeterminised",
            "Follow",
            "FollowDeterminised",
            "MarkBefore",
            "MarkBeforeMinimized",
        }:
            print(_name, _make_automata(nd).count_states())

    # write_state_counts("../state_counts.csv")

    # Position 200
    # PositionDeterminised 197
    # PositionMinimized 138
    # McNaughtonYamada 197
    # McNaughtonYamadaMinimized 138
    # Follow 135
    # FollowDeterminised 142
    # FollowMinimized 138
    # MarkBefore 138 <- nice!
    # MarkBeforeMinimized 138
    ex1 = (
        "(l(b|n)*(gu*mv*w|n|(pq)*)*odvb(e*m)*((kh)*|(ta)*zjm|(a|e)*)*(m*|x)*|ds("
        "sz)*(tv|f|a)*|b*g(z|y*(pp|xaqufb)*(c|gem)*(i|k)*eligvu|igy|r|a)*bslesxe"
        "|ffki*(cr*)*s|pxwjv*w((o|i)*|(qgnunu)*k|cu(fj)*wj(x|k*)(k|(qh)*)dnq(h*f"
        "(qvqwn)*)*t(d*xr*ynm)*(tgaf|ha(pi)*)*v(bq|e)*uz*h|e|atxxzm(etyh(o|m|r)*"
        "m*|gf|x|oj|lou*|g(c|e|s)*)*q*qdc|eb|ft)*(p|u)*bcpwl|tp|u|s|v|t(xj)*(x*|"
        "m|t)*e*ow*|icv|la|il)*"
    )

    # Position 300
    # PositionDeterminised 2746
    # Follow 224
    # FollowDeterminised 2508
    # MarkBefore 2351
    # MarkBeforeMinimized 360
    ex2 = (
        "(ii)*giiggggi|(g|g)(gg(ig)*|ggggiggiiiig|g*(iiii|i)*gig*iig|gii*gggig*)"
        "*(igggiiiii)*giigg|ig*gg*igg*iggigigig*g*giiiii*(ii*|g)*gg*i(gggiig)*g|"
        "ggi|g|(ig)*|i(ig)*(ii|g*)*(((((g|g*)ig|(ig)*(i*gi)*)*i|giiggig(i|gg)ig|"
        "ggiigiiigg(igg)*)*igi*ggg)*((ii*ggggiggggi*iii)*g(ig|gg)*)*g|(gg*)*gii|"
        "ig(gi)*(iggg*)*g|i(iiggiigg*g*|g|i|i|i(gi)*gg(gg|iiig|gg*(gg)*)*ig*g*i*"
        "g(i|g)*i|i*(i*g)*i|giggg*i)*i|g*igggg)*gg|i|i(g(gg|g)*iii)*g((gg*)*i*i)"
        "*|i*|i*g|(i(i|i*)*|giiii|g|g)gg((g(gg)*ig)*(g|i)*|gg)*g(g(gg)*)*ii*gggi"
        "i(g|i)*|gggi*iiig"
    )

    # Position 300
    # PositionDeterminised 24456
    # PositionMinimized 1497
    # Follow 228
    # FollowDeterminised 21985
    # MarkBefore 20290
    ex3 = (
        "((f*vf|v)*(v(v|f)v|f*)*vf)*f*f(v(fff*)*ffv*|v*fv|ffffffv)*f*v|f(vv)*vff"
        "vfvfvvf(v(vf)*)*vvv(f|(fffff|f*v)*)*vvv*vfv*(ffvvvv)*(vf(v|v*)vfv)*vff("
        "fv*ffv)*|fv*(fv*f)*|v*fv|(ffvfv(fv)*|f*(vff(v|f)*)*)*((v(vv)*)*|v*(vfv)"
        "*(fvf*v)*)*vff(vvvv)*fv|v|v*v*vv*f(vf*fv*v)*(fff*)*vff|vffv(f|f*)*vfv*f"
        "ff(((f|f)*vv(vf|ff|fvf(ff)*|vv*ffff*)*vfvvfffvfff*v|(vf|(ff)*)(fv)*vvv|"
        "vv*fv(v*|vv)(v|f*f*)*(v|f*))*(vv)*fvv*v|ffff(ff(ff)*v(vv)*)*(ff|(fv)*v*"
        "v)*|(fvvf)*(f|vv|vvv)*fv*ffvv(ff*vv*|fv*)*|(f|f)*vf|(f*f)*ffff|((fv)*f|"
        "v(vv*)*v*|v(fv*)*)*)(fvff(vvv|(f*v)*|ffvfvvfff((v*v*v|v*)*((v|v|f)*fv)*"
        ")*))*"
    )

    # Position 100
    # PositionDeterminised 285
    # Follow 74
    # FollowDeterminised 256
    # MarkBefore 248
    # MarkBeforeMinimized 58
    ex4 = (
        "fmm(ff|(m|f))f|(f*|f)(fff|fmf*f)*((fmm)*m|(ff)*mffm|fm|((f*m|mf|(mf)*)*"
        "f|f)*)*mmff*f(mf)*(fmfm)*fm|((mm*f|fm*|m*m|mfffm(f*mfm)*)mf|(fm)*f*mfmf"
        "*mmmmm*f|f(mmff*ff|(fmm|f)*fm|f*(mmf*|ff))*)*"
    )

    # Position 100
    # PositionDeterminised 2636
    # Follow 84
    # FollowDeterminised 2564
    # MarkBefore 2487
    # MarkBeforeMinimized 816
    ex5 = (
        "((p*pyp(pppyyyypypp*yy*yyp*p*(yp)*pp(pp)*)*)*y(yypp*y)*p*(yy)*py(y*pp(p"
        "yp)*(py)*yy)*)*(yp*)*((yypy)*py)*(ppp)*ppyy*y*p(ypypy*(pp*)*y(y*y)*ppy*"
        "ppyp*ppyp)*p*(yp)*yppyyppyy*yy"
    )

    # Position 100
    # PositionDeterminised 96
    # Follow 90
    # FollowDeterminised 91
    # MarkBefore 91
    # MarkBeforeMinimized 36
    ex6 = (
        "ggpgpppppppgppgp(gp)*(pp)*|pppgpgpggpgpgg(pgpg)*g(pg)*ppgppg(pp)*gpgpgp"
        "pgg(gp|ppp)pgp|ppp(ggggppgpgg*ggg)*(g|p)*p|pgggpppppgpp*ppg"
    )
