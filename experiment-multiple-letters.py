import pulp
from main import count_chars, spell_char, spell_chars

def experiment_multiple_letters():
    """
    We attempt to reformulate experiment_e to count multiple distinct letters.
    """
    letters = ["e", "f", "t", "h"]
    prefix = (
        f"The number of {", ".join(f"❛{l}❜s" for l in letters)} in this text is:\n\t"
    )
    lower_bounds = {k: v for k, v in count_chars(prefix).items() if k in letters}
    delta = 10
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
            implied_offset = count_chars(spell_char(letter, count)).items()
            for offset_letter, offset_count in implied_offset:
                if offset_letter in offsets:
                    offsets[offset_letter].append((offset_count, variable))

    problem = pulp.LpProblem(name="Experiment_multiple_letters", sense=pulp.LpMinimize)

    for letter, choices in variables.items():
        problem += (
            sum([variable for variable, _ in choices.items()]) == 1,
            f"Pick exactly one {letter!r}",
        )

    for letter, choices in variables.items():
        weighted_choice = sum(
            [weight * variable for variable, weight in choices.items()]
        )

        offset_sum = sum([weight * variable for weight, variable in offsets[letter]])

        problem += (
            lower_bounds[letter] + offset_sum - weighted_choice == 0,
            f"Count of {letter} is balanced",
        )

    problem.solve(solver=pulp.HiGHS())
    print(f"Problem status: {pulp.LpStatus[problem.status]}")
    for v in problem.variables():
        value = int(v.varValue)
        if value != 0:
            print(f"{v.name}={v.varValue}")

    counts: dict[str, int] = {}
    for letter, choices in variables.items():
        for variable, count in choices.items():
            if int(variable.varValue) > 0:
                counts[letter] = count

    print(f"{prefix}{spell_chars(counts)}")

experiment_multiple_letters()
