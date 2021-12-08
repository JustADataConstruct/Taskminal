import os
import sqlite3
from sqlite3 import Error, Connection
import argparse
import sys
from datetime import datetime, timedelta
from typing import List, Optional
from pathlib import Path

def init_new_database(name:str = "taskminal.db",force:bool = False) -> bool:
    if os.path.isfile(Path(__file__).with_name(name)):
        if force == False:
            print("Database already exists!")
            return False
        else:
            os.remove(Path(__file__).with_name(name))
    conn = None
    try:
        conn = sqlite3.connect(Path(__file__).with_name(name))

        sql = """ CREATE TABLE IF NOT EXISTS tasks (
                            id integer PRIMARY KEY,
                            name text NOT NULL,
                            completed integer DEFAULT FALSE);"""

        cursor = conn.cursor()
        cursor.execute(sql)

        conn.execute("PRAGMA foreign_keys = 1")

        cursor.execute("""
                       CREATE TABLE IF NOT EXISTS time(
                        id integer PRIMARY KEY,
                        task_id integer,
                        start_date text,
                        end_date text,
                        FOREIGN KEY(task_id) REFERENCES tasks(id) ON DELETE CASCADE);""")

        cursor.execute("""
                       CREATE TABLE IF NOT EXISTS comments(
                        id integer PRIMARY KEY,
                        task_id integer,
                        body text,
                        FOREIGN KEY(task_id) REFERENCES tasks(id) ON DELETE CASCADE);""")

        print("Database created sucessfully")
    except Error as e:
        print(e)
        return False
    finally:
        result = True if conn else False
        if conn:
            conn.close()
        return result

def connect_to_db(name:str) -> Connection:
    conn = None
    try:
        conn = sqlite3.connect(Path(__file__).with_name(name))
        conn.execute("PRAGMA foreign_keys = 1")
        return conn
    except Error as e:
        print(e)
        sys.exit(0)


def add_task(conn:Connection,task:str) -> int:
    try:
        now = datetime.now()
        now = now.strftime("%m/%d/%Y, %H:%M:%S")
        sql = """INSERT INTO tasks(name) VALUES(?)"""
        cursor = conn.cursor()
        cursor.execute(sql,(task,))
        conn.commit()
        id = cursor.lastrowid
        print("Task added sucessfully")
        return id
    except Error as e:
        print(e)
        return -1

def remove_task_by_index(conn:Connection,index:int) -> bool:
    try:
        sql = "DELETE FROM tasks WHERE id=?"
        cursor = conn.cursor()
        cursor.execute(sql,(index,))
        conn.commit()
        print("Task deleted.")
        return True
    except Error as e:
        print(e)
        return False

def toggle_task(conn:Connection,id:int) -> List:
    sql = """UPDATE tasks SET completed = CASE WHEN completed = 0 THEN 1 else 0 END WHERE id = ?; """
    cursor = conn.cursor()
    cursor.execute(sql,(id,))
    conn.commit()
    return get_task_by_index(conn,id)

def start_task(conn:Connection,id:int) -> Optional[List]:
    if len(get_task_by_index(conn,id)) == 0:
        print("Task does not exist.")
        return
    sql = "SELECT * from time where task_id=? and end_date is null"
    cursor = conn.cursor()
    cursor.execute(sql,(id,))
    result = cursor.fetchall()
    if len(result) != 0:
        print("This task is already open")
        return
    sql = "INSERT INTO time(start_date,task_id) VALUES(?,?)"
    now = datetime.now()
    now = now.strftime("%m/%d/%Y, %H:%M:%S")
    cursor.execute(sql,(now,id))
    conn.commit()
    print("This task is now open")
    return get_task_by_index(conn,id)

def stop_task(conn:Connection,id:int) -> Optional[List]:
    if len(get_task_by_index(conn,id)) == 0:
        print("Task does not exist.")
        return
    sql = "SELECT * from time WHERE task_id=? AND end_date is null"
    cursor = conn.cursor()
    cursor.execute(sql,(id,))
    result = cursor.fetchall()
    if len(result) == 0:
        print("This task isn't open")
        return
    sql = "UPDATE time set end_date = ? where task_id=? and end_date is null"
    now = datetime.now()
    now = now.strftime("%m/%d/%Y, %H:%M:%S")
    cursor.execute(sql,(now,id))
    conn.commit()
    print("This task is now closed.")
    return get_task_by_index(conn,id)

def get_task_by_index(conn:Connection,id:int) -> List:
    sql = "SELECT * from tasks WHERE id=?"
    cursor = conn.cursor()
    cursor.execute(sql,(id,))
    return cursor.fetchall()

def get_time(conn:Connection,id:int) -> str:
    sql = "SELECT * from time WHERE task_id=?"
    cursor = conn.cursor()
    cursor.execute(sql,(id,))
    result = cursor.fetchall()
    diff = timedelta()
    if len(result) != 0:
        for r in result:
            (_,_,start_date,end_date) = r
            startTime = datetime.strptime(start_date,"%m/%d/%Y, %H:%M:%S") if start_date else timedelta()
            endTime = datetime.strptime(end_date,"%m/%d/%Y, %H:%M:%S") if end_date else startTime
            diff += endTime-startTime
        return str(diff)
    else:
        return "Not started"


def get_all_tasks(conn:Connection) -> List:
    sql = "SELECT * FROM tasks"
    cursor = conn.cursor()
    cursor.execute(sql)
    return cursor.fetchall()

def add_comment(conn:Connection,id:int,comment:str) -> Optional[int]:
    if len(get_task_by_index(conn,id)) == 0:
        print("Task does not exist.")
        return
    sql = """INSERT INTO comments(task_id,body) VALUES(?,?)"""
    cursor = conn.cursor()
    cursor.execute(sql,(id,comment))
    conn.commit()
    id = cursor.lastrowid
    print("Comment added sucessfully.")
    return id

def get_comments_by_task_index(conn:Connection,id:int) -> List:
    if len(get_task_by_index(conn,id)) == 0:
        print("Task does not exist.")
        return []
    sql = "SELECT * FROM comments WHERE task_id = ?"
    cursor = conn.cursor()
    cursor.execute(sql,(id,))
    return cursor.fetchall()

def delete_comment(conn:Connection,comment_id:int) -> bool:
    sql = "DELETE FROM COMMENTS WHERE id=?"
    cursor = conn.cursor()
    cursor.execute(sql,(comment_id,))
    conn.commit()
    print("Comment deleted")
    return True

def close_connection(conn:Connection):
    if conn:
        conn.close()
        return True
    return False

def cleanup():
    print("This will delete all databases, active or otherwise. Do you wish to continue? [y/N]")
    answer = input().lower()
    if answer == "n":
        return
    if os.path.isfile(Path(__file__).with_name("db.txt")):
        os.remove(Path(__file__).with_name("db.txt"))
    dir = Path(__file__).parents[0]
    files = list(Path(dir).glob('*.db'))
    for f in files:
        os.remove(f)

def main():
    parser = argparse.ArgumentParser(prog='taskminal')
    subparsers = parser.add_subparsers(title="Action",help="The action to run.",required=True,dest="command")

    parser_create = subparsers.add_parser("createdb",help="Create a new database")
    parser_create.add_argument("name",help="Name of the new database.")
    parser_create.add_argument("-f",action="store_true",help="Force the creation of this database even if it already exists.")

    parser_connect = subparsers.add_parser("set",help="Sets an active database.")
    parser_connect.add_argument("name",help="Name of the database you want to use.")

    parser_add_task = subparsers.add_parser("new",aliases=["add"],help="Adds a new task")
    parser_add_task.add_argument("title",help="Name of the task")

    parser_list = subparsers.add_parser("list",help="Lists all tasks")
    group = parser_list.add_mutually_exclusive_group()
    group.add_argument("-c",action="store_true",help="Show only completed tasks.")
    group.add_argument("-u",action="store_true",help="Show only unfinished tasks.")
    parser_list.add_argument("-nc",action="store_true",help="Don't show comments.")
    
    parser_get = subparsers.add_parser("get",help="Gets info for a single task by its index.")
    parser_get.add_argument("index",help="Index of the task you're searching for.")

    parser_delete = subparsers.add_parser("delete",aliases=['remove'],help="Removes a task by its index.")
    parser_delete.add_argument("index",help="Index of the task you want to remove.")

    parser_start = subparsers.add_parser("start",help="Marks the current date/time as the start point for this session. Call stop when you're done with this task for now.")
    parser_start.add_argument("index",help="Index of the task you want to update.")

    parser_stop = subparsers.add_parser("stop",help="Stops working on this task.")
    parser_stop.add_argument("index",help="Task index")

    parser_complete = subparsers.add_parser("done",help="Completes the task with the given index.")
    parser_complete.add_argument("index",help="Index of the task.")

    parser_comment = subparsers.add_parser("comment",help="Adds or removes comments from your tasks.")
    comment_action = parser_comment.add_subparsers(title="Action",help="Add or remove comments from your tasks.",required=True,dest="comment_action")
    
    parser_comment_add = comment_action.add_parser("add",help="Add a new comment to the selected task.")
    parser_comment_add.add_argument("id",help="ID of the desired task.")
    parser_comment_add.add_argument("body",help="Text of the comment you want to add.")

    parser_comment_delete = comment_action.add_parser("delete",help="Delete a comment by its unique id.")
    parser_comment_delete.add_argument("comment",help="Index of the comment you want to delete.")

    subparsers.add_parser("cleanup",help="Deletes every database file. Run this before uninstalling.")

    conn = None


    args = parser.parse_args(args=None if sys.argv[1:] else ['--help'])
    if args.command == "createdb":
        init_new_database(args.name,args.f)
    elif args.command == "set":
        if os.path.isfile(Path(__file__).with_name(args.name)):
            with open(Path(__file__).with_name("db.txt"),"w") as f:
                f.write(args.name)
            print("Database selected.")
        else:
            print("Can't find database")
    else:
        if os.path.isfile(Path(__file__).with_name("db.txt")):
            with open(Path(__file__).with_name("db.txt"),'r') as f:
                conn = connect_to_db(f.read())
        else:
            print("There's no active database.")
            sys.exit(0)
        if args.command == "new" or args.command == "add": 
            add_task(conn,args.title)
        elif args.command == "list":
            tasks = get_all_tasks(conn)
            for t in tasks:
                (index,name,completed) = t
                if completed == 0 and args.c or completed == 1 and args.u:
                    continue
                checkmark = "✔" if completed else ""
                print(('[{0}] - {1} [{2}]\nTime spent: {3}').format(index,name,checkmark,get_time(conn,index)))
                if len(get_comments_by_task_index(conn,index)) > 0 and args.nc == False:
                    print("Comments:")
                    for c in get_comments_by_task_index(conn,index):
                        print(('[{0}] {1}').format(c[0],c[2]))
                print("---------")
        elif args.command == "get":
            print(get_task_by_index(conn,args.index))
        elif args.command == "delete" or args.command =="remove":
            remove_task_by_index(conn,args.index)
        elif args.command == "start":
            start_task(conn,args.index)
        elif args.command == "stop":
            stop_task(conn,args.index)
        elif args.command == "done":
            stop_task(conn,args.index)
            toggle_task(conn,args.index)
        elif args.command == "comment":
            if args.comment_action == "add":
                add_comment(conn,args.id,args.body)
            elif args.comment_action == "delete":
                delete_comment(conn,args.comment)
        elif args.command == "cleanup":
            cleanup()
        close_connection(conn)

if __name__=="__main__":
    main()
