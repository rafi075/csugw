#!/bin/python3
import threading
import socket as Socket
from socket import socket as sock
from time import sleep
from protocol import Protocol as NET
from protocol import Command as NET_CMD
import lib_cli as CLI


padding = 20


class Client:
    def __init__(self, ID:str, host='127.0.0.1', port=5000):
        self.ID = ID
        self.client = sock(Socket.AF_INET, Socket.SOCK_STREAM)
        self.client.settimeout(1.0)
        self.client.connect((host, port))
        self.running = True

        self.print_lock = threading.Lock()

    def print(self, *args, **kwargs):
        kwargs = {**{'sep':' ','end':'\n'},**kwargs}
        msg = ""
        for arg in args:
            msg += str(arg) + kwargs['sep']

        with self.print_lock:
            print(msg, **kwargs)

    def process_message(self, message, receiving:True):
        if not message:
            return
        
        if message == NET.INITIALIZE:
            if NET_CMD.CONFIRMED in message:
                self.print("Initialization Confirmation Received!")
            else:
                self.send(NET.INITIALIZE.msg()) # Signed with nickname so server can ID the client
        elif message == NET.DISCONNECT:
            if NET_CMD.CONFIRMED in message:
                self.print()
                self.print(CLI.message("Disconnected From Server", "red", verbose=False))
                self.running = False
                self.client.close()
                exit(0)
            else:
                self.send(NET.DISCONNECT.msg()) # Signed with nickname so server can ID the client
                # CLI.print_loading("Disconnecting...", 1, lock=self.print_lock, screen_width=2) # Wait for server to respond and rec thread to close application.
                sleep(1) # Wait for server to respond and rec thread to close application.

        elif not receiving:
            self.send(message)


    def receive(self):
        while self.running:
            try:
                message = self.rec()
                self.process_message(message, receiving=True)
            except Socket.timeout:
                continue
            except Exception as e:
                self.print("An error occured!")
                self.print(e.with_traceback())
                self.print(e)
                self.client.close()
                self.running = False
                break

    def write(self):
        while self.running:
            message = input()
            self.process_message(message, receiving=False)

    def send(self, command:NET_CMD, encoding:str = 'ascii'):
        msg = command.msg()
        self.print(f'SENDING: \t\t{msg:<{padding}} --> {self.sock_to_str(self.client):>{padding}}')
        self.client.send(msg.encode(encoding))

    def send(self, message:str, sign:bool = True, encoding:str = 'ascii'):
        if message:
            self.print(f'SENDING: \t\t{message:<{padding}} --> {self.sock_to_str(self.client):>{padding}}')
            message = f'{self.ID}:{message}' if sign else message
            self.client.send(message.encode(encoding))

    def rec(self, buff_size:int = 1024, decoding:str = 'ascii') -> str:
        message = self.client.recv(buff_size).decode(decoding)
        if message:
            r_message = r"{}".format(message)
            self.print(f'RECEIVED: \t\t{self.sock_to_str(self.client):<{padding}} <-- {r_message:>{padding}}')
            return message
    
    def sock_to_str(self, s:sock) -> str:
        pname = s.getpeername()
        return f'{str(pname[0])} : {str(pname[1])}'

    def run(self):
        receive_thread = threading.Thread(target=self.receive)
        receive_thread.start()

        write_thread = threading.Thread(target=self.write)
        write_thread.start()

        write_thread.join()
        receive_thread.join()

import argparse


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="This is a program that accepts IP address and Port number")

    parser.add_argument('-ip', '--IPv4Address', type=str, default='127.0.0.1', 
                        help='An IPv4 address in the format xxx.xxx.xxx.xxx')
    parser.add_argument('-p', '--Port', type=int, default=5000, 
                        help='A port number')

    args = parser.parse_args()
    ID = input("ID: ")
    client = Client(ID, host=args.IPv4Address, port=args.Port)
    client.run()
    exit(0)

