#%%

from api_connect.ons_api import OnsApi
from api_connect.boe_api import BoeApi
from api_connect.hmlr_api import HmlrApi
import pandas as pd

class DataBank:
    def __init__(self):
        self.registered_apis = {"ONS": OnsApi,
                                "BOE": BoeApi,
                                "HMLR": HmlrApi}
        self.data_log = []
        
    def __repr__(self):
        return str(self.registered_apis)
    
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
    
    def reset_log(self):
        self.data_log = []
    
# %%
