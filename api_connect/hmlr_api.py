#%%
from SPARQLWrapper import SPARQLWrapper, JSON
from pandas.tseries.offsets import MonthEnd
import pandas as pd


class HmlrApi:
    """ API to retrieve all of the RDF properties
    for a particular local authority and time.

    * NOTE: 
        For detailed information about input variables and regions,
        please refer to the website: https://landregistry.data.gov.uk/app/ukhpi.
    """

    def __init__(self, query_var, region="united-kingdom"):

        self.query_var = query_var
        self.region = region
        self.endpoint = "http://landregistry.data.gov.uk/landregistry/query"
        self.date_freq = None
        self.interporlated = None
        self._get_content()

    def __repr__(self):
        api = "HMLR"
        query_var = f"Query Variable: {self.query_var}"
        date_freq = f"Date Frequency: {self.date_freq}"
        interporlated = f"Interpolation: {self.interporlated}"
        return " / ".join([api, query_var, date_freq, interporlated])

    def _get_query(self):
        """ SPARQL Query.
        TODO: SQL expert needed!!
        """
        self.query = (
            """
        PREFIX  xsd:  <http://www.w3.org/2001/XMLSchema#>
        PREFIX  ukhpi: <http://landregistry.data.gov.uk/def/ukhpi/>

        SELECT  *
        WHERE
          { { SELECT  ?DATE ?item
              WHERE
                { ?item  ukhpi:refRegion  <http://landregistry.data.gov.uk/id/region/"""
            + f"{self.region}"
            + """> ;
                         ukhpi:refMonth   ?DATE
                }
              ORDER BY ?DATE
            }
            OPTIONAL
              { ?item  ukhpi:"""
            + f"{self.query_var}  ?{self.query_var}"
            + """ }

            BIND(<http://landregistry.data.gov.uk/id/region/"""
            + f"{self.region}"
            + """> AS ?Region)
          }
        """
        )
        return self.query

    def _get_content(self):
        self.query = self._get_query()
        self.response = SPARQLWrapper(self.endpoint)
        self.response.setQuery(self.query)
        self.response.setReturnFormat(JSON)
        self.response = self.response.query()
        self.content = self.response.convert()

    @staticmethod
    def catch(func, *args, **kwargs):
        try:
            return func(*args, **kwargs)
        except TypeError:
            return None

    @staticmethod
    def _freq_to_n_month(date_freq, shift=0):
        """ 

        Args:
            date_freq (str): date frequency, m / q / y.
            n (int, optional): Index shift to an alternative frequency. Defaults to 0.

        Returns:
            str: ONS frequency.
        """
        freq = {"y": 1, "q": 4, "m": 12}
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

    def _ts_df(self):
        """ Load SPARQL queried data to Padnas DataFrame.

        Returns:
            pd.DataFrame: Time-series data.
        """
        df = []
        col_vars = self.content["head"]["vars"]
        for row in self.content["results"]["bindings"]:
            df.append([self.catch(lambda: row.get(key)["value"]) for key in col_vars])

        df = pd.DataFrame(df, columns=col_vars)
        df["DATE"] = pd.to_datetime(df.iloc[:, 0]) + MonthEnd(1)
        df = df.set_index("DATE")
        df[self.query_var] = df[self.query_var].astype(float)
        return df[[self.query_var]]

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
