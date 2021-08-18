#%%
import io
import pandas as pd
import requests


class BoeApi:
    def __init__(self, series_code):
        self.series_code = series_code
        self.endpoint = (
            "https://www.bankofengland.co.uk/boeapps/iadb/fromshowcolumns.asp?csv.x=yes"
        )
        self.date_freq = None
        self.interporlated = None
        self._get_content()
        
    def __repr__(self):
        api = "API: BOE"
        series = f"Series Code: {self.series_code}"
        date_freq = f"Date Frequency: {self.date_freq}"
        interporlated = f"Interpolation: {self.interporlated}"
        return " / ".join([api, series, date_freq, interporlated])

    def _get_content(self):
        self.params = {
            "DAT": "ALL",
            "SeriesCodes": self.series_code,
            "CSVF": "TN",
            "UsingCodes": "Y",
            "VPD": "Y",
            "VFD": "N",
        }
        self.req = requests.get(self.endpoint, params=self.params)

        if self.req.status_code == 404:
            raise ConnectionError(
                f"A 404 was issued. CCeck input parameters: {self.series_code}"
            )
        else:
            self.content = self.req.content

    def _ts_df(self):
        return pd.read_csv(
            io.BytesIO(self.content), parse_dates=["DATE"], index_col=["DATE"]
        )
        
    @staticmethod
    def _freq_to_n_month(date_freq, shift=0):
        """ 

        Args:
            date_freq (str): date frequency, m / q / y.
            n (int, optional): Index shift to an alternative frequency. Defaults to 0.

        Returns:
            str: ONS frequency.
        """
        freq = {"y":1, "q":4, "m":12}
        freq_index = list(freq).index(date_freq)
        return list(freq.values())[freq_index + shift]

    def _freq_identify(self, df):
        """ Identify the date frequency of the time-series dataframe.

        Args:
            df (pandas.DataFrame): Time-series dataframe.

        Returns:
            tuple(int, str): # of unique months, date frequency.
        """
        n_month = df.index.month.nunique()
        freq = {1: "y", 4: "q", 12: "m"}
        return (n_month, freq.get(n_month))
    
    def _interporlate_ts(self, df, date_freq):
        """ Interpolate Time-series (date-indexed) dataframe.

        Args:
            df (pandas.DataFrame): Time-series dataframe.
            date_freq (str): Resampling frequency (m/q/y)

        Returns:
            pd.DataFrame: Interporlated time-series dataframe.
        """
        self.interporlated = True
        return df.resample(date_freq).interpolate(method="spline", order=3, s=0.0)
    
    def get_time_series(self, date_freq):
        """ Retrieve time-series dataframe based on input date frequency.
        
        If date frequency input is more granular than the available date frequency, 
        interporlation is conducted.

        Args:
            date_freq (str): m / q / y

        Returns:
            pandas.DataFrame: Time-series dataframe.
        """
        self.date_freq = date_freq
        df = self._ts_df()
        n_month, freq = self._freq_identify(df)
        target_n_month = self._freq_to_n_month(date_freq)
        if target_n_month > n_month: # Interporlation required.
            df = df.resample(date_freq).asfreq()
            # Last index with non NaN entry.
            valid_loc = df.index.get_loc(df.iloc[:, 0].last_valid_index())
            df = df.iloc[: valid_loc + 1, :]  # Exclude last NaN row.
            return self._interporlate_ts(df, date_freq)
        else:
            return df.resample(date_freq).asfreq()

# %%
