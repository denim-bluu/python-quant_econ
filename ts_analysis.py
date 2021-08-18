# %%
from matplotlib import pyplot as plt
import pandas as pd
import statsmodels.api as sm

def ts_plot(df):
    """ Time-series plot(s).

    Returns:
        figure: Time-series plots.
    """
    n_cols = df.shape[1]
    fig, axs = plt.subplots(n_cols, sharex=True)
    for id, ax in enumerate(axs):
        ax.plot(df.index, df.iloc[:, id])
        ax.set_title(df.columns[id])
    plt.tight_layout()
    plt.close()
    return fig

def acf_pacf_plot(df, lags: int = 40):
    """ ACF / PACF plot(s).

    Args:
        lags (int): Number of lags.

    Returns:
        figure: ACF / PACF plots.
    """
    n_cols = df.shape[1]
    fig, axs = plt.subplots(2, n_cols, sharex=True)
    for i in range(axs.shape[1]):
        sm.graphics.tsa.plot_acf(
            df.iloc[:, i],
            lags=lags,
            ax=axs[0, i],
            title=f"{df.columns[i]} ACF",
        )
        sm.graphics.tsa.plot_pacf(
            df.iloc[:, i],
            lags=lags,
            ax=axs[1, i],
            title=f"{df.columns[i]} PACF",
        )
    plt.tight_layout()
    plt.close()
    return fig

def adf_test(df, regression="c", ci=0.05):
    """ Augmented Dickey Fuller test for unit root.

    Args:
        regression (str): Constant and trend order to include in regression.
        ci (float, optional): Confidence interval for test conclusion. Defaults to 0.05.

    Returns:
        pd.DataFrame: Test statistic.
    """
    if ci not in [0.01, 0.05, 0.1]:
        raise ValueError(
            f"ci input should be either 0.01, 0.05, 0.1. Selected ci is {ci}."
        )
    output = []
    ci = int(ci * 100)
    for col in df.columns:
        res = sm.tsa.adfuller(df[col], regression=regression, autolag="AIC")
        hypot_test = True if res[4].get(f"{ci}%") > res[0] else False
        res_dict = {
            "Variable": col,
            "ADF statistic": res[0],
            "n_lags": res[2],
            "p-value": res[1],
            f"CV {ci}%": res[4].get(f"{ci}%"),
            "Conclusion": hypot_test,
        }
        output.append(res_dict)
    return pd.DataFrame(output)

def seasonal_decomp(df, period, model: str = "additive"):
    for var in df.columns:
        try:
            res = sm.tsa.seasonal_decompose(df[var], model=model, period=period)
            res.plot()
        except:
            print(f"Variable: {var} faced an error. Please conduct the decomposition separately for debugging.")