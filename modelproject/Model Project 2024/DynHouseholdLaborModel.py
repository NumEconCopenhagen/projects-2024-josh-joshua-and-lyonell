import numpy as np
from scipy.optimize import minimize,  NonlinearConstraint
import warnings
warnings.filterwarnings("ignore", message="delta_grad == 0.0. Check if the approximated function is linear.") # turn of annoying warning

from EconModel import EconModelClass

from consav.grids import nonlinspace
from consav.linear_interp import interp_2d

class DynHouseholdLaborModelClass(EconModelClass):

    def settings(self):
        """ fundamental settings """

        pass

    def setup(self):
        """ set baseline parameters """

        # unpack
        par = self.par

        par.T = 10 # time periods
        
        # preferences
        par.beta = 0.98 # discount factor
        par.mu = 0.5 # share of consumption in utility
        par.rho_1 = 0.05 # weight on labor dis-utility of men
        par.rho_2 = 0.05 # weight on labor dis-utility of women
        par.eta = -1.5 # CRRA coefficient
        par.gamma = 2.5 # curvature on labor hours 

        # income
        par.wage_const_1 = np.log(10_000.0) # constant, men
        par.wage_const_2 = np.log(10_000.0) # constant, women
        par.wage_K_1 = 0.1 # return on human capital, men
        par.wage_K_2 = 0.1 # return on human capital, women

        par.delta = 0.1 # depreciation in human capital

        # taxes
        #par.tax_scale = 2.278029 # from Borella et al. (2023), singles: 1.765038
        #par.tax_pow = 0.0861765 # from Borella et al. (2023), singles: 0.0646416

        par.lambda_joint = 2.28
        par.tau_joint = 0.0861765
        par.lambda_indiv = 1.75
        par.tau_indiv = 0.0646416

        # grids        
        par.k_max = 20.0 # maximum point in wealth grid
        par.Nk = 20 #30 # number of grid points in wealth grid    

        # simulation
        par.simT = par.T # number of periods
        par.simN = 1_000 # number of individuals

        # reform
        par.joint_tax = True

        #power share 
        par.mu = 0.5 # share of consumption in utility


    def allocate(self):
        """ allocate model """

        # unpack
        par = self.par
        sol = self.sol
        sim = self.sim

        par.simT = par.T
        
        # a. human capital grid
        par.k_grid = nonlinspace(0.0,par.k_max,par.Nk,1.1)

        # d. solution arrays
        shape = (par.T,par.Nk,par.Nk)
        sol.h1 = np.nan + np.zeros(shape)
        sol.h2 = np.nan + np.zeros(shape)
        sol.V = np.nan + np.zeros(shape)

        # e. simulation arrays
        shape = (par.simN,par.simT)
        sim.h1 = np.nan + np.zeros(shape)
        sim.h2 = np.nan + np.zeros(shape)
        sim.k1 = np.nan + np.zeros(shape)
        sim.k2 = np.nan + np.zeros(shape)
        
        sim.income1 = np.nan + np.zeros(shape)
        sim.income2 = np.nan + np.zeros(shape)

        # g. initialization
        #sim.k1_init = np.zeros(par.simN)
        #sim.k2_init = np.zeros(par.simN)
        sim.k1_init = np.full(par.simN, 2.0)  # Initialize k1 to 2 for all individuals
        sim.k2_init = np.zeros(par.simN)      # Initialize k2 to 0 for all individuals



    ############
    # Solution #
    def solve(self):

        # a. unpack
        par = self.par
        sol = self.sol
        
        # b. solve last period
        
        # c. loop backwards (over all periods)
        for t in reversed(range(par.T)):

            # i. loop over state variables: human capital for each household member
            for i_k1,capital1 in enumerate(par.k_grid):
                for i_k2,capital2 in enumerate(par.k_grid):
                    idx = (t,i_k1,i_k2)
                    
                    # ii. find optimal consumption and hours at this level of wealth in this period t.
                    if t==(par.T-1): # last period
                        obj = lambda x: -self.util(x[0],x[1],capital1,capital2)

                    else:
                        obj = lambda x: - self.value_of_choice(x[0],x[1],capital1,capital2,sol.V[t+1])  
                        

                    # call optimizer
                    bounds = [(0,np.inf) for i in range(2)]
                    
                    init_h = np.array([0.1,0.1])
                    if i_k1>0: 
                        init_h[0] = sol.h1[t,i_k1-1,i_k2]
                    if i_k2>0: 
                        init_h[1] = sol.h2[t,i_k1,i_k2-1]

                    res = minimize(obj,init_h,bounds=bounds) 
                    

                    # store results
                    sol.h1[idx] = res.x[0]
                    sol.h2[idx] = res.x[1]
                    sol.V[idx] = -res.fun
                    #print(f'{sol.V[idx]} for t = {t} and k1 = {capital1} and k2 = {capital2}')
 

    def value_of_choice(self,hours1,hours2,capital1,capital2,V_next):

        # a. unpack
        par = self.par

        # b. current utility
        util = self.util(hours1,hours2,capital1,capital2)
        
        # c. continuation value
        k1_next = (1.0-par.delta)*capital1 + hours1
        k2_next = (1.0-par.delta)*capital2 + hours2
        V_next = interp_2d(par.k_grid,par.k_grid,V_next,k1_next,k2_next)

        # d. return value of choice
        return util + par.beta*V_next


    # relevant functions
    def total_consumption(self,hours1,hours2,capital1,capital2):
        par = self.par

        income1 = self.wage_func(capital1,1) * hours1
        income2 = self.wage_func(capital2,2) * hours2
        income_hh = income1+income2

        if par.joint_tax:
            tax_hh = self.tax_joint(income_hh)
        else:
            tax_hh = self.tax_indiv(income1) + self.tax_indiv(income2)
        
        return income_hh - tax_hh


    def wage_func(self,capital,sex):
        # before tax wage rate
        par = self.par

        constant = par.wage_const_1
        return_K = par.wage_K_1
        if sex>1:
            constant = par.wage_const_2
            return_K = par.wage_K_2

        return np.exp(constant + return_K * capital)

    def tax_indiv(self,income):
        par = self.par

        rate = 1.0 - par.lambda_indiv*(income**(-par.tau_indiv))
        return rate*income
    
    def tax_joint(self,income):
        par = self.par

        rate = 1.0 - par.lambda_joint*(income**(-par.tau_joint))
        return rate*income

    def util(self,hours1,hours2,capital1,capital2):
        par = self.par

        cons = self.total_consumption(hours1,hours2,capital1,capital2)

        util_cons = (cons/2)**(1.0+par.eta) / (1.0+par.eta)
        util_hours1 = par.rho_1*(hours1)**(1.0+par.gamma) / (1.0+par.gamma)
        util_hours2 = par.rho_2*(hours2)**(1.0+par.gamma) / (1.0+par.gamma)

        return par.mu* (util_cons - util_hours1) + (1-par.mu)* (util_cons - util_hours2)
    
    def calculate_tax_revenue(self):
        # a. unpack
        par = self.par
        sol = self.sol
        sim = self.sim

        # b. initialize tax revenue array
        shape = (par.simT,)
        tax_revenue = np.zeros(shape)

        # c. loop over periods
        for t in range(par.simT):
            # i. loop over individuals
            for i in range(par.simN):
                # ii. calculate income for each individual
                income1 = self.wage_func(sim.k1[i, t], 1) * sim.h1[i, t]
                income2 = self.wage_func(sim.k2[i, t], 2) * sim.h2[i, t]

                # iii. calculate taxes paid by each individual
                if par.joint_tax:
                    tax_paid = self.tax_joint(income1 + income2)
                else:
                    tax_paid = self.tax_indiv(income1) + self.tax_indiv(income2)

                # iv. add taxes paid by the individual to total tax revenue
                tax_revenue[t] += tax_paid

        return tax_revenue

    ##############
    # Simulation #
    def simulate(self):

        # a. unpack
        par = self.par
        sol = self.sol
        sim = self.sim

        # b. loop over individuals and time
        for i in range(par.simN):

            # i. initialize states
            sim.k1[i,0] = sim.k1_init[i]
            sim.k2[i,0] = sim.k2_init[i]

            for t in range(par.simT):

                # ii. interpolate optimal hours
                idx_sol = t
                sim.h1[i,t] = interp_2d(par.k_grid,par.k_grid,sol.h1[idx_sol],sim.k1[i,t],sim.k2[i,t])
                sim.h2[i,t] = interp_2d(par.k_grid,par.k_grid,sol.h2[idx_sol],sim.k1[i,t],sim.k2[i,t])

                # store income
                sim.income1[i,t] = self.wage_func(sim.k1[i,t],1)*sim.h1[i,t]
                sim.income2[i,t] = self.wage_func(sim.k2[i,t],2)*sim.h2[i,t]

                # iii. store next-period states
                if t<par.simT-1:
                    sim.k1[i,t+1] = (1.0-par.delta)*sim.k1[i,t] + sim.h1[i,t]
                    sim.k2[i,t+1] = (1.0-par.delta)*sim.k2[i,t] + sim.h2[i,t]


                    


