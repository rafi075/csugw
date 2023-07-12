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


DEFAULT_GATEWAY = "10.1.1.1"

# TODO: initialize clients based on config
#       discuss whether the program should block until all clients are initialized?


class Server:
    def __init__(
        self,
        host=DEFAULT_GATEWAY,
        port=5000,
        send_hook=None,
        receive_hook=None,
        custom_commands=None,
    ):
        self.host = host
        self.port = port
        self.__config_content = []
        self.__config_content_queue = []
        self.__config_last_entry = None
        self.__clients = []
        self.__threads = []
        # self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.sock.bind((self.host, self.port))
        # self.sock.settimeout(1)
        # self.sock.listen()
        self.__initialize_socket()

        self.custom_commands = [] if custom_commands is None else custom_commands
        self.send_hook = send_hook
        self.receive_hook = receive_hook

        self.__exit_event = threading.Event()
        self.__locks = {
            "clients": threading.Lock(),
            "print": threading.Lock(),
            "thread": threading.Lock(),
        }

        # self.dir_path = os.path.dirname(os.path.realpath(__file__))
        # self.config_path = os.path.join(self.dir_path, "config.json")
        # self.config_schema_path = os.path.join(self.dir_path, "config_schema.json")

        self.__initialize_config_paths()
        self.max_clients = 0
        self.awaiting_connection = None

    def __initialize_socket(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.host, self.port))
        self.sock.settimeout(1)
        self.sock.listen()

    def __initialize_config_paths(self):
        self.dir_path = os.path.dirname(os.path.realpath(__file__))
        self.config_path = os.path.join(self.dir_path, "config.json")
        self.config_schema_path = os.path.join(self.dir_path, "config_schema.json")

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

        if self.receive_hook is not None and is_receiving:
            return self.receive_hook(self, client, message)

        if self.send_hook is not None and not is_receiving:
            return self.send_hook(self, client, message)

        # If no other cases have been hit, send the message to the client
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
                        message = Protocol(
                            method=message_parts[0], content=" ".join(message_parts[1:])
                        )
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
                # self.sock.close()
                self.close_connection(self.sock)
                self.__exit_event.set()
                break

    def __parse_command(self, user_input: str):
        input_segments = user_input.split(" ")
        command_name = input_segments[0]
        command_args = input_segments[1:]
        return command_name, command_args

    def __execute_command(self, command_name, command_args):
        from cli_commands import CLI_DEFAULT_COMMANDS

        for command in self.custom_commands + CLI_DEFAULT_COMMANDS:
            if command_name in command["Commands"]:
                function = command["Function"]
                need_self = hasattr(function, "__name__") and function.__name__ in dir(
                    self.__class__
                )
                if not need_self and function in dir(self.__class__):
                    need_self = True
                    function = getattr(self.__class__, function)
                if command["Parameters"] > 0:
                    return (
                        function(self, *command_args)
                        if need_self
                        else function(*command_args)
                    )
                else:
                    return function(self) if need_self else function()
        return None

    def __commands(self, user_input: str):
        command_name, command_args = self.__parse_command(user_input)
        result = self.__execute_command(command_name, command_args)
        if result is None:
            # print(f"Command '{user_input}' not found.")
            return True
        return result

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

                # Handle client thread
                if client_node is not None:
                    with self.__locks["thread"]:
                        self.__threads.append(
                            threading.Thread(
                                target=self.__handle_client, args=(client_node,)
                            )
                        )
                        self.__threads[-1].start()

    def __initialize_client(self, client: socket.socket):
        init = Protocol(
            id="Server", method=ProtocolMethod.INIT, state=ProtocolState.REQ_AWK
        )

        # Check if client is returning from configuration reboot
        if self.awaiting_connection is not None:
            # get ip address from socket named client
            client_ip = str(client.getpeername()[0])
            if client_ip == str(self.awaiting_connection.IP):
                self.awaiting_connection = None
                client_node = Node(client, config_data=self.__config_last_entry)
                self.__clients.append(client_node)

                init.state = ProtocolState.SUCCESS
                init.content = ""
                self.__send_data(client, init)

                CLI.message_ok(
                    f"CLIENT CONNECTED: {str(client_node.network_string)}",
                    print_func=self.__print_thread,
                )
                self.show_clients()
                return client_node
            else:
                CLI.message_error(
                    "EITHER CLIENT FAILED TO CONFIG OR MULTIPLE CLIENTS STARTED",
                    print_func=self.__print_thread,
                )

        if len(self.__clients) == self.max_clients:
            CLI.message_error("MAX CLIENTS CONNECTED", print_func=self.__print_thread)
            # client.close()
            self.close_connection(client)

            return None

        client_node = self.pop_config(client)
        init.content = json.dumps(self.__config_last_entry)
        self.__send_data(client, init)
        self.awaiting_connection = client_node

        while not self.__is_active(client):
            pass

        response = self.__receive_data(client)

        if response == ProtocolMethod.EXIT:
            # client.shutdown(0)
            # client.close()
            self.close_connection(client)

            CLI.message_error("CLIENT DISCONNECTED", print_func=self.__print_thread)
            return None
        elif response == ProtocolMethod.INIT:
            if response.state != ProtocolState.AWK:
                CLI.message_error("NEVER GOT AWK", print_func=self.__print_thread)
                self.__config_content_queue.insert(0, self.__config_last_entry)
                return None

        init.state = ProtocolState.FAIL
        init.content = ""
        self.__send_data(client, init)

        CLI.line()
        CLI.message_caution(
            f"CLIENT CONFIGURING",
            print_func=self.__print_thread,
        )
        return None

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
        schema_path = schema_path or self.config_schema_path
        file_path = file_path or self.config_path

        schema = self.__load_json_file(schema_path)
        if not schema:
            CLI.message_error(f"Schema file '{schema_path}' not found.")
            return

        data = self.__load_json_file(file_path)
        if not data or not self.__validate_schema(data, schema):
            CLI.message_error(f"Config file '{file_path}' not found or invalid.")
            return

        self.__config_content = list(data["Nodes"])
        self.__config_content_queue = list(data["Nodes"])
        self.max_clients = len(self.__config_content)
        return True

    def __load_json_file(self, file_path):
        try:
            with open(file_path, "r") as file:
                data = json.load(file)
            return data
        except FileNotFoundError:
            CLI.message_error(f"File '{file_path}' not found.")
            return {}
        except json.JSONDecodeError:
            CLI.message_error(f"File '{file_path}' could not be parsed as JSON.")
            return {}

    def __validate_schema(self, data, schema):
        try:
            jsonschema.validate(instance=data, schema=schema)
        except jsonschema.exceptions.ValidationError:
            CLI.message_error(f"Data does not adhere to the configuration schema.")
            return False
        return True

    def pop_config(self, socket: socket) -> Node:
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

    @staticmethod
    def is_socket_connected(sock: socket.socket) -> bool:
        try:
            if sys.platform != "win32":
                sock.send(b'', socket.MSG_DONTWAIT)
            else:
                sock.send(b'')
        except BlockingIOError:
            return True
        except BrokenPipeError:
            return False
        except ConnectionAbortedError:
            return False
        except ConnectionResetError:
            return False
        return False

    def close_connection(self, connection: socket.socket or Node):
        sock:socket.socket = connection.socket if type(connection) is Node else connection
        if Server.is_socket_connected(sock):
            try:
                # sock.shutdown(socket.SHUT_RDWR)
                sock.close()

                if type(connection) is Node and connection in self.__clients:
                    self.__clients.remove(connection)
            except:
                pass

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
                    # client.close()
                    self.close_connection(client)

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
                    # client.close()
                    self.close_connection(client)

        except:
            pass

    def broadcast(self, message, exclude=None):
        if message == ProtocolMethod.INIT:
            return

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
                # client.close()
                self.close_connection(client)


        self.__exit_event.set()

        with self.__locks["thread"]:
            for thread in self.__threads:
                if thread.is_alive() and thread != threading.current_thread():
                    thread.join()

        # self.sock.shutdown(socket.SHUT_RDWR)
        # self.sock.close()
        self.close_connection(client)
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

    def __start_threads(self):
        """Starts the threads for receiving and command line handling."""
        self.__threads.extend(
            [
                threading.Thread(target=self.__receive),
                threading.Thread(target=self.__command_line),
            ]
        )
        for thread in self.__threads:
            try:
                thread.start()
            except KeyboardInterrupt:
                break

    def __join_threads(self):
        """Joins the threads with exception handling."""
        for thread in self.__threads:
            try:
                thread.join()
            except KeyboardInterrupt:
                break
            except Exception as e:
                CLI.message_error(
                    "Failure Joining Threads", print_func=self.__print_thread
                )

    def run(self):
        CLI.clear_terminal()

        if not self.__init_config():
            CLI.message_error("Failed to initialize config.")
            return

    
        CLI.message_ok(
            f"SERVER STARTED {self.host}:{self.port}", print_func=self.__print_thread
        )

        CLI.message_caution(
            f"Configured For MAX {self.max_clients} clients.",
            print_func=self.__print_thread,
        )
        self.sock.listen()
        self.__start_threads()
        self.__join_threads()

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
        default=DEFAULT_GATEWAY,
        help="An IPv4 address in the format xxx.xxx.xxx.xxx",
    )
    parser.add_argument("-p", "--Port", type=int, default=5000, help="A port number")
    args = parser.parse_args()

    server = Server(host=args.IPv4Address, port=args.Port)
    server.run()
