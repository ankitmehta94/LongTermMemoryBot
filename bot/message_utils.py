

def create_todo_list(todo_array):
    formatted_list = []
    for todo in todo_array:
        formatted_list.append(
            "   {}  -  {}".format(todo['todo'], todo['time']))
    return "\n".join(formatted_list)
