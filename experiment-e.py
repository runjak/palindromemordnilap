import pulp
from main import count_chars, spell_number

def experiment_e():
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

experiment_e()