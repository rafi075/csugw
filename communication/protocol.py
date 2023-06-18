import socket

class Command:
    OK = "OK"
    FAIL = "FAIL"
    CONFIRMED = "CONFIRMED"
    DELIM = ":"
    def __init__(self, 
                 command:str = "default_command", 
                 name:str = "default_name", 
                 requires_confirmation:bool = False,
                 description:str = "default_description"):
        
        # Basic command Information
        self.command_name = f"{name}"
        self.command = f"{command}"
        self.description = f"{description}"
        self.requires_confirmation = requires_confirmation

        # Should always have AT LEAST these keys
        self.response_status = {
            Command.OK : f"{self.command}_OK",
            Command.FAIL : f"{self.command}_FAIL",
            Command.CONFIRMED : f"{self.command}_CONFIRMED",
        }

        # Manually set
        # Optional but helpful interaction information
        self.srcAddr:socket._Address = None
        self.dstAddr:socket._Address = None

        self.signature:str = ""

        # TODO: Look into a template to ensure protocol spec is followed
    
    # Converts Command to sendable message
    def msg(self, status:str = "") -> str:
        if status:
            # TODO: Consider error checking this
            return f"{self.response_status[status]}"

        if self.signature:
            return f"{self.signature}{Command.DELIM}{self.command}"
        else:
            return f"{self.command}"

    def __str__(self):
        return self.msg()
        
    # Returns True if some string command matches the command for this object
    def __eq__(self, __value: object) -> bool:
        if type(__value) is str:
            return self.command in __value
        return False

class Protocol:

    INITIALIZE = Command(
        command="INIT", 
        name="Initialize", 
        requires_confirmation=True,
        description = "Initializes a node/connection"
    )

    DISCONNECT = Command(
        command="exit", 
        name="Disconnect", 
        requires_confirmation=True,
        description = "Disconnects a node from the server"
    )

    SHOW = Command(
        command="SHOW", 
        name="Show", 
        requires_confirmation=False,
        description = "Makes the Server print information about all connected nodes"
    )

