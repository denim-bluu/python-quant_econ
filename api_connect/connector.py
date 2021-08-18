#%%

from api_connect.ons_api import OnsApi
from api_connect.boe_api import BoeApi
from api_connect.hmlr_api import HmlrApi
import pandas as pd

# # Single instance examples.
# a = OnsApi("QNA", "ABMI")
# b = BoeApi("LPMVQJW")
# c = HmlrApi("housePriceIndex")
# Collated example.

# # Multiple instances examples.
# ONS_VARS = [
#     {"dataset_id": "LMS", "timeseries_id": "MGSX"},
#     {"dataset_id": "PN2", "timeseries_id": "ABMI"},
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

class DataBank:
    def __init__(self):
        self.registered_apis = {}
        self.data_log = []
        
    def __repr__(self) -> str:
        pass
    
    def register_api(self, api_name, api_obj):
        self.registered_apis[api_name] = api_obj
        
    @staticmethod
    def _check_date_interval(date_interval):
        if date_interval not in ["m", "q", "y"]:
            raise ValueError("Date interval input should be: m / q / y.")
        
    def retrieve_data(self, api_name, api_params, date_interval):
        self._check_date_interval(date_interval)
        dfs = []
        api_obj = self.registered_apis[api_name]
        for params in api_params:
            _api_obj = api_obj(**params)
            dfs.append(_api_obj.get_time_series(date_interval))
            self.data_log.append(repr(_api_obj))
        return pd.concat(dfs, axis=1)
    
        
db_connector = DataBank()
db_connector.register_api("ONS", OnsApi)
db_connector.register_api("BOE", BoeApi)
db_connector.register_api("HMLR", HmlrApi)
