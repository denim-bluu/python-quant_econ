#%%
import numpy as np
import pandas as pd

df = pd.read_csv("/Users/anko/Downloads/T8-svar/za_dat1.csv")
df_mat = df.to_numpy()
# %%
def lag_matrix(mat, p):
    lag_mats = [mat[i : -p + i] for i in reversed(range(p))]
    return np.hstack(lag_mats)


def design_matrix(mat, intercept=True):
    if intercept:
        return np.hstack((mat, np.ones((mat.shape[0], 1))))
    else:
        return mat


class VectorAR:
    def __init__(self, data, p, exog_names, reg_type="const", intercept=True):
        self.p = p
        self.intercept = True
        self.reg_type = "const"
        self.exog_names = exog_names

        self.orig_data = data.copy()
        self.n_obs, self.k = data.shape
        self.n_sample = self.n_obs - p
        self.y_dep = data[p:]
        self.y_exog = design_matrix(lag_matrix(data, p))

    def _format_coefs(self):
        col_names = [self.exog_names + f"l{lag+1}" for lag in range(p)]
        if self.intercept:
            col_names = [*self.exog_names, "Intercept"]
        else:
            col_names = self.exog_names
        return pd.DataFrame(self.coefs, columns=col_names, index=self.exog_names)
        
    def fit(self):
        Y = self.y_dep.T
        X = self.y_exog.T
        self.coefs = (Y @ X.T) @ np.linalg.inv(X @ X.T)
        self.eps = Y - self.coefs @ X
        self.dof = self.n_obs - self.p - self.p * self.k - self.intercept
        self.sigma = (self.eps@ self.eps.T)/ self.dof
        
    def summary(self):
        return self._format_coefs()
    

a = VectorAR(df_mat, exog_names=df.columns, p=1)
a.fit()
a.summary()
# %%
