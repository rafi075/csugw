#!/bin/python3
from random import randrange
import threading
import argparse
import socket as Socket
from socket import socket as sock
from time import sleep
from protocol import Protocol as NET
from protocol import Command as NET_CMD
import lib_cli as CLI
import select
import sys

# For testing
from inputimeout import inputimeout, TimeoutOccurred


pad = 20


class Client:
    def __init__(self, ID:str, host='127.0.0.1', port=5000):
        self.ID = ID
        
        try:
            self.client = sock(Socket.AF_INET, Socket.SOCK_STREAM)
            self.client.settimeout(1.0)
            self.client.connect((host, port))
        except Socket.error as e:
            print(str(e))
        
        self.running = True
        self.print_lock = threading.Lock()
        self.exit_event = threading.Event()


    def print(self,*args, **kwargs):
        kwargs = {**{'sep':' ','end':'\n'},**kwargs}
        msg = ""
        for arg in args:
            msg += str(arg) + kwargs['sep']

        msg = CLI.color(kwargs["clr"], msg) if "clr"in kwargs else msg
        kwargs.pop("clr", "")
        with self.print_lock:
            print(msg, **kwargs)



    def disconnect(self, message, receiving=False):
        if NET_CMD.CONFIRMED in message:
            self.print()
            self.print(CLI.message("Disconnected From Server", "red", verbose=False))
            self.print("Press enter to continue...",clr="gray")
            self.running = False
            self.client.shutdown(0)
            self.client.close()
            exit(0)
        else:
            self.send(NET.DISCONNECT.msg())
            if not receiving:
                exit(0)



    def process_message(self, message, receiving = False):
        if not message:
            return False
        
        if message == NET.INITIALIZE:
            if NET_CMD.CONFIRMED in message:
                self.print("Initialization Confirmation Received!", clr="gray")
                self.print(CLI.message("Initialization Successful", "green", verbose=False))
            else:
                self.send(NET.INITIALIZE.msg())
            return False
            
        elif message == NET.DISCONNECT:
            self.send(NET.DISCONNECT.msg())
            self.running = False
            self.exit_event.set()
            return True

        elif not receiving:
            self.send(message)
            return False



    def receive(self):
        while not self.exit_event.is_set():
            try:
                if self.isActive(self.client):
                    message = self.rec()
                    if self.process_message(message, receiving=True):
                        break
            except Socket.timeout:
                continue
            except KeyboardInterrupt:
                self.client.close()
                break
            except Exception as e:
                self.print("An error occured!", clr="gray")
                self.print(e.with_traceback())
                self.print(e)
                self.client.close()
                self.running = False
                break

    def write(self):
        while not self.exit_event.is_set():
            try:
                # For testing only
                # Check if input is available
                if self.isActive(sys.stdin):
                    message  = input()
                    if self.process_message(message, receiving=False):
                        break
            except TimeoutOccurred:
                continue
            except KeyboardInterrupt:
                break
            except ValueError as e:
                break
            except Exception as e:
                self.print("An error occured!", clr="gray")
                self.print(type(e))
                # self.print(e.with_traceback())
                self.print(e)
                self.client.close()
                self.running = False
                break

    def isActive(self, stream, timeout = 1):
        ready, _, _ = select.select([stream], [], [], timeout)
        return ready


    def send(self, command:NET_CMD, encoding:str = 'ascii'):
        msg = command.msg()
        self.print(f'{"[LOG] SENDING:":<{pad}} {msg:<{pad}} --> {self.sock_to_str(self.client):>{pad}}',clr="gray")
        self.client.send(msg.encode(encoding))

    def send(self, message:str, sign:bool = True, encoding:str = 'ascii'):
        if message:
            self.print(f'{"[LOG] SENDING:":<{pad}} {message:<{pad}} --> {self.sock_to_str(self.client):>{pad}}',clr="gray")
            message = f'{self.ID}:{message}' if sign else message
            self.client.send(message.encode(encoding))

    def rec(self, buff_size:int = 1024, decoding:str = 'ascii') -> str:
        if not self.client:
            return ""
        message = self.client.recv(buff_size).decode(decoding)
        if message:
            r_message = r"{}".format(message)
            self.print(f'{"[LOG] RECEIVED:":<{pad}} {self.sock_to_str(self.client):<{pad}} <-- {r_message:>{pad}}',clr="gray")
            return message
    
    def sock_to_str(self, s:sock) -> str:
        pname = s.getpeername()
        return f'{str(pname[0])} : {str(pname[1])}'

    def run(self):
        receive_thread = threading.Thread(target=self.receive)
        receive_thread.start()

        write_thread = threading.Thread(target=self.write)
        write_thread.start()

        for thread in [receive_thread, write_thread]:
            try:
                thread.join()
            except KeyboardInterrupt:
                self.stop(thread)
            except Exception as e:
                e.with_traceback()
                self.stop(thread)



if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="This is a program that accepts IP address and Port number")

    parser.add_argument('-ip', '--IPv4Address', type=str, default='127.0.0.1', 
                        help='An IPv4 address in the format xxx.xxx.xxx.xxx')
    parser.add_argument('-p', '--Port', type=int, default=5000, 
                        help='A port number')

    args = parser.parse_args()
    # ID = input("ID: ")
    CLI.clear_terminal()
    ID = str(randrange(0, 1000))
    client = Client(ID, host=args.IPv4Address, port=args.Port)
    client.run()
    exit(0)

