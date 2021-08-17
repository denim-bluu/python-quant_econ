from ons_api import OnsApi
from boe_api import BoeApi
from hmlr_api import HmlrApi
import pandas as pd

# # Single instance examples.
# a = OnsApi("QNA", "ABMI")
# b = BoeApi("LPMVQJW")
# c = HmlrApi("housePriceIndex")
# Collated example.

# # Multiple instances examples.
# ONS_VARS = [
#     {"dataset_id": "LMS", "timeseries_id": "MGSX"},
#     {"dataset_id": "QNA", "timeseries_id": "ABMI"},
# ]
# BOE_VARS = [{"series_code": "XUDLUSS"}, {"series_code": "LPMVQJW"}]

# HMLR_VARS = [
#     {"query_var": "percentageAnnualChange", "region": "united-kingdom"},
#     {"query_var": "averagePrice", "region": "united-kingdom"},
#     {"query_var": "housePriceIndex", "region": "united-kingdom"},
#     {"query_var": "housePriceIndexSA", "region": "united-kingdom"},
# ]

# ons = retrieve_data(OnsApi, ONS_VARS, "months")
# boe = retrieve_data(BoeApi, BOE_VARS, "months")
# hmlr = retrieve_data(HmlrApi, HMLR_VARS, "months")


def retrieve_data(api_obj, inputs, date_interval):
    dfs = []
    for params in inputs:
        _api_obj = api_obj(**params)
        dfs.append(_api_obj.get_ts(date_interval))
    return pd.concat(dfs, axis=1)


