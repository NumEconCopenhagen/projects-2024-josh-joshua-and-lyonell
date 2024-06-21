from types import SimpleNamespace
import numpy as np
from scipy.optimize import minimize

class ExchangeEconomyClass:

    def __init__(self):

        par = self.par = SimpleNamespace()

        # a. preferences
        par.alpha = 1/3
        par.beta = 2/3

        # b. endowments
        par.w1A = 0.8
        par.w2A = 0.3

        #numeraire
        par.p2 = 1


    def utility_A(self,x1A,x2A):
        par = self.par
        utility = x1A**par.alpha * x2A**(1-par.alpha)
        return utility


    def utility_B(self,x1B,x2B):
        par = self.par
        utility = x1B**par.beta * x2B**(1-par.beta)
        return utility


    def demand_A(self,p1):
        par = self.par
        demand1 = par.alpha * (p1 * par.w1A + par.p2 * par.w2A)/ p1
        demand2 = (1-par.alpha) * (p1 * par.w1A + par.p2 * par.w2A)/ par.p2
        return demand1,demand2


    def demand_B(self,p1):
        par = self.par
        demand1 = par.beta * (p1 * (1-par.w1A) + par.p2 * (1-par.w2A))/ p1
        demand2 = (1-par.beta) * (p1 * (1-par.w1A) + par.p2 * (1-par.w2A))/ par.p2
        return demand1,demand2


    def check_market_clearing(self,p1):

        par = self.par

        x1A,x2A = self.demand_A(p1)
        x1B,x2B = self.demand_B(p1)

        eps1 = x1A-par.w1A + x1B-(1-par.w1A)
        eps2 = x2A-par.w2A + x2B-(1-par.w2A)

        return eps1,eps2

    def market_clearing(self, p1, omega_A):
        par = self.par
        p2 = par.p2
        xA_1 = par.alpha * (p1 * omega_A[0] + p2 * omega_A[1]) / p1
        xA_2 = (1 - par.alpha) * (p1 * omega_A[0] + p2 * omega_A[1]) / p2
        omega_B = [1 - omega_A[0], 1 - omega_A[1]]
        xB_1 = par.beta * (p1 * omega_B[0] + p2 * omega_B[1]) / p1
        xB_2 = (1 - par.beta) * (p1 * omega_B[0] + p2 * omega_B[1]) / p2
        return [xA_1 + xB_1 - 1, xA_2 + xB_2 - 1]

    def objective(self, p1, omega_A):
        par = self.par
        clearing_conditions = self.market_clearing(p1, omega_A)
        return np.sum(np.square(clearing_conditions))

    def find_equilibrium_allocations(self, num_samples):
        np.random.seed(42)  # For reproducibility
        omega_A = np.random.uniform(0, 1, (num_samples, 2))
        equilibrium_allocations = []

        for omega in omega_A:
            result = minimize(self.objective, x0=1, args=(omega,))
            if result.success:
                p1_eq = result.x[0]
                p2_eq = self.par.p2
                xA_1_eq = self.par.alpha * (p1_eq * omega[0] + p2_eq * omega[1]) / p1_eq
                xA_2_eq = (1 - self.par.alpha) * (p1_eq * omega[0] + p2_eq * omega[1]) / p2_eq
                equilibrium_allocations.append([xA_1_eq, xA_2_eq])
            else:
                print(f"Failed to find equilibrium for omega_A: {omega}")
                equilibrium_allocations.append([np.nan, np.nan])  # Mark failure

        # Remove invalid entries
        equilibrium_allocations = np.array(equilibrium_allocations)
        valid_allocations = equilibrium_allocations[~np.isnan(equilibrium_allocations).any(axis=1)]

        return valid_allocations