#!/bin/python3
import argparse
import json
import os
import select
import selectors
import socket
import sys
import threading
from random import randrange
import time
import traceback
from api import API
import jsonschema
from node import Node

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
LOG_MESSAGE_SIZE = 75.0
LOG = True


# TODO: Add thread for rely connections to neighbor nodes


class Client:
    def __init__(
        self,
        client_id: str,
        host="127.0.0.1",
        port=5000,
        custom_logic=None,
        custom_commands=None,
    ):
        self.id = client_id
        self.running = True
        self.__print_lock = threading.Lock()
        self.__exit_event = threading.Event()
        self.initialized = False
        self.sock = None
        self.port = port
        self.host = host

        self.custom_logic = custom_logic
        self.custom_commands = [] if custom_commands is None else custom_commands
        self.node: Node = None

        self.__selector_sock = selectors.DefaultSelector()
        self.__selector_input = selectors.DefaultSelector()

        wait_time = 5
        connected = False
        while not connected:
            try:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.settimeout(1.0)
                self.sock.connect((host, port))
                connected = True
            except socket.error as err:
                CLI.message_caution(
                    f"Unable to resolve IP address, retrying in {wait_time} second(s)...",
                    print_func=self.__print_thread,
                )
                time.sleep(wait_time)

    def __process_message(self, message: Protocol, is_receiving=False):
        if not message:
            CLI.message_caution("GOT EMPTY MESSAGE", print_func=self.__print_thread)
            return False

        if message == ProtocolMethod.INIT:
            if message.state == ProtocolState.REQ_AWK:
                self.node = Node(self.sock, config_data = json.loads(message.content))
                message = Protocol(method=ProtocolMethod.INIT, state=ProtocolState.AWK)
                self.__send_data(message)
                return False
            elif message.state == ProtocolState.SUCCESS:
                CLI.message_ok("CONNECTED", print_func=self.__print_thread)
                return False
            else:
                # CLI.message_error("INIT FAILED", print_func=self.__print_thread)
                self.os_set_IP(ip = str(self.node.IP))
                return False

        if message == ProtocolMethod.COMMAND:
            self.run_command(*message.content.split(" "))
            return False

        if message == ProtocolMethod.SCRIPT:
            self.run_script(*message.content.split(" "))
            return False

        if message == ProtocolMethod.EXIT:
            return self.disconnect(state = message.state)
            
        if self.custom_logic is not None:
            return self.custom_logic(self, self.sock, message)

        if not is_receiving:
            self.__send_data(message)

        return False

    def __receive(self):
        self.__selector_sock.register(
            self.sock, selectors.EVENT_READ, self.__receive_data
        )

        while not self.__exit_event.is_set():
            events = self.__selector_sock.select(timeout=0)
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
                CLI.message_error("RECEIVE ERROR", print_func=self.__print_thread)
                self.__print_thread(err)
                self.__print_thread(traceback.format_exc())
                self.sock.close()
                self.__exit_event.set()
                self.running = False
                break

    def __command_line(self):
        from cli_commands import CLI_CLIENT_COMMANDS

        self.custom_commands = self.custom_commands + CLI_CLIENT_COMMANDS
        while not self.__exit_event.is_set():
            try:
                if self.__is_active(sys.stdin):
                    message = input()
                    result = self.__commands(message)

                    if result is False:
                        continue
                    if result == "VOID":
                        print("Invalid METHOD:\t", f'"{message}"\n')
                        continue
                    if Protocol.has_key(message, ProtocolMethod):
                        message = Protocol(method=message)
                        if self.__process_message(message, is_receiving=False):
                            break
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
            print(f"Command '{input_segments}' not found.")
        return "VOID"

    def run(self):
        CLI.clear_terminal()
        receive_thread = threading.Thread(target=self.__receive)
        write_thread = threading.Thread(target=self.__command_line)

        receive_thread.start()
        write_thread.start()

        for thread in [receive_thread, write_thread]:
            try:
                thread.join()
            except KeyboardInterrupt:
                self.__exit_event.set()
            except Exception as err:
                print(err.with_traceback())
                self.__exit_event.set()

    def send(self, message: Protocol, sign: bool = True, encoding: str = "ascii"):
        self.__send_data(message, sign=sign)


    # Duel OS Implementation
    def __is_active(self, stream, timeout=1):
        if os.name == "nt":  # for Windows
            if type(stream) is socket.socket:
                ready, _, _ = select.select([stream], [], [], timeout)
                return ready
            import msvcrt
            import time

            start_time = time.time()
            while True:
                if msvcrt.kbhit():
                    return True
                if time.time() - start_time > timeout: 
                    return False
        else:  # for Unix/Linux/MacOS/BSD/etc
            ready, _, _ = select.select([sys.stdin], [], [], timeout)
            return bool(ready)

    def __send_data(self, message, sign: bool = True, encoding: str = "ascii"):
        if type(message) is Protocol:
            if sign:
                message.id = self.node.ID
            message = message.to_network(encoding=encoding)
            self.__log_send(message)
            self.sock.send(message)

    def __receive_data(self, sock, mask):
        message = sock.recv(1024).decode("ascii")
        if not message:
            return

        message: Protocol = Protocol.from_network(message)

        if message:
            formatted_message = r"{}".format(message)
            self.__log_receive(formatted_message)
        self.__process_message(message, is_receiving=True)

    def __log_send(self, message):
        if LOG:
            output = f"[LOG - {time.strftime('%X')}] {CLI.color('steelblue', 'SENDING:')}\n"
            output += f'{self.__get_socket_address(self.sock)} {"-->"} {str(message):<{LOG_PADDING}}\n'
            self.__print_thread(output, clr="gray")

    def __log_receive(self, message):
        if LOG:
            output = f"[LOG - {time.strftime('%X')}] {CLI.color('tomato', 'RECEIVED:')}\n"
            output += f'{self.__get_socket_address(self.sock)} {"<--"} {str(message):<{LOG_PADDING}}\n'
            self.__print_thread(output, clr="gray")

    def __get_socket_address(self, socket_obj: socket.socket) -> str:
        peer_name = socket_obj.getpeername()
        return CLI.color("aquamarine", f"{str(peer_name[0])} : {str(peer_name[1])}")

    def shutdown(self):
        self.disconnect(state = ProtocolState.DEFAULT)

    def  disconnect(self, state:ProtocolState = ProtocolState.AWK):
        if state == ProtocolState.REQ_AWK:
            self.__send_data(Protocol(method=ProtocolMethod.EXIT, state=ProtocolState.AWK))
            CLI.message_error("CONNECTION CLOSED BY SERVER", print_func=self.__print_thread)
            self.sock.close()
            self.running = False
            self.__exit_event.set()
            return True
        
        if state == ProtocolState.AWK:
            CLI.message_error("CONNECTION CLOSED", print_func=self.__print_thread)
            self.sock.close()
            self.running = False
            self.__exit_event.set()
            return True
        
        if state == ProtocolState.DEFAULT:
            CLI.message_caution("REQUESTING TERMINATION", print_func=self.__print_thread)
            self.__send_data(Protocol(method=ProtocolMethod.EXIT, state=ProtocolState.REQ_AWK))
            return False


        # self.running = False
        # self.__exit_event.set()

    def __print_thread(self, *args, **kwargs):
        kwargs = {**{"sep": " ", "end": "\n"}, **kwargs}
        msg = "".join(str(arg) + kwargs["sep"] for arg in args)
        msg = CLI.color(kwargs["clr"], msg) if "clr" in kwargs else msg
        kwargs.pop("clr", "")
        with self.__print_lock:
            print(msg, **kwargs)

    def show_help_menu(self):
        from cli_commands import CLI_DEFAULT_COMMANDS

        results = CLI.create_help_menu(
            self.custom_commands, CLI_DEFAULT_COMMANDS, verbose=False
        )
        self.__print_thread(results[0])
        self.__print_thread(results[1])

    def display_network(self):
        CLI.message_ok(self.__get_socket_address(self.sock))


    # TODO:
    # Terminate socket connection (maybe?)
    # reconfigure OS network interface
    # Re-establish socket connection to server
    def os_set_IP(self, ip: str, interface: str = "ens33", gateway: str = "10.1.1.100", dns: str = "10.1.1.1"):

        config = f"""
        [Match]
        Name={interface}

        [Network]
        Address={ip}/24
        Gateway={gateway}
        DNS={dns}

        """

        # open a file at /root/configuration/ens33.conf and replace all lines with the config variable
        with open(f"/root/configuration/{interface}.conf", "w") as f:
            f.write(config)

        self.disconnect(state=ProtocolState.AWK)
        self.run_command("reboot")


    def run_script(self, command: str, *args):
        prefix = "./" if command[0] != "/" else ""
        output = API.exe_bash(f"{prefix}{command}", *args)
        print(output)
        return output

    def run_command(self, command: str, *args):
        output = API.exe_bash(f"{command}", *args)
        print(output)
        return output


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







"""
TODO:
- Durning INIT
    - first connection will have default ip, lets say 10.1.1.250                                done
    - we need to 
        - pop config ip                                                                         done
        - send config ip to client                                                              done
        - close socket connection                                                               done
        - client call OS level script to reconfigure network                                    done
            - assume client will DC here                                                        * talk with Rakibul
                - if so, need to assess how server will handle reconnection                     *
                - + error cases? (user error: multiple connections)                             *               

        - reconnect to server                                                                   *          
"""
