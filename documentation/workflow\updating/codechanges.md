# Code Base & Changes
> This section documents core portions of the code base that are critical when adding new features / functionality. This will not give you a complete understanding of how the code works, but it is a good starting point.

## Table of Contents
- [Code Base \& Changes](#code-base--changes)
  - [Table of Contents](#table-of-contents)
  - [Project: Bare Minimum](#project-bare-minimum)
- [Data Flow](#data-flow)
  - [:page\_facing\_up: Test Server](#page_facing_up-test-server)
      - [Send Hook](#send-hook)
      - [Receive Hook](#receive-hook)
  - [:page\_facing\_up: Test Client](#page_facing_up-test-client)
      - [Send Hook](#send-hook-1)
      - [Receive Hook](#receive-hook-1)
  - [:page\_facing\_up: Protocol](#page_facing_up-protocol)
  - [:page\_facing\_up: Server](#page_facing_up-server)
      - [Receive Message](#receive-message)
      - [Process Message](#process-message)
  - [:page\_facing\_up: Client](#page_facing_up-client)
      - [Receive Message](#receive-message-1)
      - [Process Message](#process-message-1)

## Project: Bare Minimum
When importing the project, if you are working within the repository, you should work in a file structure similar to:
```
├── csugw
│  ├── communication
│  │  ├── server.py
│  │  ├── client.py
│  │  ├── [...]
│  │  ├── example
│  │  │  ├── test-client.py
│  │  │  └── test-server.py
│  │  └── experimentOne        <--- New Project
│  │     ├── osu-client.py
│  │     └── osu-server.py
│  └── [...]
```
With this configuration, you can import the communication library to the project using the following code:
```python
import sys
sys.path.append("..")

from client import Client
from server import Server
import lib_cli as CLI
```
Finally, you can build a minimally working project with:
```python
# csugw/communication/experimentOne/osu-client.py
def send_hook(client: Client, obj: socket.socket, message: Protocol or str):
    return False

def receive_hook(client: Client, obj: socket.socket, message: Protocol or str):
    return False

client = Client(
    "DefaultID", host="10.1.1.1", port=5000, send_hook=send_hook, receive_hook=receive_hook
)

client.run()
```
and 
```python
# csugw/communication/experimentOne/osu-server.py
def send_hook(server: Server, client: Node, message: Protocol or str):
    return False

def receive_hook(server: Server, client: Node, message: Protocol or str):
    return False

server = Server(
    host="10.1.1.1", port=5000, send_hook=send_hook, receive_hook=receive_hook
)

server.run()
```

The example project is only slightly more complicated as it includes command line arguments and rudimentary  function logic.
On the Windows Host Machine, execute the following in a powershell terminal:
```powershell
cd csugw/communication/experimentOne/
python3.exe osu-server.py
```

# Data Flow
> This section covers core elements of how this software works. **I recommend that you understand the data flow of the project in order to fully understand how the hooks work and when they are called.**

## [:page_facing_up: Test Server](../../communication/example/test-server.py)
> These test files demonstrate how you should use this software with an experiment in mind.

#### Send Hook
```python
def send_hook(server: Server, client: Node, message: Protocol or str):
    return False
```

#### Receive Hook
```python
def receive_hook(server: Server, client: Node, message: Protocol or str):
    return False
```

## [:page_facing_up: Test Client](../../communication/example/test-client.py)
> These test files demonstrate how you should use this software with an experiment in mind.
#### Send Hook
```python
def send_hook(client: Client, obj: socket.socket, message: Protocol or str):
    return False
```

#### Receive Hook
```python
def receive_hook(client: Client, obj: socket.socket, message: Protocol or str):
    return False
```

## [:page_facing_up: Protocol](../../communication/protocol.py)
> - The snippets below have been simplified for understandability.
> - This file is critical to the code base, make minimal and thoughtful changes.

## [:page_facing_up: Server](../../communication/server.py)
> - This file is critical to the code base, make minimal and thoughtful changes.
> - The snippets below have been simplified for understandability.

#### Receive Message
```python
def __receive_data(self, sock, mask):
    # Receive data from network
    message = sock.recv(1024).decode("ascii")
    # Transform data into a protocol
    message: Protocol = Protocol.from_network(message)

    # Process message
    # (potentially call receive_hook() from test-client.py)
    self.__process_message(message, is_receiving=True)
```

#### Process Message
```python
def __process_message(self, message: Protocol, is_receiving=False):
    if message == ProtocolMethod.EXIT:
        pass
    # [...]
    # If message/command was not a 'default' protocol (INIT, EXIT, etc.)
    # then process hooks
    if self.receive_hook is not None and is_receiving:
        # Calls receive_hook() from test-client.py
        return self.receive_hook(self, self.sock, message)
    
    if self.send_hook is not None and not is_receiving:
        # Calls send_hook() from test-client.py
        return self.send_hook(self, self.sock, message)

    return False
```


## [:page_facing_up: Client](../../communication/client.py)
> - The snippets below have been simplified for understandability.
> - This file is critical to the code base, make minimal and thoughtful changes.

#### Receive Message
```python
def __receive_data(self, sock, mask):
    # Receive data from network
    message = sock.recv(1024).decode("ascii")
    # Transform data into a protocol
    message: Protocol = Protocol.from_network(message)

    # Process message
    # (potentially call receive_hook() from test-client.py)
    self.__process_message(message, is_receiving=True)
```

#### Process Message
```python
def __process_message(self, message: Protocol, is_receiving=False):
    if message == ProtocolMethod.EXIT:
        pass
    # [...]
    # If message/command was not a 'default' protocol (INIT, EXIT, etc.)
    # then process hooks
    if self.receive_hook is not None and is_receiving:
        # Calls receive_hook() from test-client.py
        return self.receive_hook(self, self.sock, message)
    
    if self.send_hook is not None and not is_receiving:
        # Calls send_hook() from test-client.py
        return self.send_hook(self, self.sock, message)

    return False
```

