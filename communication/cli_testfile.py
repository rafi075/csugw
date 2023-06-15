import random
import string
import time
from lib_cli import print_array, color, bold, underline, print_dict, message, table, MAX_WIDTH, get_user_input, line, indent, timer, input_loop
from node import *

data = {
    "words": ["hello", "world", "great", "day",],
    "numbers": [1, 2, 3, 4, 5, 6, 7],
    "days": [
        ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        [1, 2, 3, 4, 5, 6, 7],
        [8, 9, 10, 11, 12, 13, 14]
    ],
    "users" : [
        {'name': 'Alice', 'age': 25},
        {'name': 'Bob', 'age': 30}
    ]
}

def table_test():
    message("Table Test", width=MAX_WIDTH)
    for key,value in data.items():
        table(value, verbose=True, indent_level=1, ansi=False)

def print_test():
    message("Print Test", width=MAX_WIDTH)
    print("Array / List")
    print_array(data["days"], indentation_level=1)
    print("\n Dict")
    print_dict(data, indentation_level=1)

def color_test():
    message("Color Test", width=MAX_WIDTH)
    colors = ["red", "yellow", "green", "cyan", "blue", "orange"]
    for c in colors:
        print("\t", f'{color(c, "Hello World"):<30}')

def bold_test():
    message("Bold Test", width=MAX_WIDTH)
    print("\t"+bold("Hello World") + "\t --> \tHello World")

def underline_test():
    message("Underline Test", width=MAX_WIDTH)
    print("\t"+underline("Hello World") + "\t --> \tHello World")

def line_test():
    message("Line Test", width=MAX_WIDTH)
    line(verbose=True)

def message_test():
    message("Message Test", width=MAX_WIDTH)
    a = ""
    a += message("Message, width=100", width=80, verbose=False)
    a += message("width=60",width=60, verbose=False)
    a += message("width=40",width=40, verbose=False)
    a += message("width=20",width=20, verbose=False)
    print(indent(a, 1))

def timer_test():
    message("Timer Test", width=MAX_WIDTH)

    @timer
    def temp_test(n):
        time.sleep(n)
        return "temp_test() = Done"

    message("Sleeping for 2 seconds", width=40)
    result = temp_test(2)
    message("Sleeping for 1 seconds", width=40)
    result = temp_test(1)
    message("Sleeping for 0.25 seconds", width=40)
    result = temp_test(0.25)

def user_input_test():
    message("User Input Test", width=MAX_WIDTH)
    value = get_user_input("Enter Something")
    print("\t", value)

def node_test():
    def random_char(y):
        return ''.join(random.choice(string.ascii_letters) for x in range(y))
    
    def show_nodes(**kwargs):
        for i in range(2):
            node = Node(
                ID=f"Node{i}",
                tags=[random_char(random.randint(1, 5)) for x in range(5)],
                IP=".".join(map(str, (random.randint(10, 255) for _ in range(4)))),
                PORT=random.randint(1000, 9000),
            )
            node.show(**kwargs)
            print()
        print("\n")

    message("Node Test- show(compact=False)", width=MAX_WIDTH)
    show_nodes(compact=False)
    message("Node Test- show()", width=MAX_WIDTH)
    show_nodes()
    message("Node Test- show(basic=True)", width=MAX_WIDTH)
    show_nodes(basic=True)

def cli_test():
    """    
    commands = [
        ["underline", underline_test],
        ["bold", bold_test],
        ["color", color_test],
        ["line", line_test],
        ["table", table_test],
        ["message", message_test],
        ["timer", timer_test],
    ]

    commands = [
        {
            "Commands": ["underline", "underline_test"],
            "Description": "description",
            "Function": underline_test,
            "Parameters": []
        },
        {
            "Commands": ["bold", "bold_test"],
            "Description": "description",
            "Function": bold_test,
            "Parameters": []
        },
        {
            "Commands": ["color", "color_test"],
            "Description": "description",
            "Function": color_test,
            "Parameters": []
        },
        {
            "Commands": ["line", "line_test"],
            "Description": "description",
            "Function": line_test,
            "Parameters": []
        },
        {
            "Commands": ["table", "table_test"],
            "Description": "description",
            "Function": table_test,
            "Parameters": []
        },
        {
            "Commands": ["message", "message_test"],
            "Description": "description",
            "Function": message_test,
            "Parameters": []
        },
        {
            "Commands": ["timer", "timer_test"],
            "Description": "description",
            "Function": timer_test,
            "Parameters": []
        },
        {
            "Commands": ["user_input", "user_input_test"],
            "Description": "description",
            "Function": user_input_test,
            "Parameters": []
        }
    ]

    help_commands = [{}]
    help_commands = [
        {
            "Commands": ["help", "h", "?", "--help", "-h"],
            "Description": "Displays this help menu",
            "Function": create_menu,
            "Parameters": [help_commands]
        },
        {
            "Commands": ["clear", "cls"],
            "Description": "Clears the terminal",
            "Function": clear_terminal,
            "Parameters": []
        },
        {
            "Commands": ["exit", "quit"],
            "Description": "Exits the program",
            "Function": exit,
            "Parameters": []
        }
    ]
    """

    message("CLI Test", width=MAX_WIDTH)
    input_loop()
    # table(commands, headers=["Command", "Function"])
    # input_loop(commands)

# underline_test()
# bold_test()
# color_test()
# line_test()
# table_test()
# message_test()
# timer_test()
node_test()
# user_input_test()
# cli_test()