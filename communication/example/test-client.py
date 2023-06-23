import argparse
from random import randint
import sys
import time

sys.path.append("..")
from client import Client
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


def drop_packet(chance):
    rand = randint(0, 100)
    if rand <= chance:
        CLI.message_error(f"PACKET DROPPED")
        return False
    
def ddos(length_of_attack:int):
    CLI.message_error(f"DDOS: {length_of_attack}")
    time.sleep(length_of_attack)

def attack_lib():
    rand = randint(0, 100)
    if rand <= 50:
        drop_packet(10)
    rand = randint(0, 100)
    if rand <= 50:
        ddos(10)

def custom_logic(obj: Client, client: Node, message: Protocol or str):

    attack_lib()

    if message == ProtocolMethod.TEST:
        CLI.message_ok("CUSTOM LOGIC - CLIENT TEST")
        obj.send(Protocol(content=f"TEST"))
        return False
    else:
        CLI.message_ok("CUSTOM LOGIC - CLIENT BASE CASE")
        return False


if __name__ == "__main__":
    args = program_arguments()
    client = Client(
        "Client1", 
        host=args.IPv4Address, 
        port=args.Port, 
        custom_logic=custom_logic
    )
    client.run()
