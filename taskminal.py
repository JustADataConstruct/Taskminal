import os
import sqlite3
from sqlite3.dbapi2 import sqlite_version
from sqlite3 import Error

def init_new_database(force:bool = False) -> bool:
    if os.path.isfile("taskminal.db"):
        if force == False:
            print("Database already exists!")
            return False
        else:
            os.remove("taskminal.db")
    conn = None
    try:
        conn = sqlite3.connect("taskminal.db")
        print(f"Connected: {sqlite_version}")
    except Error as e:
        print(e)
        return False
    finally:
        result = True if conn else False
        if conn:
            conn.close()
        return result

def connect_to_db():
    conn = None
    try:
        conn = sqlite3.connect("taskminal.db")
        return conn
    except Error as e:
        print(e)
    return conn

def create_table(conn,sql):
    try:
        cursor = conn.cursor()
        cursor.execute(sql)
    except Error as e:
        print(e)

def close_connection(conn):
    if conn:
        conn = conn.close()
    return conn

if __name__ == "__main__":
    print("Hello world")
