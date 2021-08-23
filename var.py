# %%
import pandas as pd
import model_diagnos as md
import numpy as np
import ts_analysis as tsa

import statsmodels.api as sm
from api_connect.connector import db_connector

# %%
# Multiple instances examples.
ONS_VARS = [
    {"dataset_id": "LMS", "timeseries_id": "MGSX"},
    {"dataset_id": "PN2", "timeseries_id": "ABMI"},
    {"dataset_id": "UKEA", "timeseries_id": "RPHQ"},
]

#! Haven't found the prototype variable for VAR modelling.
BOE_VARS = [
    {"series_code": "IUMCCTL"},
    {"series_code": "LPMVZRE"},
    {"series_code": "IUMBX67"},
    {"series_code": "LPMBI2P"},
]

HMLR_VARS = [
    # {"query_var": "percentageAnnualChange", "region": "united-kingdom"},
    # {"query_var": "averagePrice", "region": "united-kingdom"},
    # {"query_var": "housePriceIndex", "region": "united-kingdom"},
    {"query_var": "housePriceIndexSA", "region": "united-kingdom"},
]

dbs = db_connector

boe_df = dbs.retrieve_data("BOE", BOE_VARS, "m")
ons_df = dbs.retrieve_data("ONS", ONS_VARS, "m")
hmlr_df = dbs.retrieve_data("HMLR", HMLR_VARS, "m")

df = pd.concat([ons_df, hmlr_df, boe_df], axis=1)
df = df.dropna()

#%%
# Data pre-processing
def cal_udsc_series(df):
    """ Retrieve Unsecured Debt Servicing Cost with the dataframe containing:
        - Card int rate: IUMCCTL (BOE)
        - Card bal: LPMVZRE (BOE)
        - Loans int rate: IUMBX67 (BOE)
        - Total Unsec bal: LPMBI2P (BOE)
        - Disposable income: RPHQ (ONS)
        
        Formula:
        $$ UDSC = 100*\frac{\text{Card int rate} * \text{Card bal}+(\text{Loans int rate * (\text{Total Unsec bal} - \text{Card bal})})}{\text{Disposable Income}} $$

    Args:
        df (pd.DataFrame): pandas.DataFrame with specific macro variables.

    Returns:
        [type]: [description]
    """
    macro_vars = ["IUMCCTL", "LPMVZRE", "IUMBX67", "LPMBI2P", "RPHQ"]
    if not set(macro_vars) <= set(df.columns):
        req_vars = set(macro_vars).difference(set(df.columns))
        raise ValueError(f"Missing: {req_vars}")
    
    denom1 = df["IUMCCTL"].divide(100) * df["LPMVZRE"]
    denom2 = df["IUMBX67"].divide(100) * (df["LPMBI2P"] - df["LPMVZRE"])
    output = 100 * (denom1 + denom2) / df["RPHQ"]
    return output.rename("UDCS")


#%%

df["UDSC"] = cal_udsc_series(df)
df["UDSC_SA"] = tsa.seasonal_adjustment(df)
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
