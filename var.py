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
]

#! Haven't found the prototype variable for VAR modelling.
BOE_VARS = [
    {"series_code": "IUMCCTL"},
    {"series_code": "LPMVZRE"},
    {"series_code": "IUMBX67"},
    {"series_code": "LPMBI2P"},
    # {"series_code": "IUDBEDR"}, # bank rate
]

HMLR_VARS = [
    # {"query_var": "percentageAnnualChange", "region": "united-kingdom"},
    # {"query_var": "averagePrice", "region": "united-kingdom"},
    # {"query_var": "housePriceIndex", "region": "united-kingdom"},
    {"query_var": "housePriceIndexSA", "region": "united-kingdom"},
]

dbs = DataBank()

boe_df = dbs.retrieve_data("BOE", BOE_VARS, "m")
ons_df = dbs.retrieve_data("ONS", ONS_VARS, "m")
hmlr_df = dbs.retrieve_data("HMLR", HMLR_VARS, "m")

df = pd.concat([ons_df, hmlr_df, boe_df], axis=1)
df = df.dropna()

#%%
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
    
    
def calc_udsc(df):
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


def calc_ukcig(df):
    """ Retrieve Corporate Income Gearing with the dataframe containing:
        - Total interest: UKEA/I6PK (ONS)
        - Total resource: UKEA/RPBN (ONS)
        - Taxes on income and wealth: UKEA/RPLA (ONS)
        
        Formula:
        $$ CIG = \frac{\text{Total Interest}}{(\text{Total resource} - \text{Taxes on income and wealth})} $$
    Args:
        df (pandas.DataFrame): pandas.DataFrame with specific macro variables.

    Returns:
        pandas.Series: UKCIG time-series.
    """
    macro_vars = ["I6PK", "RPBN", "RPLA"]
    compare_lists(macro_vars, df.columns)
    output = df["I6PK"] / (df["RPBN"] - df["RPLA"])
    return output.rename("UKCIG")    


#%%

df["UDSC"] = calc_udsc(df)
df["UDSC_SA"] = tsa.seasonal_adjustment(df["UDSC"], 12)
df["UKCIG"] = calc_ukcig(df)
df["UKCIG_SA"] = tsa.seasonal_adjustment(df["UKCIG"], 12)
df["ABMI"] = np.log(df["ABMI"])


#%%
md.cointegration_test(df)

# %%
tsa.ts_plot(df)
#%%
tsa.acf_pacf_plot(df)
#%%
tsa.adf_test(df)
#%%
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
