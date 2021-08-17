import io
import pandas as pd
import requests


class BoeApi:
    def __init__(self, series_code):
        self.series_code = series_code
        self.endpoint = (
            "https://www.bankofengland.co.uk/boeapps/iadb/fromshowcolumns.asp?csv.x=yes"
        )
        self.freq = ["months", "quarters", "years"]
        self._get_content()

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

    def _interval_checker(self, date_interval):
        if date_interval not in self.freq:
            raise ValueError(f"Requires the specific date interval input ∈ {self.freq}")

    def _ts_df(self):
        return pd.read_csv(
            io.BytesIO(self.content), parse_dates=["DATE"], index_col=["DATE"]
        )

    def get_ts(self, date_freq):
        df = self._ts_df().resample(date_freq[0]).asfreq()

        # Last index with non NaN entry.
        valid_loc = df.index.get_loc(df.iloc[:, 0].last_valid_index())
        df = df.iloc[: valid_loc + 1, :]  # Exclude last NaN row.
        return df.resample(date_freq[0]).interpolate(method="spline", order=3, s=0.0)
