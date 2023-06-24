import sqlite3
import pandas as pd

class DBStorage():
    def __init__(self):
        self.connection = sqlite3.connect('links.db')
        self.setup_tables()

    def setup_tables(self):
        cursor = self.connection.cursor()
        results_table = r"""
            CREATE TABLE IF NOT EXISTS results (
                id INTEGER PRIMARY KEY,
                query TEXT,
                rank INTEGER,
                link TEXT,
                title TEXT,
                snippet TEXT,
                html TEXT,
                created DATETIME,
                relevance INTEGER,
                UNIQUE(query, link)
            );
        """

        cursor.execute(results_table)
        self.connection.commit()
        cursor.close()

    def query_results(self, query):
        dataframe = pd.read_sql(f"select * from results where query='{query}' order by rank asc;", self.connection)
        return dataframe
    
    def insert_row(self, values):
        cursor = self.connection.cursor()

        try:
            cursor.execute('INSERT INTO results (query, rank, link, title, snippet, html, created) VALUES(?,?,?,?,?,?,?)')
            self.connection.commit()
        except sqlite3.IntegrityError:
            pass

        cursor.close()