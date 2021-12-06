import pytest
from datetime import datetime
import os

from taskminal import add_task, close_connection, init_new_database, connect_to_db,create_table, get_all_tasks, remove_task_by_index 

def test_can_create_a_new_database():
    db_created = init_new_database("test.db",True)
    assert db_created == True
    
def test_can_fail_to_create_if_already_exists():
    with open("test.db","w") as f:
        f.write("TEST")
    db_created = init_new_database("test.db",False)
    assert db_created == False

def test_can_connect_to_db():
    init_new_database("test.db",True)
    conn = connect_to_db("test.db")
    assert conn != None

def test_can_create_table():
    conn = connect_to_db("test.db")
    cursor = conn.cursor()
    create_table(conn,""" CREATE TABLE IF NOT EXISTS tasks (
                            id integer PRIMARY KEY,
                            name text NOT NULL,
                            completed integer DEFAULT FALSE,
                            start_date text NOT NULL,
                            end_date text);""")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    assert cursor.fetchall() == [('tasks',)]

def test_can_add_task():
    conn = connect_to_db("test.db")
    now = datetime.now()
    now = now.strftime("%m/%d/%Y, %H:%M:%S")
    result = add_task(conn,('Test',now))
    print("RESULT:", result)
    assert result != None

def test_can_get_tasks():
    conn = connect_to_db("test.db")
    result = get_all_tasks(conn)
    assert result != []

def test_can_remove_task():
    conn = connect_to_db("test.db")
    remove_task_by_index(conn,1)
    result = get_all_tasks(conn)
    assert result == []


def test_can_close_connection():
    conn = connect_to_db("test.db")
    conn = close_connection(conn)
    assert conn == None

"""
TODO: Complete tasks, commands, subtasks?

"""

def teardown_module():
    if os.path.isfile("test.db"):
        os.remove("test.db")
