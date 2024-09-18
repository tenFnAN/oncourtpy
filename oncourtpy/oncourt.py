import os
import pyodbc
from datetime import datetime
import pandas as pd
import numpy as np 
from .oncourt_query import query_dict
 
class OncourtDb:
    def __init__(self, type, type2):
        """
        Initializes the OncourtDb instance with the given types and establishes a database connection.
        
        Args:
            type (str): atp or wta
            type2 (str):single or double
        """
        self.con  = self.connect_db()
        self.type = type
        self.type2= type2
        self.date_today = pd.to_datetime(datetime.today().strftime('%Y-%m-%d'))
        
    def __filter_single_or_double(self, ds ):
        return ds[ds['type2'] == self.type2]

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
        odbc_conn_str = 'Driver={Microsoft Access Driver (*.mdb, *.accdb)};Dbq=%s;Pwd=%s;' % (os.getenv('oncourt_path'), os.getenv('oncourt_pwd'))
        return pyodbc.connect(odbc_conn_str) 

    def query_oncourt_schedule_today(self):
        """
        Queries the schedule for today's single & double matches.
        
        Returns:
            pd.DataFrame: A DataFrame with today's schedule data.
        """
        query = query_dict['schedule_today']
    
        ret = (pd.read_sql( query.replace('_type', '_'+self.type) , self.con)
        .assign(
            type  = self.type, 
            type2 = lambda x: np.where(x['P1'].str.contains('/'), 'double', 'single'), 
            id    = lambda x:x['P1'] + x['P2'] + x['NAME_T'])
        .sort_values(['id', 'ODDS_B'], ascending = [True, False])
        .groupby(['id'])
        .head(1) 
        .drop(['id'], axis=1) ) 
        
        ret[['LATITUDE_T', 'LONGITUDE_T']] = ret[['LATITUDE_T', 'LONGITUDE_T']].round(3)
        
        ret = self.__filter_single_or_double(ds=ret) 

        return ret[['type', 'type2', *ret.columns[:-2] ]]
    
    def query_oncourt_schedule_historical(self, date_start, date_end):
        """
        Queries historical match schedules within the specified date range.
        
        Args:
            date_start (str): The start date for the query in 'YYYY-MM-DD' format.
            date_end (str): The end date for the query in 'YYYY-MM-DD' format.
        
        Returns:
            pd.DataFrame: A DataFrame with historical schedule data.
        """
        query = query_dict['schedule_historical'].format(date_min = date_start, date_max = date_end)

        ret = (pd.read_sql( query.replace('_type', '_'+self.type) , self.con)
        .assign(
            type  = self.type, 
            type2 = lambda x: np.where(x['P1'].str.contains('/'), 'double', 'single'), 
            id_P2 = lambda x: np.where(x['id_P2'].isna(), x['idPlayer2'], x['id_P2']),
            id_P1 = lambda x: np.where(x['id_P1'].isna(), x['idPlayer'], x['id_P1']),
            id    = lambda x: np.where(x['id_P1'] < x['id_P2'], x['P1'].astype(str), x['P2'].astype(str)) + np.where(x['id_P1'] < x['id_P2'], x['P2'].astype(str), x['P1'].astype(str)) + x['NAME_T'].astype(str) + x['DATE_G'].astype(str) ) 
        .sort_values(['id', 'ODDS_B'], ascending = [True, False])
        .groupby(['id'])
        .head(1) 
        .drop(['id', 'idPlayer2', 'idPlayer', 'ODDS_B'], axis=1) ) 
        
        ret = self.__filter_single_or_double(ds=ret) 

        return ret[['type', 'type2', *ret.columns[:-2] ]]

    def query_oncourt_playerdata(self, date_start = '2020-07-01', date_end = None, players_id = ['45854']):
        """
        Queries player data for the specified date range and player IDs.
        
        Args:
            date_start (str): The start date for the query in 'YYYY-MM-DD' format.
            date_end (str or None): The end date for the query in 'YYYY-MM-DD' format. Defaults to today's date if None.
            players_id (list): A list of player IDs to include in the query.
        
        Returns:
            pd.DataFrame: A DataFrame with player data.
        """
        if date_end is None:
            date_end = self.date_today

        players_id = ','.join( pd.Series(players_id).unique().astype(str) )
        
        query = query_dict['playerdata'].format(date_min = date_start, date_max = date_end, players_id = players_id)
        ret = (pd.read_sql( query.replace('_type', '_'+self.type) , self.con)
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

    def query_oncourt_matches(self, date_start = '2020-07-01', date_end = None):
        """
        Queries match data for the specified date range.
        
        Args:
            date_start (str): The start date for the query in 'YYYY-MM-DD' format.
            date_end (str or None): The end date for the query in 'YYYY-MM-DD' format. Defaults to today's date if None.
        
        Returns:
            pd.DataFrame: A DataFrame with match data.
        """
        if date_end is None:
            date_end = self.date_today

        query = query_dict['matches'].format(date_min = date_start, date_max = date_end)

        ret = (pd.read_sql( query.replace('_type', '_'+self.type) , self.con)
        .assign(
            type  = self.type, 
            type2 = lambda x: np.where(x['P1'].str.contains('/'), 'double', 'single'), 
            ID2 = lambda x: np.where(x['ID2'].isna(), x['idPlayer2'], x['ID2']),
            ID1 = lambda x: np.where(x['ID1'].isna(), x['idPlayer'], x['ID1']),
            DATE_G = lambda x:x['DATE_G'] + pd.Timedelta("1 day"),
            TIER_T = lambda x:x['TIER_T'].astype(str).str.strip(),
            TIME_G = lambda x:x['MT'].dt.hour * 60 + x['MT'].dt.minute 
         )
         .drop(['ID_T', 'ID_R', 'idPlayer2', 'MT'], axis=1))

        ret = self.__filter_single_or_double(ds=ret) 

        return ret

    def query_oncourt_ranking(self, days_ago):
        """
        Queries player rankings with an offset of days ago.

        Args:
            days_ago (int): The number of days ago to use for the ranking offset.
        
        Returns:
            pd.DataFrame: A DataFrame with player ranking data.
        """
        query = query_dict['playerranking'].format(offset = days_ago)  

        ret = pd.read_sql( query.replace('_type', '_'+self.type) , self.con)

        return ret 

