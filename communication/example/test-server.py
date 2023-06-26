import argparse
import sys
sys.path.append("..")
from server import Server
import lib_cli as CLI
from protocol import *


def program_arguments():
    parser = argparse.ArgumentParser(
        description="This is a program that accepts IP address and Port number"
    )
    parser.add_argument(
        "-ip",
        "--IPv4Address",
        type=str,
        default="127.0.0.1",
        help="An IPv4 address in the format xxx.xxx.xxx.xxx",
    )
    parser.add_argument("-p", "--Port", type=int, default=5000, help="A port number")
    return parser.parse_args()


def custom_logic(obj: Server, client: Node, message: Protocol or str):
    CLI.message_ok("CUSTOM LOGIC", colr="BlueViolet")

    if message == ProtocolMethod.TEST:
        CLI.message_ok("TEST", colr="BlueViolet")
        obj.send(client, message)
        return False
    elif message[Field.BODY] == "Client Confirmed":
        CLI.message_ok("CLIENT CONFIRMED", colr="BlueViolet")
        return False
    else:
        return False



args = program_arguments()
server = Server(host=args.IPv4Address, 
                port=args.Port, 
                custom_logic=custom_logic)

server.run()
