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


def spell_instructions(chars: Vector, prefix: str, suffix: str) -> str:
    return f"{prefix}{spell_chars(chars)}{suffix}".strip()


default_prefix = "* Write down "
default_suffix = ", in a palindromic sequence whose second half runs thus:"


def spell_output(chars: Vector, prefix=default_prefix, suffix=default_suffix) -> str:
    start = f"{spell_instructions(chars, prefix, suffix)}".strip()
    return f"{start}\n{start[::-1]}"


def get_alphabet(prefix: str, suffix: str) -> Alphabet:
    letters = "".join(single_digit + double_digit + below_hundred)
    letters += dash + hundred + thousand + million + billion
    letters += (
        spell_char("a", 1) + spell_chars({}) + spell_instructions({}, prefix, suffix)
    )
    letters += prefix
    letters = "".join(letters.split())
    return sorted(list(set(letters)))


def vector_scale(vector: Vector, factor: int) -> Vector:
    return {k: v * factor for k, v in vector.items()}


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


def experiment_e():
    print("Experiment e\n")

    prefix = "The number of e's in this text is: "
    lower_limit = count_chars(prefix).get("e", 0)
    upper_limit = lower_limit + 4

    print(
        f"Choosing 'e' count from [{lower_limit}, {upper_limit}] for 'e's in\n\t{prefix!r}"
    )

    e_variables = {
        pulp.LpVariable(name=f"e_{count}", cat=pulp.LpBinary): count
        for count in range(lower_limit, upper_limit + 1)
    }

    e_offsets = {
        count: count_chars(spell_number(count)).get("e", 0)
        for count in e_variables.values()
    }
    print(f"e_offsets:{e_offsets!r}")
    total_number_of_e_s = lower_limit + sum([c * v for v, c in e_variables.items()])

    problem = pulp.LpProblem(name="Experiment_e", sense=pulp.LpMinimize)

    # Make sure we choose only one count:
    problem += sum(e_variables.keys()) == 1, "pick exactly one 'e'"

    # Construct e count constraint
    offset_sum = sum([e_offsets.get(c, 0) * v for v, c in e_variables.items()])
    weighted_variables = sum([-c * v for v, c in e_variables.items()])
    problem += lower_limit + offset_sum + weighted_variables == 0

    problem.solve(solver=pulp.HiGHS())
    print(f"Problem status: {pulp.LpStatus[problem.status]}")
    for v in problem.variables():
        value = int(v.varValue)
        if value != 0:
            print(f"{v.name}={v.varValue}")
            print(f"{prefix + spell_number(e_variables[v])!r}")


def new_main():
    print("new_main()\n")
    prefix = default_prefix
    suffix = default_suffix

    alphabet = get_alphabet(prefix=prefix, suffix=suffix)
    bound_delta = 100

    lower_bounds = {letter: 0 for letter in alphabet} | vector_scale(
        count_chars(spell_output({}, prefix)), 2
    )
    upper_bounds = {
        letter: count + bound_delta for letter, count in lower_bounds.items()
    }

    letter_variables_counts = {
        letter: {
            pulp.LpVariable(name=f"{letter}_{count}", cat=pulp.LpBinary): count
            for count in range(lower_bounds[letter], upper_bounds[letter] + 1, 2)
        }
        for letter in alphabet
    }

    """
    We map each letter to a list of tuples.
    These tuples are weight, variable for every variable
    that contributes to the offset count of a letter.
    """
    letter_count_offsets: dict[str, list[(int, pulp.LpVariable)]] = {
        letter: [] for letter in alphabet
    }

    for letter, choices in letter_variables_counts.items():
        for variable, count in choices.items():  # e_68, 68
            offset_vector = vector_scale(
                count_chars(spell_char(letter, count)), 2
            )  # 2 * (achtundsechtzig es -> a:1, c:2)
            for offset_letter, offset_count in offset_vector.items():
                letter_count_offsets[offset_letter].append((offset_count, variable))

    problem = pulp.LpProblem(name="Experiment_e", sense=pulp.LpMinimize)

    # For every letter we chose exactly one count:
    for letter, choices in letter_variables_counts.items():
        problem += sum(choices.keys()) == 1, f"pick exactly one {letter!r}"

    # For every letter we have a letter specific constraint
    for letter in alphabet:
        # FIXME for ',' we need something extra
        offset_sum = sum([c * v for c, v in letter_count_offsets[letter]])
        weighted_variables = sum(
            [-c * v for v, c in letter_variables_counts[letter].items()]
        )
        problem += lower_bounds[letter] + offset_sum + weighted_variables == 0

    print(letter_count_offsets["e"])

    problem.solve(solver=pulp.HiGHS())

    print(f"Problem status: {pulp.LpStatus[problem.status]}")
    for v in problem.variables():
        value = int(v.varValue)
        if value != 0:
            print(f"{v.name}={value} ({v.varValue})")


def thingy():
    print("thingy()")
    prefix = "Edwin would you believe it? This text has "
    alphabet = get_alphabet(prefix=prefix, suffix="")

    bound_delta = 100
    lower_bounds = {letter: 0 for letter in alphabet} | count_chars(
        f"{spell_instructions(chars={}, prefix=prefix, suffix="")}".strip()
    )
    upper_bounds = {
        letter: count + bound_delta for letter, count in lower_bounds.items()
    }

    letter_variables_counts = {
        letter: {
            pulp.LpVariable(
                name=f"{letter if letter != '-' else '_'}_{count}", cat=pulp.LpBinary
            ): count
            for count in range(lower_bounds[letter], upper_bounds[letter] + 1)
        }
        for letter in alphabet
    }

    variable_letter_counts = {
        variable: (letter, count)
        for letter, choices in letter_variables_counts.items()
        for variable, count in choices.items()
    }

    """
    We map each letter to a list of tuples.
    These tuples are weight, variable for every variable
    that contributes to the offset count of a letter.
    """
    letter_count_offsets: dict[str, list[(int, pulp.LpVariable)]] = {
        letter: [] for letter in alphabet
    }

    for letter, choices in letter_variables_counts.items():
        for variable, count in choices.items():
            offset_vector = count_chars(spell_char(letter, count))
            for offset_letter, offset_count in offset_vector.items():
                letter_count_offsets[offset_letter].append((offset_count, variable))

    problem = pulp.LpProblem(name="thingy", sense=pulp.LpMinimize)

    # For every letter we chose exactly one count:
    for letter, choices in letter_variables_counts.items():
        problem += sum(choices.keys()) == 1, f"pick exactly one {letter!r}"

    # For every letter we have a letter specific constraint
    # for letter in alphabet:
    goals = [
        "E",
        "d",
        "w",
        "i",
        "n",
        "o",
        "u",
        "l",
        "y",
        "u",
        "b",
        "e",
        "v",
        "t",
        "?",
        "T",
        "h",
        "a",
        "s",
        "x",
        # "❛",
        # "❜",
    ]
    goals = set(alphabet) - set(["❛", "❜", ",", "-", "v", "f", "r"])
    goals = alphabet
    for letter in goals:
        # FIXME for ',' we need something extra
        offset_sum = sum([c * v for c, v in letter_count_offsets[letter]])
        weighted_variables = sum(
            [-c * v for v, c in letter_variables_counts[letter].items()]
        )
        problem += lower_bounds[letter] + offset_sum + weighted_variables == 0

    problem.solve(solver=pulp.HiGHS())

    print(f"Problem status: {pulp.LpStatus[problem.status]}")
    solution = dict(
        [
            variable_letter_counts[variable]
            for variable in problem.variables()
            if int(variable.varValue) != 0
        ]
    )
    print(f"solution: {solution}")
    spelled_solution = spell_instructions(chars=solution, prefix=prefix, suffix="")
    print(f"spelled_solution:\n\t{spelled_solution}")
    actual_count = count_chars(spelled_solution)

    actual_expected = {
        letter: (actual_count.get(letter, 0), solution.get(letter, 0))
        for letter in goals
    }
    print(f"letter: actual, expected:\n\t{actual_expected}")


def absolute_example():
    """
    We're interesting in minimizing an absolute value.
    Let's try our hands at that.
    x in [0, 10]
    f(x) = -x + 10
    g(x) = x
    We want minimal |f(x) - g(y)|.
    """
    print("absolute_example()")
    x = pulp.LpVariable(name="x", lowBound=0, upBound=10, cat=pulp.LpInteger)

    f_x = -x + 10
    g_x = x

    abs_f_g = pulp.LpVariable(name="abs_f_g", lowBound=0, cat=pulp.LpInteger)

    abs_constraint_1 = abs_f_g >= f_x - g_x
    abs_constraint_2 = abs_f_g >= -(f_x - g_x)

    problem = pulp.LpProblem(name="absolute", sense=pulp.LpMinimize)

    # We minimize the absolute value:
    problem += abs_f_g

    # We add the constraints for the absolute value:
    problem += abs_constraint_1
    problem += abs_constraint_2

    problem.solve(solver=pulp.HiGHS())

    print(f"Problem status: {pulp.LpStatus[problem.status]}")
    for v in problem.variables():
        value = int(v.varValue)
        print(f"{v.name} = {value}")


def abs(x: pulp.LpVariable, y: pulp.LpVariable) -> (pulp.LpVariable, list[pulp.LpConstraint]):
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


def manhattan(xys: list[(pulp.LpVariable, pulp.LpVariable)]) -> (pulp.LpConstraint, list[pulp.LpConstraint]):
    """
    Construct a tuple of (optimization_goal, constraints) where:
    - optimization_goal computes the manhattan distance of the tuples provided in xys.
    - constraints is a list of additional problem constraints produced from helper variables.
    """
    deltas = []
    constraints = []

    for (x, y) in xys:
        (delta, cs) = abs(x, y)
        deltas.append(delta)
        constraints += cs
    
    return (sum(deltas), constraints)



if __name__ == "__main__":
    # print(f"pulp got these solvers: {pulp.listSolvers(True)!r}")
    # experiment_e()
    # new_main()
    # thingy()
    absolute_example()
