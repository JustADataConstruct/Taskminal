import pytest
import os

from taskminal import close_connection, init_new_database, connect_to_db,create_table

def test_can_create_a_new_database():
    db_created = init_new_database(True)
    assert db_created == True
    
@pytest.mark.skipif(os.path.isfile("taskminal.db") == False,reason="There's no file.")
def test_can_fail_to_create_if_already_exists():
    name = "taskminal.db"
    db_created = init_new_database(False)
    assert db_created == False

def test_can_connect_to_db():
    conn = connect_to_db()
    assert conn != None

def test_can_create_table():
    conn = connect_to_db()
    cursor = conn.cursor()
    create_table(conn,""" CREATE TABLE IF NOT EXISTS test (
                            id integer PRIMARY KEY,
                            name text);""")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    assert cursor.fetchall() == [('test',)]

def test_can_close_connection():
    conn = connect_to_db()
    conn = close_connection(conn)
    assert conn == None
