# %% Import libraries

# Import linear optimization library
# Import time for performance tests
import time

# Import numpy and pandas
import pandas as pd
from pulp import LpMaximize, LpProblem, LpStatus, LpVariable, getSolver, lpSum

# %% Problem definition

# Problem description
print(
    """
Resource allocation optimization problem.

Goal: Given six investments and the possibility to borrow money,
we aim at maximizing the profit whilst respecting the constraints of the maximum borrowing
and investing amounts, asset value at the end of period (EOP) and porfolio risk.

Scenario: Suppose an investor can invest up to 300000 and borrow up to 100000 to invest
in either of 6 different opportunities. His average porfolio risk cannot be greater than 10
and the assets must generate at least a 7 percentage return EOP. Furthermore,
there are additional constraints on the maximum amounts absolute and relative that can be
used for each investment. Given these constraints and the expected returns on the investments,
we want to determine how much we should invest in each and the estimated profits.
""",
)

# Investments list
investments = [
    "Investment_1",
    "Investment_2",
    "Investment_3",
    "Investment_4",
    "Investment_5",
    "Investment_6",
    "Borrowed",
]

investment_expected_returns = {
    "Investment_1": 1.18,
    "Investment_2": 1.1,
    "Investment_3": 1,
    "Investment_4": 1.06,
    "Investment_5": 1,
    "Investment_6": 1.20,
    "Borrowed": 1.12,
}

investment_risks = {
    "Investment_1": 20,
    "Investment_2": 12,
    "Investment_3": 1,
    "Investment_4": 7,
    "Investment_5": 3,
    "Investment_6": 30,
    "Borrowed": 0,
}

max_borrowing = 100000
max_investment_amount = 300000

# Variables definition
vars = LpVariable.dicts(
    "Amount",
    investments,
    lowBound=0,  # Lowbound is set to avoid negative investment amounts
    cat="Continuous",  # Variables are continuous
)

# Objective function definition: we aim at maximizing profit which is the sum over all investments times their expected returns
objective = lpSum([vars[i] * investment_expected_returns[i] for i in investments])

# Defines the problem
problem = LpProblem("Allocation_of_resources", sense=LpMaximize)

problem += (objective, "Objective")

# %% Constraints definition

# Creating max borrowing constraint
problem += (vars["Borrowed"] <= max_borrowing, "Max_Borrowing")
# Creating max investment constraint
constraint = None
for i in investments[:-1]:
    constraint += vars[i]
constraint -= vars[investments[-1]]
problem += (constraint <= max_investment_amount, "Max_Investment_Amount")
# Creating max average risk constraint
constraint = None
for i in investments[:-1]:
    constraint += investment_risks[i] * vars[i] - 10 * vars[i]
problem += (constraint <= 0, "Max_AVG_Risk")
# Creating constraint on asset value EOP
constraint = None
for i in investments:
    constraint += investment_expected_returns[i] * vars[i] - 1.07 * vars[i]
problem += (constraint >= 0, "Asset_EOP_Value")
# Creating constraint on investment distribution
constraint = None
constraint = vars["Investment_1"] + vars["Investment_2"] - 0.2 * max_investment_amount
problem += (constraint <= 0, "Investment_20%_Assets_1&2")
constraint = None
constraint = (
    vars["Investment_4"]
    + vars["Investment_5"]
    + vars["Investment_6"]
    - lpSum([0.5 * vars[i] for i in investments[:-1]])
)
problem += (constraint >= 0, "Investment_50%_Assets_4&5&6")

# %% Execution and performance test
# Setting initial execution time, specifying solver and writing the problem
start_t = time.time()
solver = getSolver("PULP_CBC_CMD", msg=0)
problem.writeLP("Allocation_of_resources.lp")

# Solves the problem
problem.solve(solver)
end_t = time.time()

# Prints execution time
print("Time of execution:", (end_t - start_t), "s")

# Prints solution status
print("Status:", LpStatus[problem.status])

# Specifies the solver used
print("Solver:", problem.solver)

# %% Problem log

# Write optimization problem specifications into an auxiliary text file
# problem_log = str(problem)

# with open("problem_log.txt","w") as f:
#    f.write(problem_log)

# %% Showing results and calculating profits

# Storing and printing results
results = {v.name: v.varValue for v in problem.variables()}
df_results = pd.DataFrame.from_dict(results, orient="index", columns=["value"])
print("Results: \n", df_results)

# Calculating and printing profits
investments_profit = df_results["value"].to_numpy() * [
    investment_expected_returns[i] for i in investments
]
print("\nProfit by investments: ", investments_profit)
print("Total Profit: ", investments_profit.sum())
