# Adding A Feature
> This section documents how to add a simple feature

## Table of Contents
- [Adding A Feature](#adding-a-feature)
  - [Table of Contents](#table-of-contents)
  - [Demo Feature](#demo-feature)
  - [Protocol](#protocol)
  - [Server](#server)
      - [Send](#send)
      - [Receive](#receive)
  - [Client](#client)

## Demo Feature
Let's add a `DEMO` feature. For simplicity sake, let's define some steps for what our `DEMO` feature should do:
- Server
  - Create a random number
  - Send the random number to a client
- Client:
  - Receive the number
  - Print the initial number
  - Double the number & print it
  - Send the doubled number back to the server

With this purpose in mind, we can generalize the development paths into 3 general areas:
1. [Protocol](#protocol) 
   - How Sever and Client would know that our `DEMO` feature is 'happening'?
2. [Server logic](#server)
   - Where and how will the server create a random number?
   - Which client will the server send the random number to?
3. [Client logic](#client)
   - Where and how will the client print the number?
   - Where and how will the client know when and what to double?

## Protocol
>Please refer to the [protocol documentation](./codechanges.md#📄-protocol) if you are unclear on what a protocol.

Here is the default protocol schema. It demands that every message *at least* contain a `TYPE`, `ID`, and `METHOD` field. This schema will suffice for the `DEMO` feature as we can distinguish a `DEMO` network message from any other network message based on the value of the `METHOD` field.
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
To be as clear as possible, here is an example of a network message used for initializing nodes, slightly simplified for clarity, but still adhering to the schema. It is sent from the server to a client. It's `METHOD` field has the value of `INIT`, indicating it's purpose:
```json
{
	"TYPE"   : "DIRECT",
	"ID"     : "Server",
	"METHOD" : "INIT"
}
```
Here is the exact same message, but the `METHOD` field is set to `DEMO`, indicating a different purpose than `INIT`.
```json
{
	"TYPE"   : "DIRECT",
	"ID"     : "Server",
	"METHOD" : "DEMO"
}
```

However, to give the `METHOD` value of "DEMO" any meaning, we need to define it in the protocol. Since the protocol schema already accepts `ProtocolMethod` as a value type for field `TYPE.METHOD` (as defined by `Field.METHOD.name`), we only need to define a new possible value for `ProtocolMethod`. That way, the new value of "DEMO" can be seen as a legitimate value for `METHOD`. 

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
```
To do this, we simply define a new entry in `ProtocolMethod`:
```python
class ProtocolMethod(Enum):
    DEFAULT         = "DEFAULT"
    DEMO            = "DEMO"
```
Now, all network traffic and devices understand that `DEMO` is a `METHOD`... but nothing knows what `DEMO` does!

## Server
>Please refer to the [server documentation](./codechanges.md#📄-test-server) if you you are not familiar with the `receive_hook()`, `send_hook()`, or the idea of hooking.
>
> Encouraged, but not required: a look at the [core of the server](./codechanges.md#📄-server)

Let's start with a [bare bones client and server implementation](./codechanges.md#project-bare-minimum). Be sure to import random for our `DEMO` feature for the server.
```python
from random import randint
```
<br>

#### Send
Our first step as the server is to create a random number. Where and when will this happen? This somewhat depends on the purpose of the feature being added. However, for `DEMO`, the server is the source of the command, and thus in charge of when the event happens. For simplicity sake, let's have the user trigger the event via a CLI command. 
> Designed for testing, both `client.py` and `server.py` parse CLI input and check if the first word (`input.split(" ")[0]`) matches a `ProtocolMethod`. If so, the CLI input is packaged as a `Protocol`, with the first word being the `METHOD` and the remaining input being the `BODY`. The message is sent to the `__process_message()` function where user defined hooks may be called.

Since the user is triggering the event via a CLI command, the `send_hook()` function will be called when the user types `DEMO`. This answers the when and where question of our server logic. The implementation of this logic is shown below:
```python
# WHERE: send_hook() --> example/test-server.py
def send_hook(server: Server, client: Node, message: Protocol or str):
    # WHEN: 
    # Check if the current `message` is of type `DEMO`
    if message == ProtocolMethod.DEMO:
        pass

    return False
```
Next we need to implement the logic / purpose of `DEMO` with respect to the server ([shown here](#demo-feature)). We need to:
- Create a random number
- Send the random number to a client
```python
# WHERE: send_hook() --> example/test-server.py
def send_hook(server: Server, client: Node, message: Protocol or str):
    # WHEN: 
    # Check if the current `message` is of type `DEMO`
    if message == ProtocolMethod.DEMO:
        # Create a random number
        number = randint(1, 100)

        # Package the random number into a protocol / message
        # We can just use the `message` parameter
        message.content = str(number)

    # Send the random number to a client
    server.send(client, message)
    return False
```
But which client are we sending to? This is answered by the implementation of the CLI input test feature. The simplified code below, in both `server.py` and `client.py`, reveals that the server broadcasts messages triggered from the command line:
```python
message = input()
if message is ProtocolMethod:
    for client in self.__clients:
        self.__process_message(client, message, is_receiving=False)

""" 
 __process_message(client, message, ...):
    if is_receiving == False
        send_hook(client, message, ...)     <-- hook from test-server.py
"""
```
There are many other ways to specify which client to send messages to. However, this style will be simplest for this example. 

#### Receive
We now need to consider whether the server needs any logic when receiving a message of type `DEMO`. Based on the [steps](#demo-feature) for our `DEMO` feature, we do not need any logic when the server receives a `DEMO` message, therefore we can just print the message body.
```python
def receive_hook(server: Server, client: Node, message: Protocol or str):
    # only printing the message body if it is a `DEMO` message
    if message == ProtocolMethod.DEMO:
        # Using CLI library for pretty printing
        CLI.message_ok(f"DEMO: {message.content}")
    return False
```



## Client
>Please refer to the [client documentation](./codechanges.md#📄-test-client) if you you are not familiar with the `receive_hook()`, `send_hook()`, or the idea of hooking.
>
> Encouraged, but not required: a look at the [core of the client](./codechanges.md#📄-client)