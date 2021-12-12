
# Taskminal

1) An horrible pun. I'm truly sorry.
2) A CLI to-do list manager / time manager.
3) Seriously I'm so sorry about the name.

- [Features](#features)
- [Made with](#made-with)
- [Requeriments](#requeriments)
- [Installation](#installation)
- [Running Tests](#running-tests)
- [Usage](#usage)
  - [Create a Database](#create-a-database)
  - [Set a Database as Active](#set-a-database-as-active)
  - [List all Databases](#list-all-databases)
  - [Add a new Task](#add-a-new-task)
  - [List Tasks](#list-tasks)
  - [Delete Tasks](#delete-tasks)
  - [Logging Time](#logging-time)
  - [Complete a Task](#complete-a-task)
  - [Add Comments](#add-comments)
  - [Delete Comments](#delete-comments)
  - [Cleanup and Uninstall](#cleanup-and-uninstall)
  - [Report](#report)
- [Roadmap](#roadmap)
- [License](#license)


## Features

- Fully controllable with the keyboard, making it comfortable to use while writing or coding.
- Track the time you spend on each task with a few keystrokes.
- Add comments to each task, letting you put reminders or lists of subtasks.
- Export reports with your monthly work time, allowing you to see your most productive hours.
## Made with

- Python 3.9.7
- SQLite 3.36.0

## Requeriments
- Python 3.7 or higher.


## Installation

Clone the project

```bash
  git clone https://github.com/JustADataConstruct/Taskminal.git
```

Go to the project directory

```bash
  cd Taskminal
```

Install the project

```bash
  pip install .
```

Create your first database and set it as active.

```bash
  taskminal createdb <DATABASE NAME>
  taskminal set <DATABASE NAME>
```


## Running Tests

If you wish to test the code:
- Install pytest
```bash
pip install pytest
```
Move into the `taskminal` directory
```bash
cd taskminal
```
Run pytest
```bash
  pytest
```
Your output may vary depending on your pytest configuration and flags, but should be something similar to this:
```bash
============================= test session starts ==============================
collecting ... collected 15 items

tests/test_database.py::test_can_create_a_new_database PASSED            [  6%]
tests/test_database.py::test_can_fail_to_create_if_already_exists PASSED [ 13%]
tests/test_database.py::test_can_list_databases PASSED                   [ 20%]
tests/test_database.py::test_can_connect_to_db PASSED                    [ 26%]
tests/test_database.py::test_can_create_table PASSED                     [ 33%]
tests/test_database.py::test_can_add_task PASSED                         [ 40%]
tests/test_database.py::test_can_get_tasks PASSED                        [ 46%]
tests/test_database.py::test_can_remove_task PASSED                      [ 53%]
tests/test_database.py::test_can_start_task PASSED                       [ 60%]
tests/test_database.py::test_can_stop_task PASSED                        [ 66%]
tests/test_database.py::test_can_complete_task PASSED                    [ 73%]
tests/test_database.py::test_can_add_comment PASSED                      [ 80%]
tests/test_database.py::test_can_get_comments PASSED                     [ 86%]
tests/test_database.py::test_can_delete_comments PASSED                  [ 93%]
tests/test_database.py::test_can_close_connection PASSED                 [100%]

============================== 15 passed in 0.22s ==============================
```


## Usage

Run `taskminal -h` on the command line to see the usage.

```zsh
usage: taskminal [-h]
                 {createdb,set,listdb,new,add,list,delete,remove,start,stop,done,comment,cleanup,report}
                 ...

optional arguments:
  -h, --help            show this help message and exit

Action:
  {createdb,set,listdb,new,add,list,delete,remove,start,stop,done,comment,cleanup,report}
                        The action to run.
    createdb            Create a new database
    set                 Sets an active database.
    listdb              Shows all created databases
    new (add)           Adds a new task
    list                Lists all tasks
    delete (remove)     Removes a task by its index.
    start               Marks the current date/time as the start point for
                        this session. Call stop when you're done with this
                        task for now.
    stop                Stops working on this task.
    done                Completes the task with the given index.
    comment             Adds or removes comments from your tasks.
    cleanup             Deletes every database file. Run this before
                        uninstalling.
    report              Generates a monthly time report
```
## Create a Database
```zsh
taskminal createdb {DATABASE NAME} [-f]
```
The first action to do the first time you install Taskminal, and every time you want to move into a new database file.

Taskminal will create a new SQLite database with the chosen name.

Do notice that the database will not be selected as the current database until you do it manually.

This command will throw an error if a database with thet name already exists. You can use the `-f` flag to forcefully overwrite it.


## Set a Database as Active
```zsh
taskminal set {DATABASE NAME}
```
Selects a database as the active database. Most of the commands will not work until you've selected a database to work with.
## List all databases
```zsh
taskminal listdb
```
This command will print a list of any databases created, active or not.
## Add a new Task
```zsh
taskminal (new,add) {TASKNAME} [-s]
```
Adds a new Task to your database, with the indicated name.

You can use the `-s` flag to auto-start the task. Otherwise you'll need to call the `start` command (see below)

## List Tasks
```zsh
taskminal list [-h] [-c|-u] [-nc]
```
Shows a list of all the tasks in the current database, indicated by their index number, the time spent on each tasks, and the comments in that task, if any.
```zsh
[1] - Test [✔]
Time spent: Not started
---------
[2] - Test2 []
Time spent: 00:15:12
Comments:
[1] test comment
---------
```

You can use flags to alter this output. 
- The `-c` flag will only show completed tasks.
- The `-u` flag will only show unfinished tasks.
- The `-nc` flag will hide comments.
## Delete Tasks
```zsh
taskminal (delete,remove) {INDEX}
```
Deletes the task identified by the selected index, its time logs and any comments.

## Logging time
```zsh
taskminal start {INDEX}
taskminal stop {INDEX}
```
Opens and closes a time log segment.

When you start working on a task, call `start` on its index. The current time and date will be marked as the Task's start time.

Once you've finished working with this task for now, but it's not finished yet, call `stop`. The time and date will be marked as the end date and the time segment will be saved.

A Task's total spent time (as seen on `list`'s output) is the sum of the differences between each segment's start and end times.

You can have several tasks active at the same time.
## Complete a Task
```zsh
taskminal done {INDEX}
```
Closes this task's latest time segment if open, and marks the task with the indicated index as completed.
## Add Comments
```zsh
taskminal comment add {INDEX} {COMMENT}
```
Adds a new comment with the text COMMMENT on the task indicated by the INDEX.

The comments will be printed under this task when you run `list`.
## Delete Comments
```zsh
taskminal comment delete {COMMENT_INDEX}
```
Deletes the comment identified by its index, as seen on `list`'s output.

Please notice that this command requires **the comment's ID**, indepently of to what Task it is attached.
## Cleanup and Uninstall
```zsh
taskminal cleanup
```
This command must be ran only before uninstalling Taskminal, as it will delete every file it created outside of the installation process.

By default, this command will delete:

- The `db.txt` file. Taskminal uses this file to track the active database.
- Any files inside Taskminal's install directory with the `.db` extension.
## Report
```bash
taskminal report
```
This command will generate a simple HTML report showing how much time you allocated per month to each task.

Please notice that unless most commands, this command will generate a html file on your current working directory and not on Taskminal's install folder.
## Roadmap

- Better HTML reports.


## License

[MIT](https://choosealicense.com/licenses/mit/)

