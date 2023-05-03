

from time import time
from uuid import uuid4


def create_todo_list(todo_array):
    formatted_list = []
    for todo in todo_array:
        formatted_list.append(
            "   {}  -  {}".format(todo['todo'], todo['time']))
    return "\n".join(formatted_list)


def update_todo_list(todo_array):
    for todo in todo_array:
        todo['id'] = str(uuid4())
        todo['timecreated'] = str(time())
    return todo_array
