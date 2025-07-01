import pulp
from main import manhattan

def experiment_manhattan():
    """
    We'd like to minimize a manhattan distance with 6 variables.
    |x1 - y1| + |x2 - y2| + |x3 - y3|
    Where
    - xn, yn in [-10, 10]
    - x1 >= 2
    - x2 == 1
    - x3 <= 4
    - y1 <= 3
    - y2 == 0
    - y3 >= 5
    """
    x1 = pulp.LpVariable(name="x1", lowBound=-10, upBound=10)
    x2 = pulp.LpVariable(name="x2", lowBound=-10, upBound=10)
    x3 = pulp.LpVariable(name="x3", lowBound=-10, upBound=10)
    y1 = pulp.LpVariable(name="y1", lowBound=-10, upBound=10)
    y2 = pulp.LpVariable(name="y2", lowBound=-10, upBound=10)
    y3 = pulp.LpVariable(name="y3", lowBound=-10, upBound=10)

    problem = pulp.LpProblem(name="experiment_manhattan")

    problem += manhattan([(x1, y1), (x2, y2), (x3, y3)])

    problem += x1 >= 2
    problem += x2 == 1
    problem += x3 <= 4
    problem += y1 <= 3
    problem += y2 == 0
    problem += y3 >= 5

    problem.solve(solver=pulp.HiGHS())

    print(f"Problem status: {pulp.LpStatus[problem.status]}")
    print("\n".join([f"\t{v.name} = {v.varValue}" for v in [x1, x2, x3, y1, y2, y3]]))


experiment_manhattan()
