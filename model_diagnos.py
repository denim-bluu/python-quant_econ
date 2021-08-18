import pandas as pd
import numpy as np
import statsmodels.api as sm
from matplotlib import pyplot as plt
import seaborn as sns
from statsmodels.tsa.vector_ar.vecm import coint_johansen


def grangers_causation_matrix(df, test="ssr_chi2test", verbose=False):
    """Check Granger Causality of all possible combinations of the Time series.
    The rows are the response variable, columns are predictors. The values in the table 
    are the P-Values. P-Values lesser than the significance level (0.05), implies 
    the Null Hypothesis that the coefficients of the corresponding past values is 
    zero, that is, the X does not cause Y can be rejected.

    Note:
        If a given p-value is < significance level (0.05), then, the corresponding X series (column) causes the Y (row).
    Args:
        df (pd.DataFrame): pd.DataFrame containing the time series variables.
        vars (list): list containing names of the time series variables.
        test (str, optional): Test method. Defaults to 'ssr_chi2test'.
        verbose (bool, optional): Print results. Defaults to False.

    Returns:
        pd.DataFrame: Granger causality test statistics.
    """
    vars = df.columns
    output = pd.DataFrame(np.zeros((len(vars), len(vars))), columns=vars, index=vars)
    for c in output.columns:
        for r in output.index:
            test_result = sm.tsa.stattools.grangercausalitytests(
                df[[r, c]], maxlag=maxlag, verbose=False
            )
            p_values = [round(test_result[i + 1][0][test][1], 4) for i in range(maxlag)]
            if verbose:
                print(f"Y = {r}, X = {c}, P Values = {p_values}")
            min_p_value = np.min(p_values)
            output.loc[r, c] = min_p_value
    output.columns = [var + "_x" for var in vars]
    output.index = [var + "_y" for var in vars]
    return output


def cointegration_test(df: pd.DataFrame, alpha: float = 0.05):
    """ Perform Johanson's Cointegration Test and Report Summary.

    Note:
        Using Trace statistics.
    
    Args:
        df (pd.DataFrame): pd.DataFrame containing the time series variables.
        alpha (float, optional): [description]. Defaults to 0.05.

    Returns:
        pd.DataFrame: Cointegration test statistics.
    """
    res = coint_johansen(df, -1, 5)
    d = {"0.90": 0, "0.95": 1, "0.99": 2}
    traces = res.lr1
    cvts = res.cvt[:, d[str(1 - alpha)]]
    res_dict = {
        "Variable": df.columns,
        "Test statistic": traces,
        f"CV {str(1-alpha)}%": cvts,
        "Conclusion": cvts < traces,
    }
    return pd.DataFrame(res_dict)


class PostModelDiagnostic:
    def __init__(self, results):
        """

        Args:
            results (Statsmodels.results): Statsmodels results.
        """
        self.results = results

    def serial_corr_resid(self, variable: str):
        """ Residual serial correlation diagnostics.

        Args:
            variable (str): Variable name.

        Returns:
            figure: Residual serial correlation diagnostics plots.
        """
        resid = self.results.resid[variable]
        fig, axs = plt.subplots(3, 2)

        axs[0, 0].plot(resid.index, resid)
        axs[0, 0].set_title(f"Residual plot of {variable}")

        sns.kdeplot(resid, ax=axs[0, 1])
        axs[0, 1].set_title(f"KDE of Residuals: {variable}")

        sm.graphics.tsa.plot_acf(resid, ax=axs[1, 0])
        axs[1, 0].set_title(f"ACF of Residuals: {variable}")

        sm.graphics.tsa.plot_pacf(resid, ax=axs[2, 0])
        axs[2, 0].set_title(f"PACF of Residuals: {variable}")

        sm.graphics.tsa.plot_acf(np.square(resid), ax=axs[1, 1])
        axs[1, 1].set_title(f"ACF of Squared Residuals: {variable}")

        sm.graphics.tsa.plot_pacf(np.square(resid), ax=axs[2, 1])
        axs[2, 1].set_title(f"PACF of Squared Residuals: {variable}")
        plt.tight_layout()
        plt.close()
        return fig

    def normality_test(self):
        return self.results.test_normality().summary()

    def durbin_watson(self):
        return sm.stats.durbin_watson(self.results.resid)

    def whiteness_test(self):
        return self.results.test_whiteness().summary()
