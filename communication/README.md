# Communication Library

## Table of Contents

- [Communication Library](#communication-library)
  - [Table of Contents](#table-of-contents)
  - [:page_facing_up: Server](#-server)
    - [Requirements](#requirements)
    - [Exmaple Usage](#exmaple-usage)
    - [Key Components](#key-components)
  - [:page_facing_up: Client](#-client)
    - [Requirements](#requirements-1)
    - [Exmaple Usage](#exmaple-usage-1)
    - [Key Components](#key-components-1)
  - [:page_facing_up: API Wrapper](#-api-wrapper)
    - [Variables](#variables)
    - [Methods](#methods)
    - [Expected API Behavior](#expected-api-behavior)

## [:page_facing_up:](./server.py) Server

Python chat server that listens for client connections on a specified IP address and port.

### Requirements

- `config.txt`

### Exmaple Usage

1. Start the server to begin listening for client connections:

    ```bash
    python3 ./server.py
    ```

2. Connect a client to the server with `client.py`:

    ```bash
    python3 ./client.py
    ```

3. Validate client connection:<br>
    ***TODO: ADD IMAGE***

### Key Components

The server program has several important components:

- `handle_client()`

    This function is responsible for continuously reading incoming messages from each connected client. If a client sends a `SEND` command, the server relays the message to all other clients. If the command is `SENDTO`, the server finds the specified client and sends the message to them.

- `get_client()`

    This function is used to fetch a particular client from the list of connected clients based on its ID.

- `read_config()`

    This function reads from a configuration file named `config.txt`. It interprets commands in this file and sends messages to specified clients.

- `API`

    The server uses an API class from another script (as defined in api.py). This class provides a way to interface with an external program, although the server script doesn't directly use this API in handling client connections.

## [:page_facing_up:](./client.py) Client

Python client that connects to a server using a specified IP address and port.

### Requirements

- `config.txt`

### Exmaple Usage

1. Start the server to begin listening for client connections:

    ```bash
    python3 ./server.py
    ```

2. Connect a client to the server with `client.py`:

    ```bash
    python3 ./client.py
    ```

3. Validate client connection:<br>
    ***TODO: ADD IMAGE***

### Key Components

- `send_messages()`

     This function continuously reads user input from the console and sends the input as messages to the server. Each message is prefixed with 'SEND:' to indicate to the server that it's a message to be relayed.

- `receive_messages()`

     This function continuously reads incoming messages from the server and prints them to the console. It only prints messages that are prefixed with 'RECEIVE:', which are the ones relayed from the server.

## [:page_facing_up:](./api.py) API Wrapper

This module provides a Python wrapper for an external command line program. The main purpose of this API is to allow Python scripts to interface with the external programs, which would be typically used in a command line context. This is done by executing shell commands from within Python code and retrieving its output. The primary use of this API will be to communicate with the Simulator API.

The API has two public methods, `get(tag)` and `set(tag, value)`. `get(tag)` retrieves the value of a given `tag` from the Simulator, while set changes the `value` of a specified `tag`.

### Variables

- `EXECUTABLE`

    This variable stores a string which will be used to execute the file specified by `PATH`. For a console command such as:

        python3 /root/main.py 1 2 3

    The value for `EXECUTBLE` would be `python3`. Setting `EXECUTBLE` allows for reduced code verbosity, as the methods below will use `EXECUTBLE` rather than arguments.

- `PATH`

    This variable stores a string file path which will be executed by `EXECUTABLE`. For a console command such as:

        python3 /root/main.py 1 2 3

    The value for `PATH` would be `/root/main.py`. Setting `PATH` allows for reduced code verbosity, as the methods below will use `PATH` rather than arguments.

### Methods

- `execute (*args)`

    This is the main method that interacts with the Simulator. It runs a command on the Simulator and returns the output. The command to run and its arguments are passed as parameters.

- `_exec(executable, path, *args)`

    This method handles the interaction with the subprocess module to execute the command on the Simulator. It returns either the standard output of the Simulator or an error message if the command fails.

- `get(tag)`:

    This method retrieves a tag value from the Simulator.

- `set(tag, value)`:

    This method sets a tag value in the Simulator.

### Expected API Behavior

The API expects commands to be either `GET` or `SET`, followed by a `TAG`. For `SET`, it additionally expects a `VALUE`. The returned format should follow:

     TAG - COMMAND - OPTIONAL_ARG - FAILURE_STATUS
     ---------------------------------------------
     TAG - SET - VALUE - (0 || 1 )
     TAG - GET - (0 || 1 )
