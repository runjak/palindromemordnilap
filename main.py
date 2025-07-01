import pulp

type Vector = dict[str, int]
type Alphabet = list[str]

single_digit = [
    "",
    "one",
    "two",
    "three",
    "four",
    "five",
    "six",
    "seven",
    "eight",
    "nine",
]
double_digit = [
    "ten",
    "eleven",
    "twelve",
    "thirteen",
    "fourteen",
    "fifteen",
    "sixteen",
    "seventeen",
    "eighteen",
    "nineteen",
]
below_hundred = [
    "twenty",
    "thirty",
    "forty",
    "fifty",
    "sixty",
    "seventy",
    "eighty",
    "ninety",
]

hundred = "hundred"
thousand = "thousand"
million = "million"
billion = "billion"
dash = "-"


def spell_number(n: int) -> str:
    if n <= 0:
        return ""
    if n < 10:
        return single_digit[n]
    if n < 20:
        return double_digit[n - 10]
    if n < 100:
        below, recurse = below_hundred[(n - (n % 10)) // 10 - 2], spell_number(n % 10)
        if len(recurse) == 0:
            return below
        return f"{below}{dash}{recurse}"
    if n < 1_000:
        return f"{single_digit[n // 100]} {hundred} {spell_number(n % 100)}"
    if n < 1_000_000:
        return f"{spell_number(n // 1_000)} {thousand} {spell_number(n % 1_000)}"
    if n < 1_000_000_000:
        return f"{spell_number(n // 1_000_000)} {million} {spell_number(n % 1_000_000)}"
    return f"{spell_number(n // 1_000_000_000)} {billion} ${spell_number(n % 1_000_000_000)}"


def spell_char(c: str, n: int) -> str:
    if n == 0:
        return ""
    return f"{spell_number(n).strip()} ❛{c}❜s"


def spell_chars(chars: Vector) -> str:
    spelled = [spell_char(c, n) for c, n in chars.items() if n > 0]
    [*parts, last] = spelled if len(spelled) > 0 else [""]
    return f"{", ".join(parts)} and {last}"


def get_alphabet(prefix: str) -> Alphabet:
    letters = "".join(single_digit + double_digit + below_hundred)
    letters += dash + hundred + thousand + million + billion
    letters += spell_char("a", 1) + spell_chars({})
    letters += prefix
    letters += ','
    letters = "".join(letters.split())
    return sorted(list(set(letters)))


def count_chars(s: str) -> Vector:
    return {c: s.count(c) for c in set("".join(s.split()))}


def implies(a: pulp.LpVariable, b: pulp.LpVariable) -> pulp.LpConstraint:
    """
    How do implications work in ILP?
    a -> b

    !a | b
    1 1 1
    1 0 0
    0 1 1
    0 0 1

    a - b < 1
    1 1 ( 0) 1
    1 0 ( 1) 0
    0 1 (-1) 1
    0 0 ( 0) 1

    a - b <= 0
    """
    return a - b <= 0


def abs(
    x: pulp.LpVariable, y: pulp.LpVariable
) -> (pulp.LpVariable, list[pulp.LpConstraint]):
    """
    By introducing a help variable 'delta',
    we can compute the absolute difference between two values.
    The 'trick' is that we constrain the variable to be >= the linear parts of the absolute value.
    Hence the result is a tuple of the new variable alongside the implied constraints.
    """
    delta = pulp.LpVariable(name=f"delta_({x})_({y})", lowBound=0, cat=pulp.LpInteger)

    constraints = [
        delta >= x - y,
        delta >= -(x - y),
    ]

    return (delta, constraints)


def manhattan(
    xys: list[(pulp.LpVariable, pulp.LpVariable)]
) -> (pulp.LpConstraint, list[pulp.LpConstraint]):
    """
    Construct a tuple of (optimization_goal, constraints) where:
    - optimization_goal computes the manhattan distance of the tuples provided in xys.
    - constraints is a list of additional problem constraints produced from helper variables.
    """
    deltas = []
    constraints = []

    for x, y in xys:
        (delta, cs) = abs(x, y)
        deltas.append(delta)
        constraints += cs

    return (sum(deltas), constraints)


def get_bounds(
    prefix: str, alphabet: Alphabet, bound_delta: int
) -> (dict[str, int], dict[str, int]):
    lower_bounds: dict[str, int] = {letter: 0 for letter in alphabet} | count_chars(
        prefix
    )
    upper_bounds: dict[str, int] = {
        letter: count + bound_delta for letter, count in lower_bounds.items()
    }
    return (lower_bounds, upper_bounds)


def get_letters_to_variables_to_counts(
    alphabet: Alphabet, lower_bounds: dict[str, int], upper_bounds: dict[str, int]
) -> dict[str, dict[pulp.LpVariable, int]]:
    return {
        letter: {
            pulp.LpVariable(
                name=f"{letter if letter != '-' else '_'}_{count}", cat=pulp.LpBinary
            ): count
            for count in range(lower_bounds[letter], upper_bounds[letter] + 1)
        }
        for letter in alphabet
    }


if __name__ == "__main__":
    print(f"pulp got these solvers: {pulp.listSolvers(True)!r}")
