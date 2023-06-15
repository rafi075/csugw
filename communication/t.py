import socket
import threading

class ServerThread(threading.Thread):
    def __init__(self, host = '127.0.0.1', port = 5000):
        threading.Thread.__init__(self)
        self.host = host
        self.port = port
        self.running = True

    def run(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((self.host, self.port))
        self.sock.listen(1)
        print(f'Server started on {self.host}:{self.port}')

        while self.running:
            conn, addr = self.sock.accept()
            print(f'Connection from {addr}')
            conn.close()

    def stop(self):
        self.running = False
        # Creating a dummy connection to wake up the server socket from accept()
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.host, self.port))
        s.close()
        self.sock.close()


class InputThread(threading.Thread):
    def __init__(self, server):
        threading.Thread.__init__(self)
        self.server = server

    def run(self):
        while True:
            cmd = input('Enter command:')
            if cmd == 'stop':
                self.server.stop()
                break


if __name__ == "__main__":
    server_thread = ServerThread()
    server_thread.start()

    input_thread = InputThread(server_thread)
    input_thread.start()

    server_thread.join()
    input_thread.join()
