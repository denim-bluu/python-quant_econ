# %%
import model_diagnos as md
import numpy as np
import ts_analysis as tsa
import pandas as pd
import statsmodels.api as sm
from api_connect.connector import db_connector

# %%
# Multiple instances examples.
ONS_VARS = [
    {"dataset_id": "LMS", "timeseries_id": "MGSX"},
    {"dataset_id": "PN2", "timeseries_id": "ABMI"},
]

#! Haven't found the prototype variable for VAR modelling.
# BOE_VARS = [{"series_code": "LPQB4TC"}]

HMLR_VARS = [
    # {"query_var": "percentageAnnualChange", "region": "united-kingdom"},
    # {"query_var": "averagePrice", "region": "united-kingdom"},
    {"query_var": "housePriceIndex", "region": "united-kingdom"},
    # {"query_var": "housePriceIndexSA", "region": "united-kingdom"},
]

# boe_df = db_connector.retrieve_data("BOE", BOE_VARS, "q")
ons_df = db_connector.retrieve_data("ONS", ONS_VARS, "q")
hmlr_df = db_connector.retrieve_data("HMLR", HMLR_VARS, "q")

df = pd.concat([ons_df, hmlr_df], axis=1)
df["ABMI"] = np.log(df["ABMI"])
df = df.pct_change().dropna()

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
