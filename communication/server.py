#!/bin/python3

import json
import os
import threading
import argparse
import socket
import time
import traceback
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
import time

LOG_MESSAGE_SIZE = 75.0
LOG_PADDING = 0
LOG = True



# TODO: initialize clients based on config
#       discuss whether the program should block until all clients are initialized?


class Server:
    def __init__(
        self, host="127.0.0.1", port=5000, custom_logic=None, custom_commands=None
    ):
        self.host = host
        self.port = port
        self.__config_content = []
        self.__config_content_queue = []
        self.__config_last_entry = -1
        self.__clients = []
        self.__threads = []
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.host, self.port))
        self.sock.settimeout(1)
        self.sock.listen()
        self.running = True

        self.custom_commands = [] if custom_commands is None else custom_commands
        self.custom_logic = custom_logic

        self.__exit_event = threading.Event()
        self.__locks = {
            "clients": threading.Lock(),
            "print": threading.Lock(),
            "thread": threading.Lock(),
        }

        self.dir_path = os.path.dirname(os.path.realpath(__file__))
        self.config_path = os.path.join(self.dir_path, "config.json")
        self.config_schema_path = os.path.join(self.dir_path, "config_schema.json")
        self.max_clients = 0

    def __process_message(self, client, message: Protocol, is_receiving=False):
        if not message:
            CLI.message_caution("GOT EMPTY MESSAGE", print_func=self.__print_thread)
            return False

        if message == ProtocolMethod.EXIT:
            return self.disconnect_client(client, state=message.state)

        if message == Protocols.SHOW:
            self.show_clients()
            return False
        
        if message == ProtocolMethod.COMMAND:
            self.__send_data(client, message)
            return False

        if self.custom_logic is not None:
            return self.custom_logic(self, client, message)

        if not is_receiving:
            if message[ProtocolType] == ProtocolType.BROADCAST:
                self.broadcast(f"{message}", exclude=client)
            else:
                self.__send_data(client, message)

        return False

    def __command_line(self):
        from cli_commands import CLI_SERVER_COMMANDS

        self.custom_commands = self.custom_commands + CLI_SERVER_COMMANDS

        while not self.__exit_event.is_set():
            try:
                if self.__is_active(sys.stdin):
                    message = input()
                    result = self.__commands(message)
                    message_parts = message.split(" ")
                    # if result is False:
                    #     continue
                    if result == "VOID":
                        print("Invalid METHOD:\t", f'"{message}"\n')
                        continue
                    if Protocol.has_key(message_parts[0], ProtocolMethod):
                        message = Protocol(method=message_parts[0], content=" ".join(message_parts[1:]))
                        for client in self.__clients:
                            self.__process_message(client, message, is_receiving=False)

            except KeyboardInterrupt:
                break
            except ValueError:
                break
            except Exception as err:
                CLI.message_error("COMMAND LINE ERROR", print_func=self.__print_thread)
                self.__print_thread(err)
                self.__print_thread(traceback.format_exc())
                self.sock.close()
                self.__exit_event.set()
                self.running = False
                break

    def __commands(self, user_input: str):
        from cli_commands import CLI_DEFAULT_COMMANDS

        input_segments = user_input.split(" ")
        for command in self.custom_commands + CLI_DEFAULT_COMMANDS:
            if input_segments[0] in command["Commands"]:
                function = command["Function"]
                if hasattr(function, "__name__"):
                    need_self = function.__name__ in dir(self.__class__)
                else:
                    if function in dir(self.__class__):
                        need_self = True
                        function = getattr(self.__class__, function)
                    else:
                        need_self = False
                if command["Parameters"] > 0:
                    return (
                        function(self, *input_segments[1:])
                        if need_self
                        else function(*input_segments[1:])
                    )
                else:
                    return function(self) if need_self else function()
        else:
            # print(f"Command '{input_segments}' not found.")
            return True
        return "VOID"

    def __handle_client(self, client: Node):
        while not self.__exit_event.is_set():
            try:
                if self.__is_active(client.socket):
                    message = self.__receive_data(client.socket)
                    if self.__process_message(client, message, is_receiving=True):
                        break
            except Exception as e:
                # TODO: Exception thrown on DC
                # Perhaps handle it more gracefully
                self.disconnect_client(client)
                break

    def __receive(self):
        self.sock.setblocking(False)
        while not self.__exit_event.is_set():
            if self.__is_active(self.sock):
                client, address = self.sock.accept()
                with self.__locks["clients"]:
                    if address not in self.__clients:
                        client_node = self.__initialize_client(client)
                if client_node is not None:
                    with self.__locks["thread"]:
                        self.__threads.append(
                            threading.Thread(
                                target=self.__handle_client, args=(client_node,)
                            )
                        )
                        self.__threads[-1].start()

    def __initialize_client(self, client):
        CLI.message_ok(
            f"ININT",
            print_func=self.__print_thread,
        )

        if len(self.__clients) == self.max_clients:
            CLI.message_error("MAX CLIENTS CONNECTED", print_func=self.__print_thread)
            client.close()
            return None

        init = Protocol(
            id="Server", method=ProtocolMethod.INIT, state=ProtocolState.REQ_AWK
        )

        client_node = self.pop_config(client)
        init.content = json.dumps(self.__config_last_entry)
        self.__send_data(client, init)

        while not self.__is_active(client):
            pass

        response = self.__receive_data(client)

        if response == ProtocolMethod.EXIT:
            client.shutdown(0)
            client.close()
            CLI.message_error("CLIENT DISCONNECTED", print_func=self.__print_thread)
            return
        elif response == ProtocolMethod.INIT:
            if response.state != ProtocolState.AWK:
                CLI.message_error("NEVER GOT AWK", print_func=self.__print_thread)
                self.__config_content_queue.insert(0, self.__config_last_entry)
                return None

        init.state = ProtocolState.SUCCESS
        init.content = ""
        self.__clients.append(client_node)

        self.__send_data(client, init)

        CLI.line()
        CLI.message_ok(
            f"CLIENT CONNECTED: {str(client_node.network_string)}",
            print_func=self.__print_thread,
        )
        self.show_client(client_node.ID)

        return client_node

    def send(self, client, message: Protocol):
        self.__send_data(client, message)

    def __send_data(
        self, client, message: Protocol, sign: bool = True, encoding="ascii"
    ):
        if sign and type(client) is Node:
            message["ID"] = "Server"
        addr = (
            CLI.color("aquamarine", client.network_string)
            if type(client) is Node
            else self.__get_socket_address(client)
        )
        self.__log_send(message, addr)
        message = message.to_network(
            encoding=encoding, node=client if type(client) is Node else None
        )

        if type(client) is Node:
            client.socket.sendall(message)
        else:
            client.sendall(message)

    def __receive_data(self, client, buff_size=1024, decoding="ascii") -> Protocol:
        message = client.recv(buff_size).decode(decoding)
        message: Protocol = Protocol.from_network(message)
        addr = (
            client.network_string
            if type(client) is Node
            else self.__get_socket_address(client)
        )
        self.__log_receive(message, addr)
        return message

    def __init_config(self, file_path=None, schema_path=None):
        try:
            with open(
                self.config_schema_path if schema_path is None else schema_path, "r"
            ) as f:
                schema = json.load(f)
        except FileNotFoundError:
            print(f"The file '{schema_path}' does not exist.")
        except json.JSONDecodeError:
            print(f"The file could not be parsed as JSON.")

        try:
            with open(self.config_path if file_path is None else file_path, "r") as f:
                data = json.load(f)
                jsonschema.validate(instance=data, schema=schema)
                self.__config_content = list(data["Nodes"])
                self.__config_content_queue = list(data["Nodes"])
                self.max_clients = len(self.__config_content)
        except FileNotFoundError:
            print(f"The file '{file_path}' does not exist.")
        except json.JSONDecodeError:
            print(f"The file could not be parsed as JSON.")
        except jsonschema.exceptions.ValidationError:
            print(
                f"The file '{file_path}' does not adhere to the configuration schema defined in {schema_path}."
            )

    def pop_config(self, socket: socket) -> Node:
        def default(data, key, default):
            return data[key] if key in data else default

        if len(self.__config_content_queue) > 0:
            data = self.__config_content_queue.pop(0)
            self.__config_last_entry = data
            return Node(socket, config_data=data)
        else:
            CLI.message_error("Config is empty")
            return None

    def get_client_by_tag(self, tag: str) -> Node:
        for client in self.__clients:
            if tag in client.tags:
                return client
        return None

    def get_client_by_id(self, client_id: str) -> Node:
        for client in self.__clients:
            if client.ID == client_id:
                return client
        return None

    def disconnect_client(self, client: Node, state: ProtocolState = ProtocolState.AWK):
        if client not in self.__clients:
            return

        def show_message():
            CLI.message_caution(
                f"CLIENT DISCONNECTED: {str(client.network_string)}",
                print_func=self.__print_thread,
            )

        try:
            if state == ProtocolState.REQ_AWK:
                # Logic before disconnecting the client goes here!
                # Based on a CLIENT'S REQUEST to disconnect
                with self.__locks["clients"]:
                    self.__clients.remove(client)
                    self.__send_data(
                        client.socket,
                        Protocol(method=ProtocolMethod.EXIT, state=ProtocolState.AWK),
                    )
                    show_message()
                    client.close()

            elif state == ProtocolState.DEFAULT:
                # Logic before disconnecting the client goes here!
                # Based on the SERVERS REQUEST to disconnect a client

                pass

            elif state == ProtocolState.AWK:
                # Logic for when a client confirms it will disconnect
                # due to the SERVER'S REQUEST
                with self.__locks["clients"]:
                    self.__clients.remove(client)
                    show_message()
                    client.close()
        except:
            pass

    def broadcast(self, message, exclude=None):
        if exclude and exclude in self.__clients and len(self.__clients) == 1:
            return
        if message != Protocols.INITIALIZE:
            with self.__locks["clients"]:
                for client in self.__clients:
                    if exclude != client:
                        self.__send_data(client, message)

    def shutdown(self):
        message = Protocol(
            protocol_type=ProtocolType.BROADCAST,
            method=ProtocolMethod.EXIT,
            state=ProtocolState.REQ_AWK,
        )

        CLI.message_caution("STOPPING SERVER...", print_func=self.__print_thread)
        self.broadcast(message)
        time.sleep(1)

        with self.__locks["clients"]:
            for client in self.__clients:
                client.close()

        self.running = False
        self.__exit_event.set()

        with self.__locks["thread"]:
            for thread in self.__threads:
                if thread.is_alive() and thread != threading.current_thread():
                    thread.join()


        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()
        CLI.message_error("SERVER SHUTDOWN", print_func=self.__print_thread)

    def show_clients(self):
        if len(self.__clients) == 0:
            CLI.message_error("NO CLIENTS CONNECTED", print_func=self.__print_thread)
            return

        client_info = []
        for node in self.__clients:
            client_info.append(node.get_data())
        data = [list(entry.values()) for entry in client_info]
        headers = ["Index"] + list(client_info[0].keys())
        self.__print_("Connected Clients")
        CLI.table(data, headers=headers, showindex=True)

    def show_client(self, client: int or str):
        if type(client) is str:
            for node in self.__clients:
                if node.ID == client:
                    node.show()

        if str(client).isdigit():
            client = int(client)
            if client >= 0 and client < len(self.__clients):
                self.__clients[client].show()
            else:
                CLI.message_error(
                    "INVALID CLIENT INDEX", print_func=self.__print_thread
                )

    def run(self):
        CLI.clear_terminal()
        self.__init_config()

        CLI.message_ok(
            f"SERVER STARTED {self.host}:{self.port}", print_func=self.__print_thread
        )

        CLI.message_caution(
            f"Configured For MAX {len(self.__config_content)} clients.",
            print_func=self.__print_thread,
        )
        self.sock.listen()
        self.__threads.extend(
            [
                threading.Thread(target=self.__receive),
                threading.Thread(target=self.__command_line),
            ]
        )

        [thread.start() for thread in self.__threads]
        for thread in self.__threads:
            try:
                thread.join()
            except KeyboardInterrupt:
                break
            except Exception as e:
                CLI.message_error("SERVER ERROR", print_func=self.__print_thread)
                print(e)

    def show_help_menu(self):
        from cli_commands import CLI_DEFAULT_COMMANDS

        results = CLI.create_help_menu(
            self.custom_commands, CLI_DEFAULT_COMMANDS, verbose=False
        )

        self.__print_thread(results[0])
        self.__print_thread(results[1])

    def __log_send(self, message, addr):
        if LOG:
            output = (
                f"[LOG - {time.strftime('%X')}] {CLI.color('steelblue', 'SENDING:')}\n"
            )
            output += f'{str(message):<{LOG_PADDING}} {"-->":<{LOG_PADDING}} {addr}\n'
            self.__print_thread(output, clr="gray")

    def __log_receive(self, message, addr):
        if LOG:
            output = (
                f"[LOG - {time.strftime('%X')}] {CLI.color('tomato', 'RECEIVED:')}\n"
            )
            output += f'{str(message):<{LOG_PADDING}} {"<--":<{LOG_PADDING}} {addr}\n'
            self.__print_thread(output, clr="gray")

    def __get_socket_address(self, socket_obj: socket.socket) -> str:
        peer_name = socket_obj.getpeername()
        return CLI.color("aquamarine", f"{str(peer_name[0])} : {str(peer_name[1])}")

    def __print_thread(self, *args, **kwargs):
        kwargs = {**{"sep": " ", "end": "\n"}, **kwargs}
        msg = "".join(str(arg) + kwargs["sep"] for arg in args)
        msg = CLI.color(kwargs["clr"], msg) if "clr" in kwargs else msg
        kwargs.pop("clr", "")
        with self.__locks["print"]:
            print(msg, **kwargs)

    def __print_(self, message):
        self.__print_thread(
            CLI.message(message, "lime", verbose=False, width_fraction=LOG_MESSAGE_SIZE)
        )

    def __is_active(self, stream, timeout=1):
        if type(stream) is socket.socket:
            ready, _, _ = select.select([stream], [], [], timeout)
            return ready
        else:
            if os.name == "nt":  # for Windows
                import msvcrt
                import time

                start_time = time.time()
                while True:
                    if msvcrt.kbhit():
                        return True
                    if time.time() - start_time > timeout:
                        return False
            else:  # for Unix/Linux/MacOS/BSD/etc
                ready, _, _ = select.select([stream], [], [], timeout)
                return bool(ready)


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
