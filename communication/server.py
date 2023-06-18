#!/bin/python3

import threading
import argparse
import socket as Socket
from socket import socket as sock
from time import sleep
from inputimeout import inputimeout, TimeoutOccurred
from protocol import Protocol as NET
from protocol import Command as NET_CMD
from node import Node, HelpMenu
import lib_cli as CLI
import select
import sys

_VERBOSE = True
_ERROR = -1
_OK = 0
_BROADCAST = 1
_BREAK = 2

pad = 20

class Server:
    def __init__(self, host='127.0.0.1', port=5000):
        self.host:str = host
        self.port:int = port

        self.clients:list[Node] = []
        self.threads:list[threading.Thread] = []
        self.IDs = []

        self.server:sock = sock(Socket.AF_INET, Socket.SOCK_STREAM)
        self.server.bind((self.host, self.port))

        self.running = True
        self.clients_lock = threading.Lock()
        self.print_lock = threading.Lock()
        self.thread_lock = threading.Lock()
        self.exit_event = threading.Event()


    def broadcast(self, message, exclude:sock = None):
        if exclude is not None and exclude in self.clients and len(self.clients) == 1:
            return
        if message == NET.INITIALIZE:
            return
        
        # self.print(f'\n{CLI.bold("BROADCASTING")}\t[ "{message}" ]')

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
            return True
        
        if message == NET.SHOW:
            self.show_clients()
            return False
        

        
        self.broadcast(f'\n{client_id}:\n{message}\n', exclude=client)
        return 0


    def handle(self, client:Node):
        while self.running:
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
        self.server.setblocking(False)
        while not self.exit_event.is_set():
            ready_to_read, _, _ = select.select([self.server], [], [], 1)
            if ready_to_read:
                client, address = self.server.accept()

                with self.clients_lock:
                    if address not in self.clients:
                        self.send_sock(client, NET.INITIALIZE.msg())
                        ID = self.rec_sock(client)

                        if ID == NET.DISCONNECT:
                            client.shutdown(0)
                            client.close()
                            break
                        else:
                            self.send_sock(client, NET.INITIALIZE.msg(status=NET_CMD.CONFIRMED))

                        client_node = Node(client, ID[:-5])
                        self.clients.append(client_node)

                    if _VERBOSE:
                        CLI.line()
                        self.print(CLI.message(f"Client Connected: {str(address)}", "green", verbose=False))
                        CLI.line()
                    else:
                        self.print(CLI.message(f"Client Connected: {str(address)}", "green", verbose=False))


                with self.thread_lock:
                    thread = threading.Thread(target=self.handle, args=(client_node,))
                    self.threads.append(thread)
                    thread.start()


    def send(self, client:Node, command:NET_CMD, encoding:str = 'ascii'):
        msg = command.msg()
        if _VERBOSE: self.print(f'{"[LOG] SENDING:":<{pad}}  {msg:<{pad}} --> {client._strIPPORT:>{pad}}',clr="gray")
        client.send(msg)

    def send(self, client:Node, message:str, encoding:str = 'ascii'):
        if _VERBOSE: self.print(f'{"[LOG] SENDING:":<{pad}} {message:<{pad}} --> {client._strIPPORT:>{pad}}',clr="gray")
        client.send(message)

    def rec(self, client:Node, buff_size:int = 1024, decoding:str = 'ascii') -> str:
        message = client.read(buff_size, decoding)
        if message and _VERBOSE:
            self.print(f'{"[LOG] RECEIVED:":<{pad}} {client._strIPPORT:<{pad}} <-- {message:>{pad}}',clr="gray")
        return message
    

    def send_sock(self, client:sock, command:NET_CMD, encoding:str = 'ascii'):
        msg = command.msg()
        if _VERBOSE: self.print(f'{"[LOG] SENDING:":<{pad}} {msg:<{pad}} --> {self.sock_to_str(client):>{pad}}',clr="gray")
        client.send(msg.encode(encoding))

    def send_sock(self, client:sock, message:str, encoding:str = 'ascii'):
        if _VERBOSE: self.print(f'{"[LOG] SENDING:":<{pad}} {message:<{pad}} --> {self.sock_to_str(client):>{pad}}',clr="gray")
        client.send(message.encode(encoding))

    def rec_sock(self, client:sock, buff_size:int = 1024, decoding:str = 'ascii') -> str:
        message = client.recv(buff_size).decode(decoding)
        if message:
            self.print(f'{"[LOG] RECEIVED:":<{pad}} {self.sock_to_str(client):<{pad}} <-- {message:>{pad}}',clr="gray")
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
        self.print()

                

    def show_motd(self):
        self.print(CLI.message(f"SERVER STARTED {str(self.host)}:{str(self.port)}", "green", verbose=False))

    def show_clients(self):
        client_info = []
        for node in self.clients:
            client_info.append(node.get_data())

        data = [list(client_info[0].keys())]
        # for each dict entry in client_info, put the values into a list and append it to data
        for entry in client_info:
            data.append(list(entry.values()))

        self.print(CLI.message(f"Connected Clients", verbose=False))
        CLI.table(data)

    def run(self):
        self.show_motd()
        self.server.listen()
        receive_thread = threading.Thread(target=self.receive)
        self.threads.append(receive_thread)

        command_thread = threading.Thread(target=self.command_line)
        self.threads.append(command_thread)
        
        command_thread.start()
        receive_thread.start()

        for thread in self.threads:
            try:
                # New Addition: wait for the receive thread to finish
                thread.join()
            except KeyboardInterrupt:
                self.stop(thread)
            except Exception as e:
                self.print(CLI.message(f"SERVER ERROR", "red", verbose=False))
                print(e)
                e.with_traceback()
                self.stop(thread)

        self.server.shutdown(0)
        self.server.close()
        self.print(CLI.message(f"SERVER STOPPED", "red", verbose=False))



    def print(self, *args, **kwargs):
        kwargs = {**{'sep':' ','end':'\n'},**kwargs}
        msg = ""
        for arg in args:
            msg += str(arg) + kwargs['sep']

        msg = CLI.color(kwargs["clr"], msg) if "clr"in kwargs else msg
        kwargs.pop("clr", "")
        with self.print_lock:
            print(msg, **kwargs)

    def command_line(self):
        while not self.exit_event.is_set():

            ready_to_read, _, _ = select.select([sys.stdin], [], [], 1)
            if ready_to_read:
                message = input()

                if message == NET.DISCONNECT:
                    self.print(CLI.message(f"STOPPING SERVER...", "yellow", verbose=False))
                    self.broadcast(NET.DISCONNECT.command)
                    sleep(1)
                    s = sock(Socket.AF_INET, Socket.SOCK_STREAM)
                    s.connect((self.host, self.port))
                    s.recv(1024)
                    s.send(str(NET.DISCONNECT.command).encode('ascii'))
                    s.shutdown(0)
                    s.close()
                    self.exit_event.set()
                    break



            # message = input()

            # if message == NET.DISCONNECT:
            #     self.print(CLI.message(f"STOPPING SERVER...", "yellow", verbose=False))
            #     self.broadcast(NET.DISCONNECT.command)
            #     sleep(1)
            #     s = sock(Socket.AF_INET, Socket.SOCK_STREAM)
            #     s.connect((self.host, self.port))
            #     s.recv(1024)
            #     s.send(str(NET.DISCONNECT.command).encode('ascii'))
            #     s.shutdown(0)
            #     s.close()
            #     break
                


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="This is a program that accepts IP address and Port number")

    parser.add_argument('-ip', '--IPv4Address', type=str, default='127.0.0.1', 
                        help='An IPv4 address in the format xxx.xxx.xxx.xxx')
    parser.add_argument('-p', '--Port', type=int, default=5000, 
                        help='A port number')

    args = parser.parse_args()
    CLI.clear_terminal()
    server = Server(host=args.IPv4Address, port=args.Port)
    server.run()
