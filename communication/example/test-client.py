import argparse
import sys
sys.path.append("..")
from client import Client
import lib_cli as CLI
from protocol import *
from attack import attack_lib

DEFAULT_GATEWAY = "10.1.1.1"

bDoubled = False
def program_arguments():
    parser = argparse.ArgumentParser(
        description="This is a program that accepts IP address and Port number"
    )
    parser.add_argument("-ip","--IPv4Address",type=str,default=DEFAULT_GATEWAY,help="An IPv4 address in the format xxx.xxx.xxx.xxx",)
    parser.add_argument("-p", "--Port", type=int, default=5000, help="A port number")
    parser.add_argument("-id", "--id", type=str, default="Client1", help="The id of the client")
    return parser.parse_args()


def custom_logic(obj: Client, client: Node, message: Protocol or str):
    global bDoubled
    CLI.message_ok("CUSTOM LOGIC", colr="BlueViolet")

    # if attack_lib():
    #     return False

    if message == ProtocolMethod.DEMO and not bDoubled:
        # Show custom logic is being ran
        CLI.message_ok(f"DEMO {message.content}", colr="BlueViolet")

        # Double the number received
        number = int(message.content)
        response = number * 2
        message.content= f"{response}"

        # Send the doubled number back to the client
        obj.send(message)

        bDoubled = True

    return False


args = program_arguments()

client = Client(args.id, 
                host=args.IPv4Address, 
                port=args.Port, 
                custom_logic=custom_logic)

client.run()