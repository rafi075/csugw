#!/bin/python3
import argparse
import json
import select
import selectors
import socket
import sys
import threading
from random import randrange
import traceback

import jsonschema

import lib_cli as CLI

from protocol import (
    Protocols,
    Protocol,
    ProtocolState,
    ProtocolMethod,
    ProtocolType,
    Field,
)


LOG_PADDING = 0
LOG = False


class Client:
    def __init__(self, client_id: str, host="127.0.0.1", port=5000):
        self.id = client_id
        self.running = True
        self.print_lock = threading.Lock()
        self.exit_event = threading.Event()
        self.initialized = False
        self.sock = None

        self.selector_sock = selectors.DefaultSelector()
        self.selector_input = selectors.DefaultSelector()

        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(1.0)
            self.sock.connect((host, port))
        except socket.error as err:
            print(str(err))

    def print_message(self, *args, **kwargs):
        kwargs = {**{"sep": " ", "end": "\n"}, **kwargs}
        msg = "".join(str(arg) + kwargs["sep"] for arg in args)
        msg = CLI.color(kwargs["clr"], msg) if "clr" in kwargs else msg
        kwargs.pop("clr", "")
        with self.print_lock:
            print(msg, **kwargs)

    def disconnect(self):
        self.send_data(Protocols.DISCONNECT.msg())
        self.running = False
        self.exit_event.set()

    def process_message(self, message: Protocol, is_receiving=False):
        if not message:
            self.print_message("Empty Message", clr="red")
            print(message.__str__())
            return False

        if message == Protocols.INITIALIZE:
            if not self.initialized:
                self.send_data(Protocols.INITIALIZE)
                self.initialized = True
            else:
                self.print_message(
                    CLI.message("Initialization Successful", "green", verbose=False)
                )
            return False

        if message == Protocols.DISCONNECT:
            self.disconnect()
            return True

        elif not is_receiving:
            self.send_data(message)
            return False

    def receive(self):
        self.selector_sock.register(self.sock, selectors.EVENT_READ, self.receive_data2)
        while not self.exit_event.is_set():
            events = self.selector_sock.select(timeout=0)
            try:
                for key, mask in events:
                    callback = key.data
                    callback(key.fileobj, mask)

            except socket.timeout:
                continue
            except KeyboardInterrupt:
                self.sock.close()
                break
            except Exception as err:
                self.print_message("An error occured!", clr="gray")
                self.print_message(traceback.format_exc())
                self.print_message(err)
                self.sock.close()
                self.running = False
                break

    def command_line(self):
        while not self.exit_event.is_set():
            try:
                if self.is_active(sys.stdin):
                    message = input()
                    if Protocol.has_key(message, ProtocolMethod):
                        message = Protocol(method=message)
                        if self.process_message(message, is_receiving=False):
                            break
                    else:
                        print("Invalid METHOD:\t", f'"{message}"\n')
            except KeyboardInterrupt:
                break
            except ValueError:
                break
            except Exception as err:
                self.print_message("An error occured!", clr="red")
                self.print_message(traceback.format_exc())
                self.print_message(err)
                self.sock.close()
                self.running = False
                break

    def is_active(self, stream, timeout=1):
        ready, _, _ = select.select([stream], [], [], timeout)
        return ready

    def send_data(self, message, sign: bool = True, encoding: str = "ascii"):
        if type(message) is Protocol:
            message = message.to_network(encoding=encoding)
            self.log_send(message)
            self.sock.send(message)

    def receive_data(
        self, buffer_size: int = 1024, decoding: str = "ascii"
    ) -> Protocol:
        if not self.sock:
            return ""

        message = self.sock.recv(buffer_size).decode(decoding)

        if len(message) == 0:
            print(
                "Emppty Message from ",
                self.get_socket_address(self.sock),
                f'"{message}"',
            )
            return ""

        print("Message", f'"{message}"')
        message: Protocol = Protocol.from_network(message)

        if message:
            formatted_message = r"{}".format(message)
            self.log_receive(formatted_message)
        return message

    def receive_data2(self, sock, mask):
        message = sock.recv(1024).decode("ascii")
        if not message:
            return

        message: Protocol = Protocol.from_network(message)

        if message:
            formatted_message = r"{}".format(message)
            self.log_receive(formatted_message)
        self.process_message(message, is_receiving=True)

    def log_send(self, message):
        if LOG:
            output = f"[LOG] {CLI.color('steelblue', 'SENDING:')}\n"
            output += f'{self.get_socket_address(self.sock)} {"-->"} {str(message):<{LOG_PADDING}}\n'
            self.print_message(output, clr="gray")

    def log_receive(self, message):
        if LOG:
            output = f"[LOG] {CLI.color('tomato', 'RECEIVED:')}\n"
            output += f'{self.get_socket_address(self.sock)} {"<--"} {str(message):<{LOG_PADDING}}\n'
            self.print_message(output, clr="gray")

    def get_socket_address(self, socket_obj: socket.socket) -> str:
        peer_name = socket_obj.getpeername()
        return f"{str(peer_name[0])} : {str(peer_name[1])}"

    def run(self):
        receive_thread = threading.Thread(target=self.receive)
        write_thread = threading.Thread(target=self.command_line)

        receive_thread.start()
        write_thread.start()

        for thread in [receive_thread, write_thread]:
            try:
                thread.join()
            except KeyboardInterrupt:
                self.exit_event.set()
            except Exception as err:
                print(err.with_traceback())
                self.exit_event.set()


def get_args():
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


if __name__ == "__main__":
    args = get_args()
    CLI.clear_terminal()
    client_id = str(randrange(0, 1000))
    client = Client(client_id, host=args.IPv4Address, port=args.Port)
    client.run()
    exit(0)
