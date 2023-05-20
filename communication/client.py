import socket
import threading

# Define the IP address and port number of the server
SERVER_ADDRESS = ('127.0.0.1', 5000)

# Define a function to continuously read user input and send messages to the server
def send_messages(client_socket):
    while True:
        message = input()
        client_socket.send(f'SEND:{message}'.encode())

# Define a function to continuously read incoming messages from the server and print them to the console
def receive_messages(client_socket):
    while True:
        data = client_socket.recv(1024).decode()
        if not data:
            break
        command, message = data.split(':', 1)
        if command == 'RECEIVE':
            print(message)

# Connect to the server and start sending and receiving messages
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(SERVER_ADDRESS)

threading.Thread(target=send_messages, args=(client_socket,)).start()
threading.Thread(target=receive_messages, args=(client_socket,)).start()
