from server import Server
from lib_cli import create_menu, clear_terminal, show_help_menu


CLI_SERVER_COMMANDS = [
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
]


CLI_CLIENT_COMMANDS = [
    {
        "Commands": ["show", "sh"],
        "Description": "Shows connection",
        "Function": "display_network",
        "Parameters": 0,
    },
    {
        "Commands": ["script", "exec"],
        "Description": "Executes a bash script from /root/scripts/",
        "Function": "run_script",
        "Parameters": 1,
    },
    {
        "Commands": ["command", "./"],
        "Description": "Executes a bash command",
        "Function": "run_command",
        "Parameters": 1,
    },
]

CLI_DEFAULT_COMMANDS = []
CLI_DEFAULT_COMMANDS = [
    {
        "Commands": ["help", "h", "?"],
        "Description": "Displays help menu",
        "Function": "show_help_menu",
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
        "Commands": ["exit", "quit", "kill"],
        "Description": "Exits the program",
        "Function": "shutdown",
        "Parameters": 1,
    },
]
