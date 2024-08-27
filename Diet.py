#%% Import libraries

#Import linear optimization library
from pulp import LpVariable, LpProblem, LpMinimize, LpStatus, LpMaximize, LpSolverDefault, lpSum, getSolver
#Import numpy and pandas
import numpy as np
import pandas as pd
#Import time for performance tests
import time

#%% Problem definition

#Problem description
print(
"""
Diet planning optimization problem.

Goal: Given three products p1, p2 and p3 and their respective costs,
we aim at minimizing the overall dietary cost whilst respecting the nutritional intake constraints.

Scenario: Suppose we are provided with the nutritional contents of the three aforementioned products, as well as some
nutritional intake requirements and we are asked to create a diet. Given these dietary constraints and the
cost of the products, we want to determine how much of each product we should be buying and the estimated cost given these quantities.
"""
)

#Products list
products = [
    "Product_1",
    "Product_2",
    "Product_3"
]

products_cost = {
    "Product_1": 1.59,
    "Product_2": 2.19,
    "Product_3": 2.99
}

nutritional_contents = {
    "Product_1": {
        "Calories": 250,
        "Fat": 13,
        "Carbohydrates": 119
        },
    "Product_2": {
        "Calories": 380,
        "Fat": 31,
        "Carbohydrates": 10.3
        },
    "Product_3": {
        "Calories": 257,
        "Fat": 28,
        "Carbohydrates": 39.2
        }
}

nutritional_requirements = {
    "Calories": {
        "Min": 1800,
        "Max": 2200,
        },
    "Fat": {
        "Max": 100,
        }
}


#Variables definition
vars = LpVariable.dicts("Quantity",
                 [P for P in products],              
                  lowBound = 0, #Lowbound is set to avoid negative product quantities
                  cat = "Continuous") #Variables are continuous

#Objective function definition: we aim at minimizing the cost which is the sum over all products of product quantity times price
objective = lpSum([vars[P] * products_cost[P] for P in products])

#Defines the problem
problem = LpProblem("Diet",
                    sense = LpMinimize)

problem += (objective, "Objective")

#%% Constraints definition

#Creating minimum and maximum intake constraints: 

for NC in ["Calories", "Fat"]:
    for req in nutritional_requirements[NC].keys():
        constraint = None
        
        for P in products:
            constraint += vars[P] * nutritional_contents[P][NC]

        if req == "Max":
            problem += (constraint <= nutritional_requirements[NC][req],
                        f"{req}_{NC}_Intake")
        else:
            problem += (constraint >= nutritional_requirements[NC][req],
                        f"{req}_{NC}_Intake")

#%% Execution and performance test
#Setting initial execution time, specifying solver and writing the problem
start_t = time.time()
solver = getSolver("PULP_CBC_CMD", msg = 0)
problem.writeLP("Diet.lp")

#Solves the problem
problem.solve(solver)
end_t = time.time()

#Prints execution time
print("Time of execution:",
      (end_t-start_t), "s")

#Prints solution status
print("Status:",
      LpStatus[problem.status])

#Specifies the solver used
print("Solver:",
      problem.solver)

#%% Problem log

#Write optimization problem specifications into an auxiliary text file
#problem_log = str(problem)

#with open("problem_log.txt","w") as f:
#    f.write(problem_log)

#%% Showing results and calculating overall dietary cost

#Storing and printing results
results = {v.name : v.varValue for v in problem.variables()}
df_results = pd.DataFrame.from_dict(results,
                                    orient="index",
                                    columns=["value"]).round(1)
print("Results: \n", df_results)

#Calculating and printing costs
cost = df_results["value"].to_numpy() * [products_cost[P] for P in products]
print("\nCost by product: ", cost)
print("Total Cost: ", cost.sum())