
from src.optimizers import OptimizerBaseTemplate
from scipy.optimize import least_squares
from src.tools import math_tools
import numpy as np
from sklearn.metrics import r2_score


class NonLinearRegressor(OptimizerBaseTemplate):
    def __init__(self, optimizer_config, param_name_list):
        super(NonLinearRegressor, self).__init__(optimizer_config, param_name_list)
        print("Define and solve problem:")
        print("min sum of residuals")

    def func(self, c, X):
        func = (X[:, 0]*c[0])/c[3]+ (X[:, 1]*c[1])/c[3] + X[:, 2]*c[2]
        return func
    
    def _residuals(self, c, X, y):
        func = self.func(c, X)
        return y - func
    
    def bounds(self):
        # Bounds for parameters
        if "parameter_bounds" in self.config:
            lower_bounds = []
            upper_bounds = []
            param_bounds = self.config["parameter_bounds"]
            for key in param_bounds.keys():
                lower_bounds.append(param_bounds[key][0])
                upper_bounds.append(param_bounds[key][1])
        else:
            lower_bounds = [0, -np.inf, -np.inf, -np.inf]  
            upper_bounds = [np.inf, 0 , np.inf, np.inf] 
        
        return (lower_bounds, upper_bounds)
    
    def initial_guess(self):
        if "initial_guess" in self.config:
            initial_values = []
            initial_guess = self.config["initial_guess"]
            for key in initial_guess.keys():
                initial_values.append(initial_guess[key])
        else:
            initial_values = [0.1, -0.1, -1, 0.01]
        return initial_values

    def estimate_parameters(self, X, y):
        self.X = X
        self.y = y
        self.check_features()

        # Initial guess for parameters
        initial_guess = self.initial_guess()

        # Bounds for parameters
        bounds = self.bounds()

        print('=== INITIAL', initial_guess)
        print('=== BOUNDS', bounds)

        # Perform non-linear least squares fit
        self.result = least_squares(self._residuals, initial_guess, bounds = bounds,  args=(self.X, self.y))

        self.coeff = np.array(self.result.x)
        #self.params_ = self.result.x
        self.estimation_completed = True

    def get_optimization_parameters(self):
        self.check_estimation_completed()
        return list(self.coeff)

    def set_optimal_coefficients(self, c_opt, X, y):
        self.X = X
        self.y = y
        self.coeff = np.array(c_opt)
        self.estimation_completed = True

    def predict(self, X_pred):
        self.check_estimation_completed()
        return self.func(self.coeff, X_pred) #X_pred.dot(self.result.x)
    
    def compute_optimization_metrics(self):
        self.check_estimation_completed()
        y_pred = self.predict(self.X)
        metrics_dict = {
            "R2": float(r2_score(y_pred, self.y)),
            "RMSE": math_tools.rmse_between_numpy_arrays(y_pred, self.y),
        }
        return metrics_dict
