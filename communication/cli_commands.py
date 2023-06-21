from server import Server
from lib_cli import create_menu, clear_terminal, show_help_menu

# CLI_ARGS = {}
CLI_COMMANDS = [
    {
        "Commands": ["clients", "show_clients"],
        "Description": "Displays an overview of all clients connected to the server.",
        "Function": Server.show_clients,
        "Parameters": 0,
    },
    {
        "Commands": ["client", "show_client"],
        "Description": "Displays an overview of the connected client at the given index.",
        "Function": Server.show_client,
        "Parameters": 1,
    },
    {
        "Commands": ["exit", "kill"],
        "Description": "Terminates all clients and the server",
        "Function": Server.shutdown,
        "Parameters": 0,
    },
]

CLI_DEFAULT_COMMANDS = []
CLI_DEFAULT_COMMANDS = [
    {
        "Commands": ["help", "h", "?", "--help", "-h"],
        "Description": "Displays help menu",
        "Function": Server.show_help_menu,
        "Parameters": 0,
    },
    {
        "Commands": ["clear", "cls"],
        "Description": "Clears the terminal",
        "Function": clear_terminal,
        "Parameters": 0,
    },
    {
        "Commands": ["back", "return"],
        "Description": "Exits the current menu",
        "Function": lambda: "break",
        "Parameters": 0,
    },
    {
        "Commands": ["exit", "quit", "kill", "q"],
        "Description": "Exits the program",
        "Function": Server.shutdown,
        "Parameters": 1,
    },
]


# CLI_TEST_COMMANDS = [
#     {
#         "Commands": ["show clients", "clients"],
#         "Description": "Displays an overview of all clients connected to the server.",
#         "Function": show_clients,
#         "Parameters": []
#     },
#     {
#         "Commands": ["show client", "client"],
#         "Description": "Displays an overview of the connected client at the given index.",
#         "Function": show_client,
#         "Parameters": [CLI_ARGS["show_client_index"]]
#     },
#         {
#             "Commands": ["underline", "underline_test"],
#             "Description": "description",
#             "Function": underline_test,
#             "Parameters": []
#         },
#         {
#             "Commands": ["bold", "bold_test"],
#             "Description": "description",
#             "Function": bold_test,
#             "Parameters": []
#         },
#         {
#             "Commands": ["color", "color_test"],
#             "Description": "description",
#             "Function": color_test,
#             "Parameters": []
#         },
#         {
#             "Commands": ["line", "line_test"],
#             "Description": "description",
#             "Function": line_test,
#             "Parameters": []
#         },
#         {
#             "Commands": ["table", "table_test"],
#             "Description": "description",
#             "Function": table_test,
#             "Parameters": []
#         },
#         {
#             "Commands": ["message", "message_test"],
#             "Description": "description",
#             "Function": message_test,
#             "Parameters": []
#         },
#         {
#             "Commands": ["timer", "timer_test"],
#             "Description": "description",
#             "Function": timer_test,
#             "Parameters": []
#         },
#         {
#             "Commands": ["user_input", "user_input_test"],
#             "Description": "description",
#             "Function": user_input_test,
#             "Parameters": []
#         }
#     ]
