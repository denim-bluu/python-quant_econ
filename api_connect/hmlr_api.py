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
        self.freq = ["months", "quarters", "years"]
        self._get_content()

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

    def get_ts(self, date_freq):
        df = self._ts_df().resample(date_freq[0]).asfreq()

        # Last index with non NaN entry.
        valid_loc = df.index.get_loc(df.iloc[:, 0].last_valid_index())
        df = df.iloc[: valid_loc + 1, :]  # Exclude last NaN row.
        return df.resample(date_freq[0]).interpolate(method="spline", order=3, s=0.0)
