import pulp
from main import get_alphabet, count_chars, spell_char, spell_chars, manhattan


def experiment_alphabet():
    """
    We attempt to generalize experiment_multiple_letters to a whole alphabet.
    In scope of this experiment we neglect the correct count for ',',
    but try to count the other letters correctly.
    """
    prefix = f"This text contains the following letters:\n"
    letters = get_alphabet(prefix=prefix)
    lower_bounds = {l: 0 for l in letters} | count_chars(prefix + "and")
    delta = 50
    upper_bounds = {k: v + delta for k, v in lower_bounds.items()}

    variables: dict[str, dict[pulp.LpVariable, int]] = {
        letter: {
            pulp.LpVariable(name=f"{letter}_{count}", cat=pulp.LpBinary): count
            for count in range(lower_bounds[letter], upper_bounds[letter] + 1)
        }
        for letter in letters
    }

    offsets: dict[str, list[(int, pulp.LpVariable)]] = {
        letter: [] for letter in letters
    }

    for letter, choices in variables.items():
        for variable, count in choices.items():
            implied_offset = count_chars(spell_char(letter, count))
            for offset_letter, offset_count in implied_offset.items():
                if offset_letter in offsets:
                    offsets[offset_letter].append((offset_count, variable))

    problem = pulp.LpProblem(name="Experiment_alphabet", sense=pulp.LpMinimize)

    manhattan_pairs = []
    additional_constraints = []
    for letter, choices in variables.items():
        weighted_choice = sum(
            [weight * variable for variable, weight in choices.items()]
        )
        offset_sum = sum([weight * variable for weight, variable in offsets[letter]])

        manhattan_pairs.append((lower_bounds[letter] + offset_sum, weighted_choice))

    manhattan_goal, manhattan_constraints = manhattan(manhattan_pairs)
    problem += manhattan_goal
    for constraint in manhattan_constraints + additional_constraints:
        problem += constraint

    for letter, choices in variables.items():
        problem += (
            sum([variable for variable, _ in choices.items()]) == 1,
            f"Pick exactly one {letter!r}",
        )

    problem.solve(solver=pulp.HiGHS())
    print(f"Problem status: {pulp.LpStatus[problem.status]}")
    for v in problem.variables():
        value = int(v.varValue)
        if value != 0:
            print(f"{v.name}={v.varValue}")

    expected_counts: dict[str, int] = {}
    for letter, choices in variables.items():
        for variable, count in choices.items():
            if int(variable.varValue) > 0:
                expected_counts[letter] = count

    output = f"{prefix}{spell_chars(expected_counts)}"
    print(output)

    actual_counts = count_chars(output)
    letters = set(expected_counts.keys()) and set(actual_counts.keys())
    count_differences = {
        letter: expected_counts.get(letter, 0) - actual_counts.get(letter, 0)
        for letter in letters
    }

    print(f"Count differences (expected - actual):\n{count_differences}")


experiment_alphabet()

"""
Produces this output:
---
This text contains the following letters:
six ❛-❜s, two ❛:❜s, two ❛T❜s, three ❛a❜s, two ❛c❜s, two ❛d❜s, thirty-one ❛e❜s,
seven ❛f❜s, five ❛g❜s, nine ❛h❜s, eighteen ❛i❜s, five ❛l❜s, seventeen ❛n❜s,
eleven ❛o❜s, six ❛r❜s, thirty-four ❛s❜s, twenty-eight ❛t❜s, two ❛u❜s, eight ❛v❜s,
ten ❛w❜s, six ❛x❜s, six ❛y❜s, twenty-five ❛❛❜s and twenty-five ❛❜❜s
Count differences (expected - actual):
{'❛': 0, 'y': 0, 'o': 0, 's': 0, ':': 0, 'n': 0, 'd': 0, 't': 0, 'a': 0, 'l': 0, 'g': 0, 'x': 0,
 ',': -22, 'c': 0, 'v': 0, 'h': 0, '-': 0, 'T': 0, '❜': 0, 'i': 0, 'u': 0, 'w': 0, 'e': 0, 'r': 0, 'f': 0}
"""
