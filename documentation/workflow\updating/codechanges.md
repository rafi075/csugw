# Code Base & Changes
> This section documents core portions of the code base that are critical when adding new features / functionality. This will not give you a complete understanding of how the code works, but it is a good starting point.

## Table of Contents
- [Code Base \& Changes](#code-base--changes)
  - [Table of Contents](#table-of-contents)
  - [Bare Minimum](#bare-minimum)
  - [:page\_facing\_up: Test Server](#page_facing_up-test-server)
  - [:page\_facing\_up: Test Client](#page_facing_up-test-client)
  - [:page\_facing\_up: Server](#page_facing_up-server)
  - [:page\_facing\_up: Client](#page_facing_up-client)

## Bare Minimum
When importing the project, if you are working within the repository, you should work in a file structure to:
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

## [:page_facing_up: Test Server](../../communication/example/test-server.py)
> These test files demonstrate how you should use this software with an experiment in mind.

## [:page_facing_up: Test Client](../../communication/example/test-client.py)
> These test files demonstrate how you should use this software with an experiment in mind.


## [:page_facing_up: Server](../../communication/server.py)
> This file is critical to the code base, make minimal and thoughtful changes.


## [:page_facing_up: Client](../../communication/client.py)
> This file is critical to the code base, make minimal and thoughtful changes.


