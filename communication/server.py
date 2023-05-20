import socket
import threading
from api import API


# Define the IP address and port number that the server will listen on
SERVER_ADDRESS = ('127.0.0.1', 5000)

# Define the executable and file path for the API
api = API()
api.EXECUTABLE = "python"
api.PATH = "api-testfile.py"
API_TESTING = False

# Define a list to store all connected clients
clients = []
ins = []

# Define a function to handle incoming client connections
def handle_client(client_socket, client_address):
    print(f'Client {client_address} connected')

    # Add the client to the list of connected clients
    clients.append((client_socket, client_address))

    # Continuously read incoming messages from the client
    while True:
        data = client_socket.recv(1024).decode()
        if not data:
            break

        # Parse the command and message from the incoming data
        command, message = data.split(':', 1)

        # If the command is SEND, relay the message to all other connected clients
        if command == 'SEND':
            for c, addr in clients:
                if c != client_socket:
                    c.send(f'RECEIVE:{message}'.encode())
        
        # If the command is SENDTO, find the specified client and send the message to them
        elif command == 'SENDTO':
            to_client_address, message = message.split(':', 1)
            for c, addr in clients:
                if addr == to_client_address:
                    c.send(f'RECEIVE:{message}'.encode())
                    break

    # Remove the client from the list of connected clients
    clients.remove((client_socket, client_address))
    client_socket.close()
    print(f'Client {client_address} disconnected')

def get_client(client_id):

    conn = 0
    addr = 0
    while True:
        if(len(clients) >= client_id):
            conn, addr = clients[client_id - 1]
            break

    return conn,addr

def read_config():
    # using readlines()
    count = 0
    
    with open("config.txt") as fp:
        Lines = fp.readlines()
        for line in Lines:
            count += 1
            print("Line{}: {}".format(count, line.strip()))
            command,data = line.split(':',1)

            if command == 'SENDTO':
                client_id,message = data.split(':',1)
                client_conn,addr = get_client(int(client_id))
                if client_conn != 0 and addr != 0 :
                    print(f'Send msg {message} to Client {addr}')
                    client_conn.send(f'RECEIVE:{message}'.encode())
                else:
                    print("client not found")
            else:
                print("Command is not recognized")


# Testing, delete later
def API_TEST(api, status = False):
    if status:
        arguments = [1,2,3,4,5,6,7,8,9,10]
        
        print("API TESTING:\tcalling SET with arguments:", arguments, "\n", "-"*50)
        for arg in arguments:
            
            # API SET Call Example
            tag = f"tag_{chr(ord('A') + arg)}"
            output = api.set(tag, arg)

            print(f'\t{api.EXECUTABLE} {api.PATH} SET {tag} {arg} \t --> \t {api.set(tag, arg)}', end="")
            
        print("\nAPI TESTING:\tcalling GET with arguments:", arguments, "\n", "-"*50)
        for arg in arguments:
            
            # API GET Call Example
            tag = f"tag_{chr(ord('A') + arg)}"
            output = api.get(tag)
            
            print(f'\t{api.EXECUTABLE} {api.PATH} GET {tag} \t --> \t {api.get(tag)}', end="")
        
        exit(1)



# Testing, delete later
API_TEST(api, status=API_TESTING)

# Create a socket for the server and start listening for incoming connections
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(SERVER_ADDRESS)
server_socket.listen()

print(f'Server listening on {SERVER_ADDRESS}')

threading.Thread(target=read_config).start()

# Continuously accept incoming client connections
while True:
    client_socket, client_address = server_socket.accept()
    threading.Thread(target=handle_client, args=(client_socket, client_address)).start()
