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
Production planning optimization problem.

Goal: Given three products p1, p2 and p3 and their respective selling prices,
we aim at maximizing the profit whilst respecting the constraints of the production machines.

Scenario: Suppose there are two machines m1 and m2, each with its own specific production times (min) for 
any given product and total time capacity (min) per day. Each product must be processed by both machines irrespective of the order.
Given these constraints and the selling prices of the three aforementioned products, we want to determine how much of 
each product we should be producing daily and the estimated profits given these quantities.
"""
)

#Products list
products = [
    "Product_1",
    "Product_2",
    "Product_3"
]

products_prices = {
    "Product_1": 5,
    "Product_2": 3.5,
    "Product_3": 4.5
}

machine_times = {
    "Machine_1": {
        "Prod_times": {
            "Product_1": 3,
            "Product_2": 5,
            "Product_3": 4
            },
        "Time_capacity": 540
    },
    "Machine_2": {
        "Prod_times": {
            "Product_1": 6,
            "Product_2": 1,
            "Product_3": 3
            },
        "Time_capacity": 480
    }
}


#Variables definition
vars = LpVariable.dicts("Quantity",
                 [P for P in products],              
                  lowBound = 0, #Lowbound is set to avoid negative production quantities
                  cat = "Continuous") #Variables are continuous

#Objective function definition: we aim at maximizing profit which is the sum over all products of product quantity times price
objective = lpSum([vars[P] * products_prices[P] for P in products])

#Defines the problem
problem = LpProblem("Production_Planning",
                    sense = LpMaximize)

problem += (objective, "Objective")

#%% Constraints definition

#Creating machine 1 and 2 constraints: 

for M in machine_times.keys():
    constraint = None

    for P in machine_times[M]["Prod_times"].keys():
        constraint += vars[P] * machine_times[M]["Prod_times"][P]

    problem += (constraint <= machine_times[M]["Time_capacity"],
                f"Machine_times_M_{M}")

#%% Execution and performance test
#Setting initial execution time, specifying solver and writing the problem
start_t = time.time()
solver = getSolver("PULP_CBC_CMD", msg = 0)
problem.writeLP("Production_Planning.lp")

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

#%% Showing results and calculating profits

#Storing and printing results
results = {v.name : v.varValue for v in problem.variables()}
df_results = pd.DataFrame.from_dict(results,
                                    orient="index",
                                    columns=["value"])
print("Results: \n", df_results)

#Calculating and printing profits
products_profit = df_results["value"].to_numpy() * [products_prices[P] for P in products]
print("\nProfit by product: ", products_profit)
print("Total Profit: ", products_profit.sum())