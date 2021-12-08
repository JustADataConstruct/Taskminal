import pytest
from datetime import datetime
import os

from taskminal import * 

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
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    assert cursor.fetchall() == [('tasks',), ('time',), ('comments',),]

def test_can_add_task():
    conn = connect_to_db("test.db")
    result = add_task(conn,'Test')
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

def test_can_start_task():
    conn = connect_to_db("test.db")
    start_task(conn,1)
    time = get_time(conn,1)
    assert time != 0

def test_can_stop_task():
    conn = connect_to_db("test.db")
    stop_task(conn,1)
    time = get_time(conn,1)
    assert time != 0

def test_can_complete_task():
    conn = connect_to_db("test.db")
    now = datetime.now()
    now = now.strftime("%m/%d/%Y, %H:%M:%S")
    task = add_task(conn,'Test')
    (id,name,completed) = toggle_task(conn,task)[0]
    assert completed == 1

def test_can_add_comment():
    conn = connect_to_db("test.db")
    id = add_task(conn,"Test")
    comment = add_comment(conn,id,"test comment")
    assert comment != None

def test_can_get_comments():
    conn = connect_to_db("test.db")
    add_comment(conn,1,"test2")
    comments = get_comments_by_task_index(conn,1)
    assert len(comments) != 0

def test_can_delete_comments():
    conn = connect_to_db("test.db")
    print(get_comments_by_task_index(conn,1))
    delete_comment(conn,1,2)
    comments = get_comments_by_task_index(conn,1)
    assert len(comments) == 0

def test_can_close_connection():
    conn = connect_to_db("test.db")
    conn = close_connection(conn)
    assert conn == None



"""
TODO: subtasks?

"""

def teardown_module():
    if os.path.isfile("test.db"):
        os.remove("test.db")
