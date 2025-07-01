import pulp

def experiment_absolute():
    """
    We're interested in minimizing an absolute value.
    Let's try our hands at that.
    x in [0, 10]
    f(x) = -x + 10
    g(x) = x
    We want minimal |f(x) - g(y)|.
    """
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

experiment_absolute()
