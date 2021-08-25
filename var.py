# %%
import pandas as pd
import model_diagnos as md
import numpy as np
import ts_analysis as tsa

import statsmodels.api as sm
from api_connect.connector import DataBank

# %%
# Multiple instances examples.
ONS_VARS = [
    {"dataset_id": "LMS", "timeseries_id": "MGSX"},
    {"dataset_id": "PN2", "timeseries_id": "ABMI"},
    {"dataset_id": "UKEA", "timeseries_id": "RPHQ"},
    {"dataset_id": "UKEA", "timeseries_id": "I6PK"},
    {"dataset_id": "UKEA", "timeseries_id": "RPBN"},
    {"dataset_id": "UKEA", "timeseries_id": "RPLA"},
    {"dataset_id": "UKEA", "timeseries_id": "NLBC"},
    {"dataset_id": "UKEA", "timeseries_id": "NKZA"},
    {"dataset_id": "MM23", "timeseries_id": "D7BT"},
    {"dataset_id": "LMS", "timeseries_id": "MGSX"},
    {"dataset_id": "PN2", "timeseries_id": "YBHA"},
    {"dataset_id": "UKEA", "timeseries_id": "ROYJ"},
    {"dataset_id": "UKEA", "timeseries_id": "ROYH"},
    {"dataset_id": "UKEA", "timeseries_id": "ROYK"},
    {"dataset_id": "UKEA", "timeseries_id": "RPQK"},
]

BOE_VARS = [
    {"series_code": "IUMCCTL"},
    {"series_code": "LPMVZRE"},
    {"series_code": "IUMBX67"},
    {"series_code": "LPMBI2P"},
    {"series_code": "IUDBEDR"},
]

HMLR_VARS = [
    # {"query_var": "percentageAnnualChange", "region": "united-kingdom"},
    # {"query_var": "averagePrice", "region": "united-kingdom"},
    # {"query_var": "housePriceIndex", "region": "united-kingdom"},
    {"query_var": "housePriceIndexSA", "region": "united-kingdom"},
]

dbs_q = DataBank()
dbs_m = DataBank()

boe_df = dbs_q.retrieve_data("BOE", BOE_VARS, "q")
ons_df = dbs_q.retrieve_data("ONS", ONS_VARS, "q")
hmlr_df = dbs_q.retrieve_data("HMLR", HMLR_VARS, "q")

boe_df_m = dbs_m.retrieve_data("BOE", BOE_VARS, "m")
ons_df_m = dbs_m.retrieve_data("ONS", ONS_VARS, "m")
hmlr_df_m = dbs_m.retrieve_data("HMLR", HMLR_VARS, "m")

df_q = pd.concat([ons_df, hmlr_df, boe_df], axis=1)
df_q = df_q.dropna()
df_m = pd.concat([ons_df_m, hmlr_df_m, boe_df_m], axis=1)
df_m = df_m.dropna()

# %%
# Data pre-processing


def compare_lists(list1, list2):
    """ Check if list1 is a subset of list 2. If not, raise an error.


    Args:
        list1 (list): A subset list.
        list2 (list): A comparable list.

    Raises:
        ValueError: A list of variables missing in list2 from list1
    """
    if not set(list1) <= set(list2):
        req_vars = set(list1).difference(set(list2))
        raise ValueError(f"Missing: {req_vars}")


def udsc_ts(df):
    """ Retrieve Unsecured Debt Servicing Cost with the dataframe containing:
        - Card int rate: IUMCCTL (BOE)
        - Card bal: LPMVZRE (BOE)
        - Loans int rate: IUMBX67 (BOE)
        - Total Unsec bal: LPMBI2P (BOE)
        - Disposable income: RPHQ (ONS)

        Formula:
        $$ UDSC = 100*\frac{\text{Card int rate} * \text{Card bal}+(\text{Loans int rate * (\text{Total Unsec bal} - \text{Card bal})})}{\text{Disposable Income}} $$

    Args:
        df (pandas.DataFrame): pandas.DataFrame with specific macro variables.

    Returns:
        pandas.Series: USDC time-series.
    """
    macro_vars = ["IUMCCTL", "LPMVZRE", "IUMBX67", "LPMBI2P", "RPHQ"]
    compare_lists(macro_vars, df.columns)

    denom1 = df["IUMCCTL"].divide(100) * df["LPMVZRE"]
    denom2 = df["IUMBX67"].divide(100) * (df["LPMBI2P"] - df["LPMVZRE"])
    output = 100 * (denom1 + denom2) / df["RPHQ"]
    return output.rename("UDCS")


def uk_cig_ts(df):
    """ Retrieve UK Corporate Income Gearing with the dataframe containing:
        - Total interest: UKEA/I6PK (ONS)
        - Total resource: UKEA/RPBN (ONS)
        - Taxes on income and wealth: UKEA/RPLA (ONS)

        Formula:
        $$ CIG = \frac{\text{Total Interest}}{(\text{Total resource} - \text{Taxes on income and wealth})} $$
    Args:
        df (pandas.DataFrame): pandas.DataFrame with specific macro variables.

    Returns:
        pandas.Series: UK CIG time-series.
    """
    macro_vars = ["I6PK", "RPBN", "RPLA"]
    compare_lists(macro_vars, df.columns)
    output = df["I6PK"] / (df["RPBN"] - df["RPLA"])
    return output.rename("UKCIG")


def uk_corp_profits_ts(df):
    """ Retrieve UK Corporate Profits with the dataframe containing:
        - PN2/YBHA (ONS)
        - UKEA/ROYJ (ONS)
        - UKEA/ROYH (ONS)
        - UKEA/ROYK (ONS)

        Formula:
        $$ \text{Corporate Profits} = \text{Nominal GDP} - \text{Pre-tax labour income} $$
    Args:
        df (pandas.DataFrame): pandas.DataFrame with specific macro variables.

    Returns:
        pandas.Series: UK Corporate Profits time-series.
    """
    macro_vars = ["YBHA", "ROYJ", "ROYH", "ROYK"]
    compare_lists(macro_vars, df.columns)
    output = df["YBHA"] - df["ROYJ"] + df["ROYH"] - df["ROYK"]
    return output.rename("UKCPROF")


def ts_yoy_pct_change(t_series):
    """ Calculate Year on Year percentage difference.

    Args:
        t_series (pandas.Series): Time-series object.

    Raises:
        TypeError: If the input is not pandas.Series with date index.

    Returns:
        pandas.Series: YoY percentage change series. 
    """
    if t_series.index.inferred_type != "datetime64":
        raise TypeError("Please submit the series with datetime index.")

    freq = pd.infer_freq(t_series.index).lower()
    intervals = {"m": 12, "q": 4, "y": 1}
    output = t_series / t_series.shift(intervals[freq]) - 1
    return output.rename(t_series.name + "_YOY")


def ts_log(t_series):
    return np.log(t_series)


def ts_first_diff(t_series):
    return t_series - t_series.shift(1)


class PreProcessPipe:
    def __init__(self):
        self.steps = []

    def add_preprocess_step(self, function):
        self.steps.append(function)

    def show_steps(self):
        for i, func in enumerate(self.steps):
            print(f"Step {i}: {func.__name__}")

    def apply_preprocess(self, t_series):
        if not self.steps:
            raise AttributeError("Pre-process step is None.")

        for func in self.steps:
            t_series = func(t_series)

        return t_series


# %%
df_m["UDSC"] = udsc_ts(df_m)
df_m["UDSC_SA"] = tsa.seasonal_adjustment(df_m["UDSC"], 12)
df_m["UKCIG"] = uk_cig_ts(df_m)
df_m["UKCIG_SA"] = tsa.seasonal_adjustment(df_m["UKCIG"], 12)
df_m["UKCPROF"] = uk_corp_profits_ts(df_m)
df_m["UKCPROF_SA"] = tsa.seasonal_adjustment(df_m["UKCPROF"], 12)

df = df_q[["ABMI", "D7BT", "IUDBEDR"]]
df = df.apply(np.log)
df = df.diff().dropna()

# %%
md.cointegration_test(df)

# %%
tsa.ts_plot(df)
# %%
tsa.acf_pacf_plot(df, lags=20)
# %%
tsa.adf_test(df)
# %%
tsa.seasonal_decomp(df, 4)
# %%
model = sm.tsa.VAR(df)
order_df = model.select_order(15).summary()
results = model.fit(maxlags=15, ic="aic")
# results = model.fit(2)
# %%
irf = results.irf(40)
irf.plot()
fevd = results.fevd(5)
fevd.plot()
# %%
diagnos = md.PostModelDiagnostic(results)
diagnos.durbin_watson()
diagnos.normality_test()
diagnos.whiteness_test()
diagnos.serial_corr_resid("MGSX")
diagnos.serial_corr_resid("ABMI")
diagnos.serial_corr_resid("housePriceIndex")


# %%

# %%