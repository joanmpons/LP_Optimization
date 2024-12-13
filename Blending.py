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
Blending optimization problem.

Goal: Given two possible final products and three materials,
we aim at maximizing the profit whilst respecting the blending constraints for creating the final product,
meeting customer demand, and not using more than the available materials' resources.

Scenario: Suppose we produce two final products (FP) by blending three different basic
materials. Each FP needs to contain specific proportions of the materials in a strict range
in order to pass the quality control. Moreover, we know their market prices and the 
consumer demand for the products. As per the materials, each has a cost and a maximum qty available.

Given these constraints, we want to determine how much of each material we should use in
the fabrication of each product, how much of each final product we should be producing
and the expected profits.

""",
)

# Data definition
materials = [
    "Material_1",
    "Material_2",
    "Material_3",
]
materials_cost = {
    "Material_1": 8,
    "Material_2": 6,
    "Material_3": 5,
}
materials_qty = {
    "Material_1": 10000,
    "Material_2": 5000,
    "Material_3": 6000,
}
final_products = [
    "Final_Product_1",
    "Final_Product_2",
]
fp_materials_required = {
    "Final_Product_1": {
        "Material_1": [0.45, 0.55],
        "Material_2": [0.1, 0.15],
        "Material_3": [0.35, 0.35],
    },
    "Final_Product_2": {
        "Material_1": [0.2, 0.5],
        "Material_2": [0.1, 0.6],
        "Material_3": [0.3, 0.4],
    },
}
fp_selling_prices = {
    "Final_Product_1": 16,
    "Final_Product_2": 18,
}
fp_demand = {
    "Final_Product_1": 7000,
    "Final_Product_2": 8000,
}

# Variables definition
vars = LpVariable.dicts(
    "Amount",
    [(i, j) for i in materials for j in final_products],
    lowBound=0,  # Lowbound is set to avoid negative material amounts
    cat="Continuous",  # Variables are continuous
)

# The objective is to maximize profit
objective = lpSum(
    [
        (vars[(i, j)] * fp_selling_prices[j]) - (vars[(i, j)] * materials_cost[i])
        for i in materials
        for j in final_products
    ],
)

# Defines the problem
problem = LpProblem("Blending", sense=LpMaximize)

problem += (objective, "Objective")

# %% Constraints definition

# Creating min material qty constraint
for i in materials:
    constraint = None
    constraint = lpSum([vars[(i, j)] for j in final_products]) - materials_qty[i]
    problem += (constraint <= 0, f"Min_qty_{i}")
# Creating demand constraint
for j in final_products:
    constraint = None
    constraint = lpSum([vars[(i, j)] for i in materials]) - fp_demand[j]
    problem += (constraint >= 0, f"Demand_{j}")
# Creating min and max material percentage constraints
for iteraton in list(range(2)):
    for j in final_products:
        for i in materials:
            if iteraton == 1:
                constraint = None
                constraint = vars[(i, j)] - min(fp_materials_required[j][i]) * lpSum(
                    vars[(i, j)] for i in materials
                )
                problem += (constraint >= 0, f"Min_material_percentage_{i}_{j}")

            else:
                constraint = None
                constraint = vars[(i, j)] - max(fp_materials_required[j][i]) * lpSum(
                    vars[(i, j)] for i in materials
                )
                problem += (constraint <= 0, f"Max_material_percentage_{i}_{j}")
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
results = {v.name: v.varValue for v in problem.variables()}
df_results = pd.DataFrame.from_dict(
    results,
    orient="index",
    columns=["value"],
).reset_index()
profits = {
    "Final_Product_1": (
        df_results[df_results["index"].str.contains("Final_Product_1")].sum()
        * fp_selling_prices["Final_Product_1"]
    )["value"],
    "Final_Product_2": (
        df_results[df_results["index"].str.contains("Final_Product_2")].sum()
        * fp_selling_prices["Final_Product_2"]
    )["value"],
}
print("\nProfits:\n", profits)
