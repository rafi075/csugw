import argparse
import sys

sys.path.append("..")
from client import Client
from server import Server
import lib_cli as CLI
from protocol import *
from attack import attack_lib

DEFAULT_GATEWAY = "10.1.1.1"

bDoubled = False


def program_arguments():
    parser = argparse.ArgumentParser(
        description="This is a program that accepts IP address and Port number"
    )
    parser.add_argument(
        "-ip",
        "--IPv4Address",
        type=str,
        default=DEFAULT_GATEWAY,
        help="An IPv4 address in the format xxx.xxx.xxx.xxx",
    )
    parser.add_argument("-p", "--Port", type=int, default=5000, help="A port number")
    parser.add_argument(
        "-id", "--id", type=str, default="Client1", help="The id of the client"
    )
    return parser.parse_args()


# def send_hook(client: Client, obj: socket.socket, message: Protocol or str):
#     CLI.message_ok("Send Hook", colr="BlueViolet")
#     client.send(message)
#     return False


# def receive_hook(client: Client, obj: socket.socket, message: Protocol or str):
#     CLI.message_ok("Receive Hook", colr="BlueViolet")

#     # if attack_lib():
#     #     return False

#     if message == ProtocolMethod.DEMO:
#         # Double the number received
#         number = int(message.content)
#         response = number * 2
#         message.content= f"{response}"

#         # Send the doubled number back to the client
#         client.send(message)

#     return False


def send_hook(client: Client, obj: socket.socket, message: Protocol or str):
    return False


def receive_hook(client: Client, obj: socket.socket, message: Protocol or str):
    return False


client = Client(
    "DefaultID",
    host="10.1.1.1",
    port=5000,
    send_hook=send_hook,
    receive_hook=receive_hook,
)

client.run()


def send_hook(server: Server, client: Node, message: Protocol or str):
    return False


def receive_hook(server: Server, client: Node, message: Protocol or str):
    return False


# server = Server(
#     host="10.1.1.1", port=5000, send_hook=send_hook, receive_hook=receive_hook
# )

# server.run()

