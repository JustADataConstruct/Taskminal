import os
import sqlite3
from sqlite3.dbapi2 import sqlite_version
from sqlite3 import Error

def init_new_database(name:str = "taskminal.db",force:bool = False) -> bool:
    if os.path.isfile(name):
        if force == False:
            print("Database already exists!")
            return False
        else:
            os.remove(name)
    conn = None
    try:
        conn = sqlite3.connect(name)
        print(f"Connected: {sqlite_version}")
    except Error as e:
        print(e)
        return False
    finally:
        result = True if conn else False
        if conn:
            conn.close()
        return result

def connect_to_db(name):
    conn = None
    try:
        conn = sqlite3.connect(name)
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

def add_task(conn,task):
    sql = """INSERT INTO tasks(name,start_date) VALUES(?,?)"""
    cursor = conn.cursor()
    cursor.execute(sql,task)
    conn.commit()
    return cursor.lastrowid

def remove_task_by_index(conn,index):
    sql = "DELETE FROM tasks WHERE id=?"
    cursor = conn.cursor()
    cursor.execute(sql,(index,))
    conn.commit()

def get_all_tasks(conn):
    sql = "SELECT * FROM tasks"
    cursor = conn.cursor()
    cursor.execute(sql)
    return cursor.fetchall()

def close_connection(conn):
    if conn:
        conn = conn.close()
    return conn

if __name__ == "__main__":
    print("Hello world")
