import os
import sqlite3
from sqlite3 import Error
import argparse
import sys
from datetime import datetime

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

        sql = """ CREATE TABLE IF NOT EXISTS tasks (
                            id integer PRIMARY KEY,
                            name text NOT NULL,
                            completed integer DEFAULT FALSE,
                            start_date text NOT NULL,
                            end_date text);"""

        cursor = conn.cursor()
        cursor.execute(sql)

        print("Database created sucessfully")
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
        #print("Connected.")
        return conn
    except Error as e:
        print(e)
    return conn


def add_task(conn,task):
    now = datetime.now()
    now = now.strftime("%m/%d/%Y, %H:%M:%S")
    sql = """INSERT INTO tasks(name,start_date) VALUES(?,?)"""
    cursor = conn.cursor()
    cursor.execute(sql,(task,now))
    conn.commit()
    return cursor.lastrowid

def remove_task_by_index(conn,index):
    sql = "DELETE FROM tasks WHERE id=?"
    cursor = conn.cursor()
    cursor.execute(sql,(index,))
    conn.commit()

def toggle_task(conn,id):
    sql = """UPDATE tasks SET completed = CASE WHEN completed = 0 THEN 1 else 0 END WHERE id = ?; """
    cursor = conn.cursor()
    cursor.execute(sql,(id,))
    conn.commit()
    return get_task_by_index(conn,id)

def update_task(conn,id):
    now = datetime.now()
    now = now.strftime("%m/%d/%Y, %H:%M:%S")
    sql = "UPDATE tasks SET end_date = ? WHERE id=?"
    cursor = conn.cursor()
    cursor.execute(sql,(now,id))
    conn.commit()
    return get_task_by_index(conn,id)

def get_task_by_index(conn,id):
    sql = "SELECT * from tasks WHERE id=?"
    cursor = conn.cursor()
    cursor.execute(sql,(id,))
    return cursor.fetchall()

def get_all_tasks(conn):
    sql = "SELECT * FROM tasks"
    cursor = conn.cursor()
    cursor.execute(sql)
    return cursor.fetchall()

def close_connection(conn):
    if conn:
        conn = conn.close()
        #print("Connection closed.")
    return conn

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog='taskminal')
    subparsers = parser.add_subparsers(title="Action",help="The action to run.",required=True,dest="command")

    parser_create = subparsers.add_parser("createdb",help="Create a new database")
    parser_create.add_argument("name",help="Name of the new database.")
    parser_create.add_argument("-f",action="store_true",help="Force the creation of this database even if it already exists.")

    parser_connect = subparsers.add_parser("set",help="Sets an active database.")
    parser_connect.add_argument("name",help="Name of the database you want to use.")

    parser_add_task = subparsers.add_parser("new",help="Adds a new task")
    parser_add_task.add_argument("title",help="Name of the task")

    parser_list = subparsers.add_parser("list",help="Lists all tasks")
    parser_list.add_argument("-c",action="store_true",help="Show only completed tasks.")
    parser_list.add_argument("-u",action="store_true",help="Show only unfinished tasks.")
    
    parser_get = subparsers.add_parser("get",help="Gets info for a single task by its index.")
    parser_get.add_argument("index",help="Index of the task you're searching for.")

    parser_delete = subparsers.add_parser("delete",help="Removes a task by its index.")
    parser_delete.add_argument("index",help="Index of the task you want to remove.")

    parser_update = subparsers.add_parser("update",help="Sets the current date/time as the last time you worked on this task, but keeps it open.")
    parser_update.add_argument("index",help="Index of the task you want to update.")

    parser_complete = subparsers.add_parser("done",help="Completes the task with the given index.")
    parser_complete.add_argument("index",help="Index of the task.")

    parser_close = subparsers.add_parser("close",help="Close an active connection.")

    conn = None

    args = parser.parse_args()
    if args.command == "createdb":
        init_new_database(args.name,args.f)
    elif args.command == "set":
        if os.path.isfile(args.name):
            with open("db.txt","w") as f:
                f.write(args.name)
            print("Database selected.")
        else:
            print("Can't find database")
    else:
        if os.path.isfile("db.txt"):
            with open('db.txt','r') as f:
                conn = connect_to_db(f.read())
        else:
            print("There's no active database.")
            sys.exit(0)
        if args.command == "new":
            add_task(conn,args.title)
        elif args.command == "list":
            print(get_all_tasks(conn)) #TODO: Make this pretty.
            #TODO: Use the args.
        elif args.command == "get":
            print(get_task_by_index(conn,args.index))
        elif args.command == "delete":
            remove_task_by_index(conn,args.index)
        elif args.command == "update":
            update_task(conn,args.index) #TODO: We could save every time we start and stop a task so we can generate reports and stuff. 
        elif args.command == "done":
            update_task(conn,args.index)
            toggle_task(conn,args.index)
        close_connection(conn)

