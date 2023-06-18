#!/bin/python3

import threading
import socket as Socket
from socket import socket as sock
from protocol import Protocol as NET
from protocol import Command as NET_CMD
from node import Node, HelpMenu
import lib_cli as CLI

_VERBOSE = True
_ERROR = -1
_OK = 0
_BROADCAST = 1
_BREAK = 2

padding:int = 20

class Server:
    def __init__(self, host='127.0.0.1', port=5000):
        self.host:str = host
        self.port:int = port

        self.clients:list[Node] = []
        self.IDs = []

        self.server:sock = sock(Socket.AF_INET, Socket.SOCK_STREAM)
        self.server.bind((self.host, self.port))

        self.clients_lock = threading.Lock()

    def broadcast(self, message, exclude:sock = None):
        if exclude is not None and exclude in self.clients and len(self.clients) == 1:
            return
        if message == NET.INITIALIZE:
            return
        
        # print(f'\n{CLI.bold("BROADCASTING")}\t[ "{message}" ]')

        with self.clients_lock:
            for client in self.clients:
                if exclude is not None and client == exclude:

                    continue
                else:
                    self.send(client, message)


    # TODO: Perhaps clean this up with protocol 'states'
    def process_message(self, client:Node, message:str):

        # Message is signed with client ID
        if ":" in message:
            client_id, message = message.split(":")
        else:
            return ("null","null",_ERROR)

        if message == NET.DISCONNECT:
            self.client_disconnect(client)
            return 1
        
        if message == NET.SHOW:
            self.show_clients()
            return 0
        

        
        self.broadcast(f'\n{client_id}:\n{message}\n', exclude=client)
        return 0


    def handle(self, client:Node):
        while True:
            try:
                message = self.rec_sock(client.socket)
                if self.process_message(client, message):
                    break
            except Exception as e:
                e.with_traceback()
                with self.clients_lock:
                    self.clients.remove(client)
                    client.close()
                self.broadcast(f'\n{client.ID} left the chat!\n')
                break

    def receive(self):
        while True:
            client, address = self.server.accept()
            tmp_node = Node(client)

            with self.clients_lock:
                if address not in self.clients:
                    self.send_sock(client, NET.INITIALIZE.msg())
                    ID = self.rec_sock(client)
                    self.send_sock(client, NET.INITIALIZE.msg(status=NET_CMD.CONFIRMED))
                    # with self.clients_lock:
                    client_node = Node(client, ID[:-5])
                    self.clients.append(client_node)
                    # self.IDs.append(address[0])
                if _VERBOSE:
                    CLI.line()
                    CLI.message(f"Client Connected: {str(address)}", "green")
                    print(f"Client ID: {str(ID[:-5]):<{padding}}")
                    CLI.line()
                else:
                    CLI.message(f"Client Connected: {str(address)}", "green")

                self.broadcast(f'\n{ID} joined the chat!\n', exclude=client)

            thread = threading.Thread(target=self.handle, args=(client_node,))
            thread.start()


    def send(self, client:Node, command:NET_CMD, encoding:str = 'ascii'):
        msg = command.msg()
        if _VERBOSE: print(f'SENDING: \t\t{msg:<{padding}} --> {client._strIPPORT:>{padding}}')
        client.send(msg)

    def send(self, client:Node, message:str, encoding:str = 'ascii'):
        if _VERBOSE: print(f'SENDING: \t\t{message:<{padding}} --> {client._strIPPORT:>{padding}}')
        client.send(message)

    def rec(self, client:Node, buff_size:int = 1024, decoding:str = 'ascii') -> str:
        message = client.read(buff_size, decoding)
        if message and _VERBOSE:
            print(f'RECEIVED: \t\t{client._strIPPORT:<{padding}} <-- {message:>{padding}}')
        return message
    

    def send_sock(self, client:sock, command:NET_CMD, encoding:str = 'ascii'):
        msg = command.msg()
        if _VERBOSE: print(f'SENDING: \t\t{msg:<{padding}} --> {self.sock_to_str(client):>{padding}}')
        client.send(msg.encode(encoding))

    def send_sock(self, client:sock, message:str, encoding:str = 'ascii'):
        if _VERBOSE: print(f'SENDING: \t\t{message:<{padding}} --> {self.sock_to_str(client):>{padding}}')
        client.send(message.encode(encoding))

    def rec_sock(self, client:sock, buff_size:int = 1024, decoding:str = 'ascii') -> str:
        message = client.recv(buff_size).decode(decoding)
        if message:
            print(f'RECEIVED: \t\t{self.sock_to_str(client):<{padding}} <-- {message:>{padding}}')
        return message

    def sock_to_str(self, s:sock) -> str:
        pname = s.getpeername()
        return f'{str(pname[0])} : {str(pname[1])}'


    def client_disconnect(self, client:Node):
        with self.clients_lock:
            self.send(client, NET.DISCONNECT.msg(status=NET_CMD.CONFIRMED))
            client.close()
            self.clients.remove(client)
        self.broadcast(f'\nLEFT: {client.ID}\n')

    def stop(self, run_thread:threading.Thread):
        """
        Close the server Socket and stop the server.
        """

        self.broadcast('Server is shutting down!')
        self.server.close()

        with self.clients_lock:
            for client in self.clients:
                client.close()

        run_thread.join()
        print()
        CLI.message(f"SERVER STOPPED", "red")

                

    def show_motd(self):
        CLI.message(f"SERVER STARTED {str(self.host)}:{str(self.port)}", "green")

    def show_clients(self):
        client_info = []
        for node in self.clients:
            client_info.append(node.get_data())

        data = [list(client_info[0].keys())]
        # for each dict entry in client_info, put the values into a list and append it to data
        for entry in client_info:
            data.append(list(entry.values()))

        CLI.message(f"Connected Clients")
        CLI.table(data)

    def run(self):
        self.show_motd()
        self.server.listen()
        thread = threading.Thread(target=self.receive)
        thread.start()

        try:
            # New Addition: wait for the receive thread to finish
            thread.join()
        except KeyboardInterrupt:
            # New Addition: stop the server when a KeyboardInterrupt is received
            self.stop(thread)
        except Exception as e:
            CLI.message(f"SERVER ERROR", "red")
            print(e)
            print()
            self.stop(thread)





import argparse

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="This is a program that accepts IP address and Port number")

    parser.add_argument('-ip', '--IPv4Address', type=str, default='127.0.0.1', 
                        help='An IPv4 address in the format xxx.xxx.xxx.xxx')
    parser.add_argument('-p', '--Port', type=int, default=5000, 
                        help='A port number')

    args = parser.parse_args()
    server = Server(host=args.IPv4Address, port=args.Port)
    server.run()
