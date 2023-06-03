from lib_cli import *


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
    message("Table Test")
    for key,value in data.items():
        table(value, verbose=True, indent_level=1, ansi=False)

def print_test():
    message("Print Test")
    print("Array / List")
    print_array(data["days"], indentation_level=1)
    print("\n Dict")
    print_dict(data, indentation_level=1)

def color_test():
    message("Color Test")
    colors = ["red", "yellow", "green", "cyan", "blue", "orange"]
    for c in colors:
        print("\t", f'{color(c, "Hello World"):<30}')

def bold_test():
    message("Bold Test")
    print("\t"+bold("Hello World") + "\t --> \tHello World")

def underline_test():
    message("Underline Test")
    print("\t"+underline("Hello World") + "\t --> \tHello World")

def line_test():
    message("Line Test")
    line(verbose=True)

def message_test():
    message("Message Test")
    a = ""
    a += message("Message, width=100", width=80, verbose=False)
    a += message("width=60",width=60, verbose=False)
    a += message("width=40",width=40, verbose=False)
    a += message("width=20",width=20, verbose=False)
    print(indent(a, 1))

def timer_test():
    message("Timer Test")

    @timer
    def temp_test(n):
        time.sleep(n)
        return "temp_test() = Done"

    message("Sleeping for 5 seconds", width=40)
    result = temp_test(5)
    message("Sleeping for 4 seconds", width=40)
    result = temp_test(4)
    message("Sleeping for 3 seconds", width=40)
    result = temp_test(3)
    message("Sleeping for 1 seconds", width=40)
    result = temp_test(1)


underline_test()
bold_test()
color_test()
line_test()
table_test()
message_test()
timer_test()


