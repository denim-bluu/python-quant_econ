#%%
import pandas as pd
import requests


class OnsApi:
    def __init__(self, dataset_id, timeseries_id):
        self.timeseries_id = timeseries_id
        self.dataset_id = dataset_id
        self.endpoint = "https://api.ons.gov.uk/timeseries"
        self.date_freq = None
        self.interporlated = None
        self._get_content()
        
    def __repr__(self):
        api = "ONS"
        data_id = f"Dataset ID: {self.dataset_id}"
        ts_id = f"Timeseries ID: {self.timeseries_id}"
        date_freq = f"Date Frequency: {self.date_freq}"
        interporlated = f"Interpolation: {self.interporlated}"
        return " / ".join([api, data_id, ts_id, date_freq, interporlated])

    def _get_content(self):
        self.url = (
            f"{self.endpoint}/{self.timeseries_id}/dataset/{self.dataset_id}/data"
        )

        self.req = requests.get(self.url)

        if self.req.status_code == 404:
            raise ConnectionError(
                f"A 404 was issued. CCeck input parameters: {self.timeseries_id}, {self.dataset_id}"
            )
        else:
            self.content = self.req.json()

    def _freq(self, date_freq, shift=0):
        """ ONS API requires frequency inputs to be months / quarters / years.
        For consistency, this class inputs for frequency are m / q / y.
        Hence, re-mapping the m / q / y user inputs to months / quarters / years.
        Also, allowing the user to the next frequency in the list with 'shift' argument.

        Args:
            date_freq (str): m / q / y
            n (int, optional): Index shift to an alternative frequency. Defaults to 0.

        Returns:
            str: ONS frequency.
        """
        freq = {"m": "months", "q": "quarters", "y": "years"}
        freq_index = list(freq).index(date_freq)
        return list(freq.values())[freq_index + shift]

    @staticmethod
    def _date_parser(df):
        """ Parse Quarterly / Monthly date format and retrieve
        period date index.

        Returns:
            pd.DatetimeIndex: Date time index.
        """
        if not all(df["month"] == ""):
            period_idx = pd.PeriodIndex(df["date"], freq="M")
        elif not all(df["quarter"] == ""):  # Check if 'Q' in date string.
            _date = df["date"].str.replace(r"(\d+) (Q\d)", r"\1-\2", regex=True)
            period_idx = pd.PeriodIndex(_date, freq="Q")
        else:
            period_idx = pd.PeriodIndex(df["date"], freq="Y")

        return pd.to_datetime(period_idx.to_timestamp(how="e").date)

    def _ts_df(self, date_freq):
        df = pd.DataFrame(pd.json_normalize(self.content[date_freq]))
        df["DATE"] = self._date_parser(df)
        df[self.timeseries_id] = df["value"].astype(float)
        df = df.set_index("DATE")[[self.timeseries_id]]
        return df

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
        # If date_interval param is not included.
        if not self.content.get(self._freq(date_freq)):
            _df = self._ts_df(self._freq(date_freq, 1))
            return self._interporlate_ts(_df, date_freq)
        return self._ts_df(self._freq(date_freq))


# %%
