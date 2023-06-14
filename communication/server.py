import socket
import threading
from time import sleep
from api import API
import lib_cli as CLI

VERBOSE = False

# Define the IP address and port number that the server will listen on
SERVER_ADDRESS = ('127.0.0.3', 5000)
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


# Define the executable and file path for the API
api = API()
api.EXECUTABLE = "python"
api.PATH = "api-testfile.py"
API_TESTING = False

# Define a list to store all connected clients
clients = []
ins = []

# Define a threading variables
threads = []
threads_lock = threading.Lock()
threads_active = True


# Define a function to handle incoming client connections
def handle_client(client_socket, client_address):
    global threads_active
    print(CLI.color("cyan", f'Client {client_address} connected'))

    # Add the client to the list of connected clients
    clients.append((client_socket, client_address))

    # Continuously read incoming messages from the client
    while True:
        data = client_socket.recv(1024).decode()
        if not data:
            break

        if data == "SHUTDOWN":
            client_socket.close()
            # clients.remove((client_socket, client_address))
            server_socket.close()
            threads_active = False
            print()
            CLI.message(CLI.color("red", f"Server Shutting Down"))
            # threading.current_thread().join()
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
    print(CLI.color("cyan", f'Client {client_address} disconnected'))

def get_client(client_id):

    conn = 0
    addr = 0
    while True:
        if(len(clients) >= client_id):
            conn, addr = clients[client_id - 1]
            break

    return conn,addr

def read_config():
    count = 0
    with open("config.txt") as fp:
        Lines = fp.readlines()
        for line in Lines:
            count += 1
            if VERBOSE: print("Line{}: {}".format(count, line.strip()))
            command,data = line.split(':',1)

            if command == 'SENDTO':
                client_id,message = data.split(':',1)
                client_conn,addr = get_client(int(client_id))
                if client_conn != 0 and addr != 0 :
                    if VERBOSE: print(f'Send msg {message} to Client {addr}')
                    client_conn.send(f'RECEIVE:{message}'.encode())
                else:
                    print("client not found")
            else:
                print("Command is not recognized")


def show_clients():
    for c, addr in clients:
        print(f'Client {addr} connected')
    pass

def show_client(index:int):
    print(f"Client [{index}]")
    pass

def show_server_status():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    state = (s.connect_ex(SERVER_ADDRESS) == 0)
    s.close()
    txt = CLI.color("green" if state else "red", (f"Server Online -  {SERVER_ADDRESS[0]}:{SERVER_ADDRESS[1]}" if state else "Server Offline"))
    CLI.message(txt)


def shutdown(server=True):
    global server_socket

    # Check if server_socket is still open
    if server:
        # Creating a dummy connection to wake up the server socket from accept()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        if (s.connect_ex(SERVER_ADDRESS) == 0):
            s.send(f'SHUTDOWN'.encode())
        s.close()
        CLI.message(CLI.color("red", f"Shutting Down: Server"))
        sleep(1)
        shutdown(server=False)
    else:
        CLI.reset_color()
        CLI.message(CLI.color("red", f"Shutting Down: CLI"))
        exit()


def main():
    # Create a socket for the server and start listening for incoming connections
    global server_socket

    server_socket.bind(SERVER_ADDRESS)
    server_socket.listen()

    # Start CLI and sever thread
    with threads_lock:
        # threads.append(threading.Thread(target=read_config))
        threads.append(threading.Thread(target=CLI.input_loop, kwargs={}))
        CLI.message(CLI.color("green", f"Server Active -  {SERVER_ADDRESS[0]} : {SERVER_ADDRESS[1]}"))

        for thread in threads:
            thread.start()

    # Continuously accept incoming client connections
    try:
        while server_socket.fileno() != -1:
            if (server_socket.connect_ex(SERVER_ADDRESS) != 0):
                break

            client_socket, client_address = server_socket.accept()
            new_thread = threading.Thread(target=handle_client, args=(client_socket, client_address))
            threads.append(new_thread)
            new_thread.start()

    except KeyboardInterrupt:
        shutdown()


    for thread in threads:
        thread.join()

    exit()

if __name__ == '__main__':
    main()
