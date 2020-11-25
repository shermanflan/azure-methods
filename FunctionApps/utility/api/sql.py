import os

import pyodbc


class SQLConnection():

    def __init__(self, sql_conn_id):
        self.sql_conn_id = sql_conn_id
        self.sql_client = None

    def get_conn(self):
        if self.sql_client is not None:
            return self.sql_client

        self.sql_client = pyodbc.connect(os.environ[self.sql_conn_id], 
                                         autocommit=True)

        return self.sql_client