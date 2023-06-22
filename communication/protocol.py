from enum import Enum
from string import Template
import socket
import json
import jsonschema
from node import Node


class ProtocolState(Enum):
    DEFAULT = "DEFAULT"
    FAIL = "FAIL"
    CONFIRM = "CONFIRM"


class ProtocolType(Enum):
    DIRECT = "DIRECT"
    BROADCAST = "BROADCAST"


class ProtocolMethod(Enum):
    DEFAULT = "DEFAULT"
    INIT = "INIT"
    EXIT = "EXIT"
    SHOW = "SHOW"
    TEST = "TEST"


class Field(Enum):
    ID = "ID"
    TYPE = "TYPE"
    METHOD = "METHOD"
    BODY = "BODY"
    STATE = "STATE"


DEFAULT_SCHEMA = {
    "type": "object",
    "properties": {
        Field.TYPE.name: {"type": "string"},
        Field.ID.name: {"type": "string"},
        Field.METHOD.name: {"type": "string"},
        Field.BODY.name: {"type": "string"},
        Field.STATE.name: {
            "type": "string",
            "enum": [state.value for state in ProtocolState],
        },
    },
    "required": [Field.TYPE.name, Field.ID.name, Field.METHOD.name],
}


class Protocol:
    def __init__(
        self,
        protocol_type: ProtocolType or str = ProtocolType.DIRECT,
        method: ProtocolMethod or str = ProtocolMethod.DEFAULT,
        state: ProtocolState or str = ProtocolState.DEFAULT,
        content: str = "",
        json_data: dict = None,
    ):
        self.method = self._validate_enum(method, ProtocolMethod)
        self.protocol_type = self._validate_enum(protocol_type, ProtocolType)
        self.state = self._validate_enum(state, ProtocolState)

        self.content = f"{content}"
        self.node = None
        self.data = {}

        self._populate_data(id="...")
        if json_data is not None:
            self._populate_from_json(json_data)
            self.data = {Field[key]: value for key, value in json_data.items()}
            if Field.ID.name not in self.data:
                self.data[Field.ID.name] = "0"

    @staticmethod
    def _validate_enum(value, enum):
        if isinstance(value, enum):
            return value
        elif isinstance(value, str):
            return (
                enum[value.upper()]
                if value.upper() in enum.__members__
                else enum.DEFAULT
            )
        return enum.DEFAULT

    def _populate_data(self, id="..."):
        self.data = {
            Field.TYPE: self.protocol_type.value,
            Field.ID: id,
            Field.METHOD: self.method.value,
            Field.BODY: self.content,
            Field.STATE: ProtocolState.DEFAULT.value,
        }

    def _populate_from_json(self, json_data):
        self.method = ProtocolMethod[json_data[Field.METHOD.name]]
        self.protocol_type = ProtocolType[json_data[Field.TYPE.name]]
        self.state = ProtocolState[json_data[Field.STATE.name]]
        self.content = json_data[Field.BODY.name]

    def get_data(self, node=None) -> dict:
        self.node = node
        self._populate_data(id="...")

        data = {key.name: value for key, value in self.data.items()}
        jsonschema.validate(instance=data, schema=DEFAULT_SCHEMA)
        return data

    def to_network(self, node=None, encoding="ascii") -> str:
        return json.dumps(self.get_data(node)).encode(encoding)

    @staticmethod
    def from_network(message):
        data = json.loads(message)
        return Protocol(json_data=data)

    def msg(self) -> str:
        return json.dumps(self.get_data(self.node))

    def __str__(self):
        return self.msg()

    def __bool__(self):
        try:
            # self.get_data()
            self._populate_data(id="...")
        except:
            print("Failed to get data")
            return False

        content_size = len(self[Field.BODY])
        method_size = len(self[Field.METHOD])

        broadcast_requires_body = (
            self[Field.TYPE] == ProtocolType.BROADCAST.value
            and len(self[Field.BODY]) > 0
        )
        return broadcast_requires_body or self[Field.TYPE] == ProtocolType.DIRECT.value

    # Returns True if some string command matches the command for this object
    def __eq__(self, __value: object) -> bool:
        if type(__value) is Protocol:
            return self[Field.METHOD] == __value[Field.METHOD]
        if type(__value) is str:
            return self[Field.METHOD] == __value
        if type(__value) is ProtocolMethod:
            return self[Field.METHOD] == __value.value
        return False

    def __getitem__(self, key: Field or str):
        if type(key) is Field:
            return self.data[key]
        elif type(key) is str:
            for key, value in self.data.items():
                if key.name == key:
                    return value

    def __setitem__(self, key: Field, value):
        self.data[key] = value

    @staticmethod
    def has_key(key: str, obj: Enum):
        try:
            obj[key]
            return True
        except:
            return False


class Protocols:
    INITIALIZE = Protocol(
        method=ProtocolMethod.INIT,
        state=ProtocolState.DEFAULT,
        content="Initialize",
    )

    DISCONNECT = Protocol(
        method=ProtocolMethod.EXIT,
        state=ProtocolState.DEFAULT,
        content="Disconnect",
    )

    SHOW = Protocol(
        method=ProtocolMethod.SHOW,
        state=ProtocolState.DEFAULT,
        content="Show",
    )


class Validator:
    @staticmethod
    def validate(format_str: str, input_str: str, delim: str = "::") -> bool:
        format_parts = format_str.split(delim)
        input_parts = input_str.split(delim)

        if len(format_parts) != len(input_parts):
            return False

        for format_part, input_part in zip(format_parts, input_parts):
            if not Validator.is_valid_input(format_part, input_part):
                return False

        return True

    @staticmethod
    def is_valid_input(format_part: str, input_part: str) -> bool:
        if format_part == "%d":
            return input_part.isdigit()
        elif format_part == "%f":
            return Validator.is_float(input_part)
        elif format_part == "%s":
            return Validator.is_string(input_part)
        return False

    @staticmethod
    def is_float(s: str) -> bool:
        try:
            float(s)
            return True
        except ValueError:
            return False

    @staticmethod
    def is_string(s: str) -> bool:
        return not s.isdigit() and not Validator.is_float(s)
