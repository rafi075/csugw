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

***What is a protocol?*** 

A protocol is similar to a language. For example, the English language is just a collection of mouth noises. However, we have collectively agreed that certain noises have meaning. Using a language is that same as using a protocol; it is agreeing that noises have meaning. The language in use is no different than the protocol in use. When a person communicates using a language another person does not know, it is as if gibberish is being spoken. The same circumstance happens with computers when they communicate. Therefore, we need to define a protocol (language) that contains the relevant 'meaning' for this project.


Below is the schema definition of a protocol. A schema is similar to an alphabet or dictionary for a language; essentially the anatomy of the protocol. As you can see, the elements that make up a protocol are all members of the `Field` class, as shown by `Field.TYPE.name`. Therefore, it we wanted to add a timestamp to every network message, we would need to add a `timestamp` attribute to the `Field` class, then to the schema. 
```python
DEFAULT_SCHEMA = {
    "type": "object",
    "properties": {
        Field.TYPE.name:      {"type": "string"},
        Field.ID.name:        {"type": "string"},
        Field.METHOD.name:    {"type": "string"},
        Field.BODY.name:      {"type": "string"},
        Field.STATE.name: {
            "type": "string",
            "enum": [state.value for state in ProtocolState],
        },
    },
    "required": [Field.TYPE.name, Field.ID.name, Field.METHOD.name],
}
```

Below is the definition of what felids are allowed, and furthermore, what values are allowed for each field type. 
```python
class Field(Enum):
    ID              = "ID"
    TYPE            = "TYPE"
    METHOD          = "METHOD"
    BODY            = "BODY"
    STATE           = "STATE"

class ProtocolState(Enum):
    DEFAULT         = "DEFAULT"
    FAIL            = "FAIL"
    # [...]

class ProtocolType(Enum):
    DIRECT          = "DIRECT"
    BROADCAST       = "BROADCAST"

class ProtocolMethod(Enum):
    DEFAULT         = "DEFAULT"
    # [...]
```
> If you notice in the schema `{"type": "string"}` indicates that each field in the protocol is a `string` type -- this is true, and the enums defined above are ultimately converted to strings. However, I used this implementation of enum's to hopefully make your development experience easier as you are able to use intellisense to help guide your programming: ![intelisense](https://github.com/rafi075/csugw/assets/78711391/92d58caf-2bd9-440e-a5bc-980a1b86a49a)

The `Protocol` class aims to provide an easy way for you to define and understand network messages in this project as it manages validation, string parsing, and intellisense operations based on the definitions provided above.

I have implemented some basic functionalities around the protocol type definitions above. These protocol components are the baseline and should not be removed without a full understanding of the code base. However, adding new protocol components is a requirement for new features! For a full walkthrough on how to add a feature, follow [this guide](./adding_a_feature.md).



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

