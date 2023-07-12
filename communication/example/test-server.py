import argparse
from random import randint
import sys
sys.path.append("..")
from server import Server
import lib_cli as CLI
from protocol import *

DEFAULT_GATEWAY = "10.1.1.1"

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
    return parser.parse_args()


def send_hook(server: Server, client: Node, message: Protocol or str):
    CLI.message_ok("Send Hook", colr="BlueViolet")

    if message == ProtocolMethod.DEMO:
        message.content = f"{randint(1, 100)}"

    server.send(client, message)

    return False


def receive_hook(server: Server, client: Node, message: Protocol or str):
    CLI.message_ok("Receive Hook", colr="BlueViolet")

    if message == ProtocolMethod.DEMO:
        # Show custom logic is being ran
        CLI.message_ok(f"DOUBLED: {message.content}", colr="BlueViolet")
    

    return False



args = program_arguments()

server = Server(host=args.IPv4Address, 
                port=args.Port, 
                send_hook=send_hook,
                receive_hook=receive_hook)


server.run()