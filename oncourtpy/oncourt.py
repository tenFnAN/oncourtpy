import os
import warnings
import pyodbc
from datetime import datetime
import pandas as pd
import numpy as np 
from oncourtpy.oncourt_query import query_dict
 
class OncourtDb:
    def __init__(self, type, type2):
        """
        Initializes the OncourtDb instance with the given types and establishes a database connection.
        
        Args:
            type (str): atp or wta
            type2 (str):single or double
        """
        valid_type = {'atp', 'wta'}
        valid_type2 = {'single', 'double'}

        self.type = str(type).strip().lower()
        self.type2 = str(type2).strip().lower()

        if self.type not in valid_type:
            raise ValueError(f"Invalid type='{type}'. Expected one of: {sorted(valid_type)}")
        if self.type2 not in valid_type2:
            raise ValueError(f"Invalid type2='{type2}'. Expected one of: {sorted(valid_type2)}")

        self.con  = self.connect_db()
        self.date_today = pd.to_datetime(datetime.today().strftime('%Y-%m-%d'))
        
    def __filter_single_or_double(self, ds ):
        return ds[ds['type2'] == self.type2]

    def __normalize_date(self, value, field_name):
        try:
            return pd.to_datetime(value).strftime('%Y-%m-%d')
        except Exception as exc:
            raise ValueError(
                f"Invalid {field_name}='{value}'. Expected date-like value (e.g. 'YYYY-MM-DD')."
            ) from exc

    def __normalize_players_id_csv(self, players_id):
        series = pd.Series(players_id).dropna().astype(str).str.strip()
        series = series[series != '']

        if series.empty:
            raise ValueError("players_id cannot be empty.")

        valid_mask = series.str.fullmatch(r'\d+')
        if not valid_mask.all():
            invalid_examples = series[~valid_mask].unique().tolist()[:5]
            raise ValueError(
                f"players_id contains non-numeric values: {invalid_examples}. "
                "Only numeric player IDs are allowed."
            )

        return ','.join(series.drop_duplicates().tolist())

    def __normalize_non_negative_int(self, value, field_name):
        try:
            normalized = int(value)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"Invalid {field_name}='{value}'. Expected integer >= 0.") from exc

        if normalized < 0:
            raise ValueError(f"Invalid {field_name}='{value}'. Expected integer >= 0.")

        return normalized

    def __ensure_open_connection(self):
        if getattr(self, 'con', None) is None:
            raise RuntimeError(
                "Database connection is closed. Create a new OncourtDb instance before querying."
            )

    def __warn_deprecated(self, old_name, new_name):
        warnings.warn(
            f"'{old_name}' is deprecated and will be removed in a future release. Use '{new_name}' instead.",
            DeprecationWarning,
            stacklevel=2,
        )

    def __read_sql_df(self, query):
        self.__ensure_open_connection()
        cursor = self.con.cursor()
        try:
            cursor.execute(query)
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description] if cursor.description else []
        finally:
            cursor.close()
        return pd.DataFrame.from_records(rows, columns=columns)

    def connect_db(self):
        """
        Connects to the Microsoft Access database using credentials from environment variables.
        
        This method constructs a connection string for Microsoft Access using the `pyodbc` library. 
        It retrieves the database path and password from environment variables, which must be set 
        prior to calling this method.

        Environment Variables Required:
            - `oncourt_path`: The path to the Access database file (MDB or ACCDB).
            - `oncourt_pwd`: The password for the database.

        Returns:
            pyodbc.Connection: The database connection object.
        
        Raises:
            pyodbc.Error: If the connection fails or environment variables are not set correctly.
        """
        db_path = os.getenv('oncourt_path')
        db_pwd = os.getenv('oncourt_pwd')

        if not db_path:
            raise ValueError("Missing required environment variable: oncourt_path")
        if db_pwd is None:
            raise ValueError("Missing required environment variable: oncourt_pwd")

        odbc_conn_str = 'Driver={Microsoft Access Driver (*.mdb, *.accdb)};Dbq=%s;Pwd=%s;' % (db_path, db_pwd)
        return pyodbc.connect(odbc_conn_str) 

    def close(self):
        if getattr(self, 'con', None) is not None:
            self.con.close()
            self.con = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False

    def get_schedule_today(self):
        """
        Queries the schedule for today's single & double matches.
        
        Returns:
            pd.DataFrame: A DataFrame with today's schedule data.
        """
        self.__ensure_open_connection()
        query = query_dict['schedule_today']
    
        ret = (self.__read_sql_df(query.replace('_type', '_'+self.type))
        .assign(
            type  = self.type, 
            type2 = lambda x: np.where(x['P1'].str.contains('/', na=False), 'double', 'single'), 
            id    = lambda x:x['P1'] + x['P2'] + x['NAME_T'],
            TIER_T= lambda x:x['TIER_T'].astype(str).str.strip() )
        .sort_values(['id', 'ODDS_B'], ascending = [True, False])
        .groupby(['id'])
        .head(1) 
        .drop(['id'], axis=1) ) 
        
        ret[['LATITUDE_T', 'LONGITUDE_T']] = ret[['LATITUDE_T', 'LONGITUDE_T']].round(3)
        
        ret = self.__filter_single_or_double(ds=ret) 

        return ret[['type', 'type2', *ret.columns[:-2] ]]
    
    def get_schedule_history(self, date_start, date_end):
        """
        Queries historical match schedules within the specified date range.
        
        Args:
            date_start (str): The start date for the query in 'YYYY-MM-DD' format.
            date_end (str): The end date for the query in 'YYYY-MM-DD' format.
        
        Returns:
            pd.DataFrame: A DataFrame with historical schedule data.
        """
        self.__ensure_open_connection()
        date_start = self.__normalize_date(date_start, 'date_start')
        date_end = self.__normalize_date(date_end, 'date_end')

        query = query_dict['schedule_historical'].format(date_min = date_start, date_max = date_end)

        ret = (self.__read_sql_df(query.replace('_type', '_'+self.type))
        .assign(
            type  = self.type, 
            type2 = lambda x: np.where(x['P1'].str.contains('/', na=False), 'double', 'single'), 
            id_P2 = lambda x: np.where(x['id_P2'].isna(), x['idPlayer2'], x['id_P2']),
            id_P1 = lambda x: np.where(x['id_P1'].isna(), x['idPlayer'], x['id_P1']),
            TIER_T= lambda x:x['TIER_T'].astype(str).str.strip(),
            id    = lambda x: np.where(x['id_P1'] < x['id_P2'], x['P1'].astype(str), x['P2'].astype(str)) + np.where(x['id_P1'] < x['id_P2'], x['P2'].astype(str), x['P1'].astype(str)) + x['NAME_T'].astype(str) + x['DATE_G'].astype(str) ) 
        .sort_values(['id', 'ODDS_B'], ascending = [True, False])
        .groupby(['id'])
        .head(1) 
        .drop(['id', 'idPlayer2', 'idPlayer', 'ODDS_B'], axis=1) ) 
        
        ret = self.__filter_single_or_double(ds=ret) 

        return ret[['type', 'type2', *ret.columns[:-2] ]]

    def get_player_data(self, date_start = '2020-07-01', date_end = None, players_id = None):
        """
        Queries player data for the specified date range and player IDs.
        
        Args:
            date_start (str): The start date for the query in 'YYYY-MM-DD' format.
            date_end (str or None): The end date for the query in 'YYYY-MM-DD' format. Defaults to today's date if None.
            players_id (list or None): A list of player IDs to include in the query.
        
        Returns:
            pd.DataFrame: A DataFrame with player data.
        """
        self.__ensure_open_connection()

        if date_end is None:
            date_end = self.date_today

        if players_id is None:
            players_id = ['45854']

        date_start = self.__normalize_date(date_start, 'date_start')
        date_end = self.__normalize_date(date_end, 'date_end')

        players_id = self.__normalize_players_id_csv(players_id)
        
        query = query_dict['playerdata'].format(date_min = date_start, date_max = date_end, players_id = players_id)
        ret = (self.__read_sql_df(query.replace('_type', '_'+self.type))
        .assign(
            type  = self.type, 
            ID2 = lambda x: np.where(x['ID2'].isna(), x['idPlayer2'], x['ID2']),
            ID1 = lambda x: np.where(x['ID1'].isna(), x['idPlayer'], x['ID1']),
            DATE_G = lambda x:x['DATE_G'] + pd.Timedelta("1 day"),
            TIER_T = lambda x:x['TIER_T'].astype(str).str.strip(),
            TIME_G = lambda x:x['MT'].dt.hour * 60 + x['MT'].dt.minute 
         )
         .drop(['ID_T', 'ID_R', 'idPlayer', 'idPlayer2', 'MT'], axis=1))

        return ret

    def get_matches(self, date_start = '2020-07-01', date_end = None):
        """
        Queries match data for the specified date range.
        
        Args:
            date_start (str): The start date for the query in 'YYYY-MM-DD' format.
            date_end (str or None): The end date for the query in 'YYYY-MM-DD' format. Defaults to today's date if None.
        
        Returns:
            pd.DataFrame: A DataFrame with match data.
        """
        self.__ensure_open_connection()

        if date_end is None:
            date_end = self.date_today

        date_start = self.__normalize_date(date_start, 'date_start')
        date_end = self.__normalize_date(date_end, 'date_end')

        query = query_dict['matches'].format(date_min = date_start, date_max = date_end)

        ret = (self.__read_sql_df(query.replace('_type', '_'+self.type))
        .assign(
            type  = self.type, 
            type2 = lambda x: np.where(x['P1'].str.contains('/', na=False), 'double', 'single'), 
            ID2 = lambda x: np.where(x['ID2'].isna(), x['idPlayer2'], x['ID2']),
            ID1 = lambda x: np.where(x['ID1'].isna(), x['idPlayer'], x['ID1']),
            DATE_G = lambda x:x['DATE_G'] + pd.Timedelta("1 day"),
            TIER_T = lambda x:x['TIER_T'].astype(str).str.strip(),
            TIME_G = lambda x:x['MT'].dt.hour * 60 + x['MT'].dt.minute 
         )
         .drop(['ID_T', 'ID_R', 'idPlayer2', 'MT'], axis=1))

        ret = self.__filter_single_or_double(ds=ret) 

        return ret

    def get_ranking(self, days_ago):
        """
        Queries player rankings with an offset of days ago.

        Args:
            days_ago (int): The number of days ago to use for the ranking offset.
        
        Returns:
            pd.DataFrame: A DataFrame with player ranking data.
        """
        self.__ensure_open_connection()
        days_ago = self.__normalize_non_negative_int(days_ago, 'days_ago')
        query = query_dict['playerranking'].format(offset = days_ago)  

        ret = self.__read_sql_df(query.replace('_type', '_'+self.type))

        return ret 

    def query_oncourt_schedule_today(self):
        self.__warn_deprecated('query_oncourt_schedule_today', 'get_schedule_today')
        return self.get_schedule_today()

    def query_oncourt_schedule_historical(self, date_start, date_end):
        self.__warn_deprecated('query_oncourt_schedule_historical', 'get_schedule_history')
        return self.get_schedule_history(date_start, date_end)

    def query_oncourt_playerdata(self, date_start = '2020-07-01', date_end = None, players_id = None):
        self.__warn_deprecated('query_oncourt_playerdata', 'get_player_data')
        return self.get_player_data(date_start=date_start, date_end=date_end, players_id=players_id)

    def query_oncourt_matches(self, date_start = '2020-07-01', date_end = None):
        self.__warn_deprecated('query_oncourt_matches', 'get_matches')
        return self.get_matches(date_start=date_start, date_end=date_end)

    def query_oncourt_ranking(self, days_ago):
        self.__warn_deprecated('query_oncourt_ranking', 'get_ranking')
        return self.get_ranking(days_ago)

