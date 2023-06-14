from server import show_clients, show_client, shutdown, show_server_status
from lib_cli import create_menu, clear_terminal, show_help_menu

CLI_ARGS = {}
CLI_COMMANDS = [
    {
        "Commands": ["clients", "show_clients"],
        "Description": "Displays an overview of all clients connected to the server.",
        "Function": show_clients,
        "Parameters": []
    },
    {
        "Commands": ["client", "show_client"],
        "Description": "Displays an overview of the connected client at the given index.",
        "Function": show_client,
        "Parameters": []
    },
    {
        "Commands": ["sstat", "server_status"],
        "Description": "Displays server status.",
        "Function": show_server_status,
        "Parameters": []
    },
]

CLI_DEFAULT_COMMANDS = []
CLI_DEFAULT_COMMANDS = [
    {
        "Commands": ["help", "h", "?", "--help", "-h"],
        "Description": "Displays help menu",
        "Function": show_help_menu,
        "Parameters": []
    },
    {
        "Commands": ["clear", "cls"],
        "Description": "Clears the terminal",
        "Function": clear_terminal,
        "Parameters": []
    },
    {
        "Commands": ["back", "return"],
        "Description": "Exits the current menu",
        "Function": lambda: "break",
        "Parameters": []
    },
    {
        "Commands": ["exit", "quit", "kill", "q"],
        "Description": "Exits the program",
        "Function": shutdown,
        "Parameters": []
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