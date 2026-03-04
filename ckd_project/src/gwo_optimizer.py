"""
Grey Wolf Optimizer (GWO) Module
=================================
Implements the Grey Wolf Optimization algorithm for hyperparameter tuning
of SVR regression models, as described in:

    Mirjalili, S., Mirjalili, S.M., Lewis, A. (2014). 
    "Grey Wolf Optimizer." Advances in Engineering Software, 69, 46–61.

The optimizer finds the best combination of (C, epsilon, gamma) for SVR
by minimizing the RMSE on a validation set.
"""

import numpy as np
from sklearn.svm import SVR
from sklearn.metrics import mean_squared_error
import time


class GreyWolfOptimizer:
    """
    Grey Wolf Optimizer (GWO).
    
    Mimics the hunting behaviour of grey wolves with a social hierarchy:
    Alpha (α) – best solution, Beta (β) – 2nd best, Delta (δ) – 3rd best.
    Remaining wolves (ω) follow α, β, δ to converge on the prey (optimum).

    Parameters
    ----------
    objective_function : callable
        Function to minimize. Takes a 1D array of parameters, returns scalar.
    dim : int
        Number of dimensions (hyperparameters).
    lb, ub : array-like
        Lower and upper bounds for each dimension.
    n_wolves : int
        Pack size (population).
    max_iter : int
        Maximum number of iterations.
    verbose : bool
        Print progress during optimization.
    """

    def __init__(self, objective_function, dim, lb, ub,
                 n_wolves=30, max_iter=20, verbose=True):
        self.objective_function = objective_function
        self.dim = dim
        self.lb = np.array(lb, dtype=float)
        self.ub = np.array(ub, dtype=float)
        self.n_wolves = n_wolves
        self.max_iter = max_iter
        self.verbose = verbose
        self.convergence_curve = []

    def optimize(self):
        """
        Run GWO optimization.

        Returns
        -------
        alpha_pos : ndarray
            Best parameters found.
        alpha_score : float
            Best objective value (lowest RMSE).
        """
        # Initialize wolf positions randomly within bounds
        positions = np.random.uniform(
            low=self.lb, high=self.ub,
            size=(self.n_wolves, self.dim)
        )

        # Hierarchy leaders
        alpha_pos = np.zeros(self.dim)
        alpha_score = float('inf')
        beta_pos = np.zeros(self.dim)
        beta_score = float('inf')
        delta_pos = np.zeros(self.dim)
        delta_score = float('inf')

        start_time = time.time()

        for t in range(self.max_iter):
            # --- Evaluate all wolves ---
            for i in range(self.n_wolves):
                fitness = self.objective_function(positions[i])

                # Update hierarchy
                if fitness < alpha_score:
                    delta_score = beta_score
                    delta_pos = beta_pos.copy()
                    beta_score = alpha_score
                    beta_pos = alpha_pos.copy()
                    alpha_score = fitness
                    alpha_pos = positions[i].copy()
                elif fitness < beta_score:
                    delta_score = beta_score
                    delta_pos = beta_pos.copy()
                    beta_score = fitness
                    beta_pos = positions[i].copy()
                elif fitness < delta_score:
                    delta_score = fitness
                    delta_pos = positions[i].copy()

            # --- Update coefficient 'a' (linearly decreasing from 2 to 0) ---
            a = 2.0 - t * (2.0 / self.max_iter)

            # --- Update all wolf positions ---
            for i in range(self.n_wolves):
                for j in range(self.dim):
                    # Encircle α
                    r1, r2 = np.random.random(2)
                    A1 = 2 * a * r1 - a
                    C1 = 2 * r2
                    D_alpha = abs(C1 * alpha_pos[j] - positions[i, j])
                    X1 = alpha_pos[j] - A1 * D_alpha

                    # Encircle β
                    r1, r2 = np.random.random(2)
                    A2 = 2 * a * r1 - a
                    C2 = 2 * r2
                    D_beta = abs(C2 * beta_pos[j] - positions[i, j])
                    X2 = beta_pos[j] - A2 * D_beta

                    # Encircle δ
                    r1, r2 = np.random.random(2)
                    A3 = 2 * a * r1 - a
                    C3 = 2 * r2
                    D_delta = abs(C3 * delta_pos[j] - positions[i, j])
                    X3 = delta_pos[j] - A3 * D_delta

                    # Update position (mean of three encirclement positions)
                    positions[i, j] = (X1 + X2 + X3) / 3.0

                    # Enforce bounds
                    positions[i, j] = np.clip(positions[i, j], self.lb[j], self.ub[j])

            self.convergence_curve.append(alpha_score)

            if self.verbose and (t % 5 == 0 or t == self.max_iter - 1):
                elapsed = time.time() - start_time
                print(f"  [GWO] Iter {t+1:3d}/{self.max_iter} | "
                      f"Best RMSE = {alpha_score:.4f} | a = {a:.3f} | "
                      f"Time: {elapsed:.1f}s")

        return alpha_pos, alpha_score


def optimize_svr_with_gwo(X_train, y_train, X_val, y_val,
                           n_wolves=20, max_iter=15):
    """
    Optimize SVR hyperparameters (C, epsilon, gamma) using GWO.

    Parameters
    ----------
    X_train, y_train : training data
    X_val, y_val : validation data
    n_wolves : int
    max_iter : int

    Returns
    -------
    best_params : ndarray [C, epsilon, gamma]
    best_score : float (RMSE)
    """
    print("\n" + "="*60)
    print("GWO-SVR HYPERPARAMETER OPTIMIZATION")
    print("="*60)
    print(f"  Wolves: {n_wolves} | Iterations: {max_iter}")
    print(f"  Search space: C ∈ [0.1, 100], ε ∈ [0.01, 1], γ ∈ [0.001, 1]")

    def objective(params):
        C, epsilon, gamma = params
        try:
            svr = SVR(C=C, epsilon=epsilon, gamma=gamma, kernel='rbf')
            svr.fit(X_train, y_train)
            y_pred = svr.predict(X_val)
            return np.sqrt(mean_squared_error(y_val, y_pred))
        except Exception:
            return float('inf')

    gwo = GreyWolfOptimizer(
        objective_function=objective,
        dim=3,
        lb=[0.1, 0.01, 0.001],
        ub=[100.0, 1.0, 1.0],
        n_wolves=n_wolves,
        max_iter=max_iter,
        verbose=True,
    )

    best_params, best_score = gwo.optimize()

    print(f"\n  ✓ Best SVR Parameters Found:")
    print(f"    C       = {best_params[0]:.4f}")
    print(f"    epsilon = {best_params[1]:.4f}")
    print(f"    gamma   = {best_params[2]:.4f}")
    print(f"    RMSE    = {best_score:.4f}")

    return best_params, best_score, gwo.convergence_curve
