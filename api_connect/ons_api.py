import pandas as pd
import requests


class OnsApi:
    def __init__(self, dataset_id, timeseries_id):
        self.timeseries_id = timeseries_id
        self.dataset_id = dataset_id
        self.endpoint = "https://api.ons.gov.uk/timeseries"
        self.freq = ["months", "quarters", "years"]
        self._get_content()

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

    @staticmethod
    def _date_parser(df) -> pd.DatetimeIndex:
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

    def get_ts(self, date_freq):
        # If date_interval param is not supported.
        if not self.content.get(date_freq):
            _index = self.freq.index(date_freq)

            if _index == len(self.freq) - 1:
                raise ValueError("Something is wrong...")

            # Interpolate with higher date interval.
            _df = self._ts_df(self.freq[_index + 1])
            return _df.resample(date_freq[0]).interpolate(
                method="spline", order=3, s=0.0
            )
        return self._ts_df(date_freq)
