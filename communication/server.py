#!/bin/python3

import json
import threading
import argparse
import socket
from inputimeout import inputimeout
import jsonschema
from protocol import Protocols, Protocol, ProtocolState, ProtocolMethod, ProtocolType, Field
from node import Node, HelpMenu
import lib_cli as CLI
import select
import sys

LOG_PADDING = 0
LOG = True


class Server:
    def __init__(self, host='127.0.0.1', port=5000):
        self.host = host
        self.port = port
        self.clients = []
        self.threads = []
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host, self.port))
        self.server.listen()
        self.running = True
        self.locks = {'clients': threading.Lock(), 'print': threading.Lock(), 'thread': threading.Lock()}
        self.exit_event = threading.Event()


    def broadcast(self, message, exclude=None):
        if exclude and exclude in self.clients and len(self.clients) == 1:
            return
        if message != Protocols.INITIALIZE:
            with self.locks['clients']:
                for client in self.clients:
                    if exclude != client:
                        self.send(client, message)

    def process_message(self, client, message:Protocol):
        # client_id, message = message.split(":") if ":" in message else ("null", "null")

        if message == Protocols.DISCONNECT:
            self.disconnect_client(client)
            return True
        if message == Protocols.SHOW:
            self.show_clients()
            return False

        if message[ProtocolType] == ProtocolType.BROADCAST:
            self.broadcast(f'{message}', exclude=client)
        return False

    def handle_client(self, client:Node):
        while not self.exit_event.is_set():
            try:
                ready_to_read, _, _ = select.select([client.socket], [], [], 1)
                if ready_to_read:
                    message = self.receive_data(client.socket)
                    if self.process_message(client, message):
                        break
            except Exception:
                print("Client disconnected")
                break

    def receive(self):
        self.server.setblocking(False)
        while not self.exit_event.is_set():
            ready_to_read, _, _ = select.select([self.server], [], [], 1)
            if ready_to_read:
                client, address = self.server.accept()
                with self.locks['clients']:
                    if address not in self.clients:
                        client_node = self.initialize_client(client)
                if client_node:
                    with self.locks['thread']:
                        self.threads.append(threading.Thread(target=self.handle_client, args=(client_node,)))
                        self.threads[-1].start()


    def initialize_client(self, client):
        self.send(client, Protocols.INITIALIZE)
        response = self.receive_data(client)
        if response == Protocols.DISCONNECT:
            client.shutdown(0)
            client.close()
            return
        
        # TODO: Implement AWK
        self.send(client, Protocols.INITIALIZE)
        client_node = Node(client, response["ID"])
        self.clients.append(client_node)
        CLI.line()
        self.print_message(CLI.message(f"Client Connected: {str(client.getpeername())}", "green", verbose=False))
        return client_node

    def send(self, client, message:Protocol, encoding='ascii'):
        addr = client._strIPPORT if type(client) is Node else self.get_socket_address(client)
        self.log_send(message, addr)
        message = message.to_network(encoding=encoding,
            node = client if type(client) is Node else None)

        if type(client) is Node:
            client.socket.sendall(message)
        else:
            client.sendall(message)

    def receive_data(self, client, buff_size=1024, decoding='ascii') -> Protocol:
        message =  client.recv(buff_size).decode(decoding)
        message:Protocol = Protocol.from_network(message)        
        addr = client._strIPPORT if type(client) is Node else self.get_socket_address(client)
        self.log_receive(message, addr)
        return message
    
    def log_send(self, message, addr):
        if LOG: 
            output = f"[LOG] {CLI.color('steelblue', 'SENDING:')}\n"
            output += f'{str(message):<{LOG_PADDING}} {"-->":<{LOG_PADDING}} {addr}\n'
            self.print_message(output, clr="gray")

    def log_receive(self, message, addr):
        if LOG: 
            output = f"[LOG] {CLI.color('tomato', 'RECEIVED:')}\n"
            output += f'{str(message):<{LOG_PADDING}} {"<--":<{LOG_PADDING}} {addr}\n'
            self.print_message(output, clr="gray")

    def get_socket_address(self, socket_obj: socket.socket) -> str:
        peer_name = socket_obj.getpeername()
        return CLI.color('aquamarine', f'{str(peer_name[0])} : {str(peer_name[1])}')

    def disconnect_client(self, client:Node):
        with self.locks['clients']:
            # self.send(client.socket, Protocols.DISCONNECT(Status.CONFIRM.value, client))
            self.send(client.socket, Protocols.DISCONNECT)
            client.close()
            self.clients.remove(client)
        self.broadcast(f'\nLEFT: {client.ID}\n')

    def stop(self):
        message = Protocols.DISCONNECT
        message[ProtocolType] = ProtocolType.BROADCAST
        message[Field.ID] = "Server"
        self.print_message(CLI.message(f"STOPPING SERVER...", "yellow", verbose=False))
        self.broadcast(message)
        self.exit_event.set()
        with self.locks['clients']:
            for client in self.clients:
                client.close()

        with self.locks['thread']:
            for thread in self.threads:
                if thread.is_alive() and thread != threading.current_thread():
                    thread.join()

        self.server.close()
        self.print_message(CLI.message(f"SERVER SHUTDOWN", "red", verbose=False))
        

    def show_clients(self):
        client_info = []
        for node in self.clients:
            client_info.append(node.get_data())
        data = [list(client_info[0].keys())] + [list(entry.values()) for entry in client_info]
        self.print_message(CLI.message(f"Connected Clients", verbose=False))
        CLI.table(data)

    def run(self):
        CLI.clear_terminal()
        # self.print_message("TEST")
        self.print_message(CLI.message(f"SERVER STARTED {self.host}:{self.port}", "green", verbose=False))
        self.server.listen()
        self.threads.extend([threading.Thread(target=self.receive), threading.Thread(target=self.command_line)])
        [thread.start() for thread in self.threads]

        for thread in self.threads:
            try:
                # thread.start()
                thread.join()
            except KeyboardInterrupt:
                break;
            except Exception as e:
                self.print_message(CLI.message(f"SERVER ERROR", "red", verbose=False))
                print(e)

        # self.stop()
        

    def print_message(self, *args, **kwargs):
        kwargs = {**{'sep': ' ', 'end': '\n'}, **kwargs}
        msg = "".join(str(arg) + kwargs['sep'] for arg in args)
        msg = CLI.color(kwargs["clr"], msg) if "clr" in kwargs else msg
        kwargs.pop("clr", "")
        with self.locks['print']:
            print(msg, **kwargs)

    def command_line(self):
        while not self.exit_event.is_set():
            ready_to_read, _, _ = select.select([sys.stdin], [], [], 1)
            if ready_to_read:
                message = input()
                message = Protocol(content = message, method = message)
                if message == Protocols.DISCONNECT:
                    self.stop()
                    exit(0)
                elif message == Protocols.SHOW:
                    self.show_clients()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="This is a program that accepts IP address and Port number")
    parser.add_argument('-ip', '--IPv4Address', type=str, default='127.0.0.1', help='An IPv4 address in the format xxx.xxx.xxx.xxx')
    parser.add_argument('-p', '--Port', type=int, default=5000, help='A port number')
    args = parser.parse_args()

    server = Server(host=args.IPv4Address, port=args.Port)
    server.run()
