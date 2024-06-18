import psycopg2
import traceback
import time
from flask import current_app as app


class DatabaseConnection:
    _instance = None

    @staticmethod
    def get_instance():
        if DatabaseConnection._instance is None:
            DatabaseConnection()
        return DatabaseConnection._instance

    def __init__(self):
        if DatabaseConnection._instance is not None:
            raise Exception("This class is a singleton!")
        else:
            self.connect()
            DatabaseConnection._instance = self

    def connect(self):
        retries = 0
        db_params = {
            "dbname": app.config["POSTGRES_DB"],
            "user": app.config["POSTGRES_USER"],
            "password": app.config["POSTGRES_PASSWORD"],
            "host": app.config["METADATA_STORAGE_HOST"],
            "port": app.config["METADATA_STORAGE_PORT"],
        }
        while retries < 5:
            try:
                retries += 1
                self._connection = psycopg2.connect(**db_params)
                print("Connected to database")
            except psycopg2.OperationalError:
                traceback.print_exc()
                time.sleep(3)

    def write(self, query, params=None):
        try:
            print(f"Query: {query}")
            cur = self._connection.cursor()
            cur.execute(query, params)
            self._connection.commit()
            return cur
        except Exception:
            traceback.print_exc()
            self._connection.rollback()
            raise Exception("Error writing to database")

    def write_many(self, query, params=None):
        try:
            cur = self._connection.cursor()
            cur.executemany(query, params)
            self._connection.commit()
            return cur
        except Exception:
            traceback.print_exc()
            self._connection.rollback()
            return None

    def read_all(self, query, params=None):
        try:
            cur = self._connection.cursor()
            cur.execute(query, params)
            return cur.fetchall()
        except Exception:
            traceback.print_exc()
            self._connection.rollback()
            return None

    def read_one(self, query, params=None):
        try:
            cur = self._connection.cursor()
            cur.execute(query, params)
            return cur.fetchone()
        except Exception:
            traceback.print_exc()
            self._connection.rollback()
            return None
