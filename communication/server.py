#!/bin/python3

import json
import threading
import argparse
import socket
from inputimeout import inputimeout
import jsonschema
from protocol import (
    Protocols,
    Protocol,
    ProtocolState,
    ProtocolMethod,
    ProtocolType,
    Field,
)
from node import Node, HelpMenu
import lib_cli as CLI
import select
import sys

LOG_MESSAGE_SIZE = 75.0
LOG_PADDING = 0
LOG = True


class Server:
    def __init__(self, host="127.0.0.1", port=5000):
        self.host = host
        self.port = port
        self.clients = []
        self.threads = []
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host, self.port))
        self.server.listen()
        self.running = True
        self.locks = {
            "clients": threading.Lock(),
            "print": threading.Lock(),
            "thread": threading.Lock(),
        }
        self.exit_event = threading.Event()
        self.custom_commands = []

    def broadcast(self, message, exclude=None):
        if exclude and exclude in self.clients and len(self.clients) == 1:
            return
        if message != Protocols.INITIALIZE:
            with self.locks["clients"]:
                for client in self.clients:
                    if exclude != client:
                        self.send_data(client, message)

    def process_message(self, client, message: Protocol):
        # client_id, message = message.split(":") if ":" in message else ("null", "null")

        if message == Protocols.DISCONNECT:
            self.disconnect_client(client)
            return True
        if message == Protocols.SHOW:
            self.show_clients()
            return False

        if message[ProtocolType] == ProtocolType.BROADCAST:
            self.broadcast(f"{message}", exclude=client)
        return False

    def handle_client(self, client: Node):
        while not self.exit_event.is_set():
            try:
                ready_to_read, _, _ = select.select([client.socket], [], [], 1)
                if ready_to_read:
                    message = self.receive_data(client.socket)
                    if self.process_message(client, message):
                        break
            except Exception as e:
                # TODO: Exception thrown on DC
                # self.print_caution("Exception in handle_client")
                # self.print_thread(e)
                self.disconnect_client(client)
                break

    def receive(self):
        self.server.setblocking(False)
        while not self.exit_event.is_set():
            ready_to_read, _, _ = select.select([self.server], [], [], 1)
            if ready_to_read:
                client, address = self.server.accept()
                with self.locks["clients"]:
                    if address not in self.clients:
                        client_node = self.initialize_client(client)
                if client_node:
                    with self.locks["thread"]:
                        self.threads.append(
                            threading.Thread(
                                target=self.handle_client, args=(client_node,)
                            )
                        )
                        self.threads[-1].start()

    def initialize_client(self, client):
        self.send_data(client, Protocols.INITIALIZE)
        response = self.receive_data(client)
        if response == Protocols.DISCONNECT:
            client.shutdown(0)
            client.close()
            return

        # TODO: Implement AWK
        self.send_data(client, Protocols.INITIALIZE)
        client_node = Node(client, response["ID"])
        self.clients.append(client_node)
        CLI.line()
        self.print_ok(f"CLIENT CONNECTED: {str(client_node._strIPPORT)}")

        return client_node

    def send_data(self, client, message: Protocol, encoding="ascii"):
        addr = (
            CLI.color("aquamarine", client._strIPPORT)
            if type(client) is Node
            else self.get_socket_address(client)
        )
        self.log_send(message, addr)
        message = message.to_network(
            encoding=encoding, node=client if type(client) is Node else None
        )

        if type(client) is Node:
            client.socket.sendall(message)
        else:
            client.sendall(message)

    def receive_data(self, client, buff_size=1024, decoding="ascii") -> Protocol:
        message = client.recv(buff_size).decode(decoding)
        message: Protocol = Protocol.from_network(message)
        addr = (
            client._strIPPORT
            if type(client) is Node
            else self.get_socket_address(client)
        )
        self.log_receive(message, addr)
        return message

    def log_send(self, message, addr):
        if LOG:
            output = f"[LOG] {CLI.color('steelblue', 'SENDING:')}\n"
            output += f'{str(message):<{LOG_PADDING}} {"-->":<{LOG_PADDING}} {addr}\n'
            self.print_thread(output, clr="gray")

    def log_receive(self, message, addr):
        if LOG:
            output = f"[LOG] {CLI.color('tomato', 'RECEIVED:')}\n"
            output += f'{str(message):<{LOG_PADDING}} {"<--":<{LOG_PADDING}} {addr}\n'
            self.print_thread(output, clr="gray")

    def get_socket_address(self, socket_obj: socket.socket) -> str:
        peer_name = socket_obj.getpeername()
        return CLI.color("aquamarine", f"{str(peer_name[0])} : {str(peer_name[1])}")

    def disconnect_client(self, client: Node):
        try:
            self.send_data(client.socket, Protocols.DISCONNECT)
            client.close()
        except:
            pass
        with self.locks["clients"]:
            self.clients.remove(client)

        self.print_caution(f"CLIENT DISCONNECTED: {str(client._strIPPORT)}")
        # self.broadcast(f"\nLEFT: {client.ID}\n")

    def stop(self):
        message = Protocols.DISCONNECT
        message[ProtocolType] = ProtocolType.BROADCAST
        message[Field.ID] = "Server"

        self.print_caution("STOPPING SERVER...")
        self.broadcast(message)
        self.running = False
        self.exit_event.set()
        with self.locks["clients"]:
            for client in self.clients:
                client.close()

        with self.locks["thread"]:
            for thread in self.threads:
                if thread.is_alive() and thread != threading.current_thread():
                    thread.join()

        self.server.close()
        self.print_error("SERVER SHUTDOWN")

    def show_clients(self):
        if len(self.clients) == 0:
            self.print_error("NO CLIENTS CONNECTED")
            return

        client_info = []
        for node in self.clients:
            client_info.append(node.get_data())
        data = [list(client_info[0].keys())] + [
            list(entry.values()) for entry in client_info
        ]
        self.print_("Connected Clients")
        CLI.table(data, showindex=True)

    def show_client(self, client:int or str):
        if type(client) is str:
            for node in self.clients:
                if node.ID == client:
                    node.show()

        if str(client).isdigit():
            client = int(client)
            if client >=0 and client < len(self.clients):
                self.clients[client].show()
            else:
                self.print_error("INVALID CLIENT INDEX")

    def run(self):
        CLI.clear_terminal()
        self.print_ok(f"SERVER STARTED {self.host}:{self.port}")
        self.server.listen()
        self.threads.extend(
            [
                threading.Thread(target=self.receive),
                threading.Thread(target=self.command_line),
            ]
        )
        [thread.start() for thread in self.threads]

        for thread in self.threads:
            try:
                # thread.start()
                thread.join()
            except KeyboardInterrupt:
                break
            except Exception as e:
                self.print_error("SERVER ERROR")
                print(e)

        # self.stop()

    def print_thread(self, *args, **kwargs):
        kwargs = {**{"sep": " ", "end": "\n"}, **kwargs}
        msg = "".join(str(arg) + kwargs["sep"] for arg in args)
        msg = CLI.color(kwargs["clr"], msg) if "clr" in kwargs else msg
        kwargs.pop("clr", "")
        with self.locks["print"]:
            print(msg, **kwargs)

    def print_error(self, message):
        self.print_thread(
            CLI.message(message, "red", verbose=False, width_fraction=LOG_MESSAGE_SIZE)
        )

    def print_caution(self, message):
        self.print_thread(
            CLI.message(
                message, "yellow", verbose=False, width_fraction=LOG_MESSAGE_SIZE
            )
        )

    def print_ok(self, message):
        self.print_thread(
            CLI.message(message, "lime", verbose=False, width_fraction=LOG_MESSAGE_SIZE)
        )

    def print_(self, message):
        self.print_thread(
            CLI.message(message, "lime", verbose=False, width_fraction=LOG_MESSAGE_SIZE)
        )

    def command_line(self):
        while not self.exit_event.is_set():
            ready_to_read, _, _ = select.select([sys.stdin], [], [], 1)
            if ready_to_read:
                message = input()

                if self.commands(message) == 123:
                    continue

                message = Protocol(content=message, method=message)
                # if message == Protocols.DISCONNECT:
                    # self.stop()
                # if message == Protocols.SHOW:
                    # self.show_clients()


    def commands(self, user_input:str):
        from cli_commands import CLI_DEFAULT_COMMANDS, CLI_COMMANDS
        self.custom_commands = CLI_COMMANDS
        input_segments = user_input.split(" ")
        for command in self.custom_commands + CLI_DEFAULT_COMMANDS:
            if input_segments[0] in command["Commands"]:


                if hasattr(command["Function"], "__name__"):
                    need_self = command["Function"].__name__ in dir(Server)
                else:
                    need_self = False


                if command["Parameters"] > 0:
                    # return command["Function"](self, *command["Parameters"]) if need_self else command["Function"](*command["Parameters"])
                    return command["Function"](self, *input_segments[1:]) if need_self else command["Function"](*input_segments[1:])
                    # return command["Function"](self, *command["Parameters"]) if need_self else command["Function"](*command["Parameters"])
                elif len(input_segments) > 0:
                    return command["Function"](self, *input_segments[1:]) if need_self else command["Function"](*input_segments[1:])
                else:
                    return command["Function"](self) if need_self else command["Function"]()
        else:
            print(f"Command '{input_segments}' not found.")
        return 123


    def show_help_menu(self):
        # print("Available commands:")
        from cli_commands import CLI_DEFAULT_COMMANDS
        results = CLI.create_help_menu(self.custom_commands, CLI_DEFAULT_COMMANDS, verbose=False)
        self.print_thread(results[0])
        self.print_thread(results[1])
        


if __name__ == "__main__":
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
    args = parser.parse_args()

    server = Server(host=args.IPv4Address, port=args.Port)
    server.run()
