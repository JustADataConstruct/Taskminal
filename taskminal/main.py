import os
import sqlite3
from sqlite3 import Error, Connection
import argparse
import sys
from datetime import datetime, timedelta
from typing import List, Tuple
from pathlib import Path
import webbrowser
from calendar import month_name

from taskminal.report import Report


def init_new_database(name: str = "taskminal.db", force: bool = False) -> bool:
    """
    Will try to create a new database with the indicated name. If force is true, will overwrite any existing database with that name.

    :param name str: Name of the new database. If it doesn't have the ".db" extension, it will be appended.
    :param force bool: Overwrite existing database with the same name?
    :rtype bool: True if the database has been created correctly, False otherwise.
    """
    if name.endswith(".db") is False:
        name += ".db"
    if os.path.isfile(Path(__file__).with_name(name)):
        if force is False:
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


def connect_to_db(name: str) -> Connection:
    """
    Tries to connect with the indicated database. Finishes execution if it can't connect.

    :param name str: Filename of the desired database. Expects an sqlite3 file.
    :rtype Connection: A functional sqlite3 connection, if the database connected.
    """
    conn = None
    try:
        conn = sqlite3.connect(Path(__file__).with_name(name))
        conn.execute("PRAGMA foreign_keys = 1")
        return conn
    except Error as e:
        print(e)
        sys.exit(1)


def list_databases() -> List:
    """
    Returns a list of every .db file in the same folder as the program.

    :rtype List: List of the filename of each .db file in the main folder, as strings.
    """
    cur = ""
    if os.path.isfile(Path(__file__).with_name("db.txt")):
        with open(Path(__file__).with_name("db.txt"), 'r') as f:
            cur = f.read()
    dir = Path(__file__).parents[0]
    files = list(Path(dir).glob('*.db'))
    if cur != "":
        print(f"Active: {cur}")
    for f in files:
        print(f)
    return files


def add_task(conn: Connection, task: str) -> int:
    """
    Adds a new task to the database, with the indicated name and the current date and time. Returns id of the task if created.

    :param conn Connection: Current sqlite3 connection.
    :param task str: Name/title of the current task.
    :rtype int: ID of the new task if it has been created sucessfully, -1 otherwise.
    """
    try:
        now = datetime.now()
        now = now.strftime("%m/%d/%Y, %H:%M:%S")
        sql = """INSERT INTO tasks(name) VALUES(?)"""
        cursor = conn.cursor()
        cursor.execute(sql, (task,))
        conn.commit()
        id = cursor.lastrowid
        print("Task added sucessfully")
        return id
    except Error as e:
        print(e)
        return -1


def remove_task_by_index(conn: Connection, index: int) -> bool:
    """
    Removes task with the indicated index if it exists on the current database.

    :param conn Connection: Current sqlite3 connection.
    :param index int: ID of the task to delete.
    :rtype bool: True if correctly deleted, False otherwise.
    """
    try:
        sql = "DELETE FROM tasks WHERE id=?"
        cursor = conn.cursor()
        cursor.execute(sql, (index,))
        conn.commit()
        print("Task deleted.")
        return True
    except Error as e:
        print(e)
        return False


def toggle_task(conn: Connection, id: int) -> Tuple[int, str, int]:
    """
    If the selected task is marked as completed, sets its as not completed and viceversa.

    :param conn Connection: Current sqlite3 connection.
    :param id int: Index of the task to toggle.
    :rtype Tuple[int, str, int]: Task with the selected ID.
    """
    sql = """UPDATE tasks SET completed = CASE WHEN completed = 0 THEN 1 else 0 END WHERE id = ?; """
    cursor = conn.cursor()
    cursor.execute(sql, (id,))
    conn.commit()
    return get_task_by_index(conn, id)


def start_task(conn: Connection, id: int) -> Tuple[int, str, int] | None:
    """
    Marks the starttime of the selected task as the current datetime, unless it's already not null.

    :param conn Connection: Current sqlite3 connection.
    :param id int: ID of the selected task.
    :rtype Tuple[int,str,int] | None: Task with the selected index, or None if the task was already started.
    """
    if len(get_task_by_index(conn, id)) == 0:
        print("Task does not exist.")
        return
    sql = "SELECT * from time where task_id=? and end_date is null"
    cursor = conn.cursor()
    cursor.execute(sql, (id,))
    result = cursor.fetchall()
    if len(result) != 0:
        print("This task is already open")
        return
    sql = "INSERT INTO time(start_date,task_id) VALUES(?,?)"
    now = datetime.now()
    now = now.strftime("%m/%d/%Y, %H:%M:%S")
    cursor.execute(sql, (now, id))
    conn.commit()
    print("This task is now open")
    return get_task_by_index(conn, id)


def stop_task(conn: Connection, id: int) -> Tuple[int, str, int] | None:
    if len(get_task_by_index(conn, id)) == 0:
        print("Task does not exist.")
        return
    sql = "SELECT * from time WHERE task_id=? AND end_date is null"
    cursor = conn.cursor()
    cursor.execute(sql, (id,))
    result = cursor.fetchall()
    if len(result) == 0:
        print("This task isn't open")
        return
    sql = "UPDATE time set end_date = ? where task_id=? and end_date is null"
    now = datetime.now()
    now = now.strftime("%m/%d/%Y, %H:%M:%S")
    cursor.execute(sql, (now, id))
    conn.commit()
    print("This task is now closed.")
    return get_task_by_index(conn, id)


def get_task_by_index(conn: Connection, id: int) -> Tuple[int, str, int]:
    """
    Returns task with the selected index.

    :param conn Connection: Current sqlite3 connection.
    :param id int: ID of the task to find.
    :rtype Tuple[int,str,int]: Task with the selected index with the format (id,name,completed).
    """
    sql = "SELECT * from tasks WHERE id=?"
    cursor = conn.cursor()
    cursor.execute(sql, (id,))
    tsk = cursor.fetchone()
    return tsk


def get_time(conn: Connection, id: int) -> str:
    """
    Returns total time spent on a task, if it has been started and stopped at least once.

    :param conn Connection: Current sqlite3 connection.
    :param id int: ID of the chosen task.
    :rtype str: Total time spent as a string formatted as H:MM:SS, or Not Started.
    """
    sql = "SELECT * from time WHERE task_id=?"
    cursor = conn.cursor()
    cursor.execute(sql, (id,))
    result = cursor.fetchall()
    diff = timedelta()
    if len(result) != 0:
        for r in result:
            (_, _, start_date, end_date) = r
            startTime = datetime.strptime(
                start_date, "%m/%d/%Y, %H:%M:%S") if start_date else timedelta()
            endTime = datetime.strptime(
                end_date, "%m/%d/%Y, %H:%M:%S") if end_date else startTime
            diff += endTime-startTime
        return str(diff)
    else:
        return "Not started"


def get_all_tasks(conn: Connection) -> List:
    """
    Returns list of all tasks.

    :param conn Connection: Current sqlite3 connection
    :rtype List: List of all tasks in the current database.
    """
    sql = "SELECT * FROM tasks"
    cursor = conn.cursor()
    cursor.execute(sql)
    return cursor.fetchall()


def add_comment(conn: Connection, id: int, comment: str) -> int | None:
    """
    Adds a comment to the chosen task, if it exists.

    :param conn Connection: Current sqlite3 connection.
    :param id int: ID of the chosen task.
    :param comment str: Content of the comment you want to add.
    :rtype int | None: id of the created comment, or None if task doesn't exist.
    """
    if len(get_task_by_index(conn, id)) == 0:
        print("Task does not exist.")
        return
    sql = """INSERT INTO comments(task_id,body) VALUES(?,?)"""
    cursor = conn.cursor()
    cursor.execute(sql, (id, comment))
    conn.commit()
    id = cursor.lastrowid
    print("Comment added sucessfully.")
    return id


def get_comments_by_task_index(conn: Connection, id: int) -> List:
    """
    Returns all comments of a single task.

    :param conn Connection: Current sqlite3 connection.
    :param id int: ID of the chosen task.
    :rtype List: List of all comments from the chosen task.
    """
    if len(get_task_by_index(conn, id)) == 0:
        print("Task does not exist.")
        return []
    sql = "SELECT * FROM comments WHERE task_id = ?"
    cursor = conn.cursor()
    cursor.execute(sql, (id,))
    return cursor.fetchall()


def delete_comment(conn: Connection, comment_id: int) -> bool:
    """
    Deletes comment with the chosen comment id.

    :param conn Connection: Current sqlite3 connection.
    :param comment_id int: ID of the chosen comment
    :rtype bool: True if the comment has been deleted, False otherwise.
    """
    try:
        sql = "DELETE FROM COMMENTS WHERE id=?"
        cursor = conn.cursor()
        cursor.execute(sql, (comment_id,))
        conn.commit()
        print("Comment deleted")
        return True
    except Exception as e:
        print(f"Something went wrong while deleting the comment: {e}")
        return False


def close_connection(conn: Connection):
    """
    Closes current connection.

    :param conn Connection: Connection to close.
    """
    if conn:
        conn.close()
        return True
    return False


def cleanup():
    """
    Deletes all .db files on the main folder, plus the db.txt file if it exists.

    """
    print(
        "This will delete all databases, active or otherwise. Do you wish to continue? [y/N]")
    answer = input().lower()
    if answer == "n":
        return
    if os.path.isfile(Path(__file__).with_name("db.txt")):
        os.remove(Path(__file__).with_name("db.txt"))
    dir = Path(__file__).parents[0]
    files = list(Path(dir).glob('*.db'))
    for f in files:
        os.remove(f)


# TODO: Rewrite this with Jinja2.
def generate_month_report(conn: Connection):
    """
    Deprecated: Will be rewritten.

    :param conn Connection: [TODO:description]
    """
    print("Generating report...")
    dates = []
    sql = "SELECT * from time WHERE start_date is not null and end_date is not null"
    cursor = conn.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    for _, task_id, start, end in result:
        startTime = datetime.strptime(start, "%m/%d/%Y, %H:%M:%S")
        endTime = datetime.strptime(end, "%m/%d/%Y, %H:%M:%S")
        month = startTime.strftime("%B")
        diff = endTime - startTime
        dates.append((month, task_id, startTime, endTime, diff))
    dates = sorted(dates, key=lambda month: month[0], reverse=True)
    months = set([a[0] for a in dates])
    rep = Report()
    month_lookup = list(month_name)
    for m in sorted(months, key=month_lookup.index):
        tasks = [a for a in dates if a[0] == m]
        monthtotal = timedelta()
        rep.add_month(m.upper())
        for t in tasks:
            task = get_task_by_index(conn, t[1])[0]
            total = t[3] - t[2]
            monthtotal += total
            rep.add_task(task[1], t[2], t[3], total)
        rep.add_total(monthtotal)
        rep.close_report()
    print("Report generated. Opening now.")
    webbrowser.open('file://' + os.path.realpath('report.html'))


def main():
    parser = argparse.ArgumentParser(prog='taskminal')
    subparsers = parser.add_subparsers(
        title="Action", help="The action to run.", required=True, dest="command")

    parser_create = subparsers.add_parser(
        "createdb", help="Create a new database")
    parser_create.add_argument("name", help="Name of the new database.")
    parser_create.add_argument(
        "-f", action="store_true", help="Force the creation of this database even if it already exists.")

    parser_connect = subparsers.add_parser(
        "set", help="Sets an active database.")
    parser_connect.add_argument(
        "name", help="Name of the database you want to use.")

    subparsers.add_parser("listdb", help="Shows all created databases")

    parser_add_task = subparsers.add_parser(
        "new", aliases=["add"], help="Adds a new task")
    parser_add_task.add_argument("title", help="Name of the task")
    parser_add_task.add_argument(
        "-s", action="store_true", help="Automatically start the task after adding it.")

    parser_list = subparsers.add_parser("list", help="Lists all tasks")
    group = parser_list.add_mutually_exclusive_group()
    group.add_argument("-c", action="store_true",
                       help="Show only completed tasks.")
    group.add_argument("-u", action="store_true",
                       help="Show only unfinished tasks.")
    parser_list.add_argument("-nc", action="store_true",
                             help="Don't show comments.")

    parser_delete = subparsers.add_parser(
        "delete", aliases=['remove'], help="Removes a task by its index.")
    parser_delete.add_argument(
        "index", help="Index of the task you want to remove.")

    parser_start = subparsers.add_parser(
        "start", help="Marks the current date/time as the start point for this session. Call stop when you're done with this task for now.")
    parser_start.add_argument(
        "index", help="Index of the task you want to update.")

    parser_stop = subparsers.add_parser(
        "stop", help="Stops working on this task.")
    parser_stop.add_argument("index", help="Task index")

    parser_complete = subparsers.add_parser(
        "done", help="Completes the task with the given index.")
    parser_complete.add_argument("index", help="Index of the task.")

    parser_comment = subparsers.add_parser(
        "comment", help="Adds or removes comments from your tasks.")
    comment_action = parser_comment.add_subparsers(
        title="Action", help="Add or remove comments from your tasks.", required=True, dest="comment_action")
    parser_comment_add = comment_action.add_parser(
        "add", help="Add a new comment to the selected task.")
    parser_comment_add.add_argument("id", help="ID of the desired task.")
    parser_comment_add.add_argument(
        "body", help="Text of the comment you want to add.")

    parser_comment_delete = comment_action.add_parser(
        "delete", help="Delete a comment by its unique id.")
    parser_comment_delete.add_argument(
        "comment", help="Index of the comment you want to delete.")

    subparsers.add_parser(
        "cleanup", help="Deletes every database file. Run this before uninstalling.")

    subparsers.add_parser("report", help="Generates a monthly time report")

    conn = None

    args = parser.parse_args(args=None if sys.argv[1:] else ['--help'])
    if args.command == "createdb":
        init_new_database(args.name, args.f)
    elif args.command == "listdb":
        list_databases()
    elif args.command == "set":
        if args.name.endswith(".db") is False:
            args.name += ".db"
        if os.path.isfile(Path(__file__).with_name(args.name)):
            with open(Path(__file__).with_name("db.txt"), "w") as f:
                f.write(args.name)
            print("Database selected.")
        else:
            print("Can't find database")
    elif args.command == "cleanup":
        cleanup()
    else:
        if os.path.isfile(Path(__file__).with_name("db.txt")):
            with open(Path(__file__).with_name("db.txt"), 'r') as f:
                conn = connect_to_db(f.read())
        else:
            print("There's no active database.")
            sys.exit(0)
        if args.command == "new" or args.command == "add":
            id = add_task(conn, args.title)
            if args.s:
                start_task(conn, id)
        elif args.command == "list":
            tasks = get_all_tasks(conn)
            for t in tasks:
                (index, name, completed) = t
                if completed == 0 and args.c or completed == 1 and args.u:
                    continue
                checkmark = "✔" if completed else ""
                print(('[{0}] - {1} [{2}]\nTime spent: {3}').format(index,
                      name, checkmark, get_time(conn, index)))
                if len(get_comments_by_task_index(conn, index)) > 0 and args.nc is False:
                    print("Comments:")
                    for c in get_comments_by_task_index(conn, index):
                        print(('[{0}] {1}').format(c[0], c[2]))
                print("---------")
        elif args.command == "delete" or args.command == "remove":
            remove_task_by_index(conn, args.index)
        elif args.command == "start":
            start_task(conn, args.index)
        elif args.command == "stop":
            stop_task(conn, args.index)
        elif args.command == "done":
            stop_task(conn, args.index)
            toggle_task(conn, args.index)
        elif args.command == "comment":
            if args.comment_action == "add":
                add_comment(conn, args.id, args.body)
            elif args.comment_action == "delete":
                delete_comment(conn, args.comment)
        elif args.command == "report":
            # FIXME: Deprecated, rewrite.
            print("Currently disabled.")
            # generate_month_report(conn)
        close_connection(conn)


if __name__ == "__main__":
    main()
