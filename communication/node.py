import ipaddress as ip
import socket

import jsonschema
from lib_cli import print_array, table, message

DEFAULT_IP = "10.1.2.1"
DEFAULT_PORT = 5000
DEFAULT_GATEWAY = "10.1.1.1"

class Node:
    def __init__(
        self,
        socket: socket.socket,
        ID: str = "Default",
        tags: list = [],
        IP: str or ip.IPv4Address = DEFAULT_IP,
        PORT: str or int = DEFAULT_PORT,
        net_mask: str or int = 24,
        gateway: str or ip.IPv4Address = DEFAULT_GATEWAY,
        config_data: dict = None,
    ):
        self.socket = socket
        peerName = socket.getpeername()

        def default(data, key, default):
            return data[key] if key in data else default
        
        if config_data is not None:
            self.ID = config_data["ID"]
            self.IP = ip.IPv4Address(str(config_data["IP"]))
            self.PORT = default(config_data, "PORT", int(peerName[1]))

            if "." in str(config_data["SUBNET_MASK"]):
                self.net_mask = (config_data["SUBNET_MASK"], Node.netmask_to_cidr(config_data["SUBNET_MASK"]))
            else:
                self.net_mask = (Node.cidr_to_netmask(config_data["SUBNET_MASK"]), config_data["SUBNET_MASK"])
        else:
            self.ID = ID
            self.PORT = int(peerName[1])
            self.IP = ip.IPv4Address(str(peerName[0]))
        
            if "." in str(net_mask):
                self.net_mask = (net_mask, Node.netmask_to_cidr(net_mask))
            else:
                self.net_mask = (Node.cidr_to_netmask(net_mask), net_mask)
        
        self.network_string = str(self.IP) + ":" + str(self.PORT)
        self.network = f""

        # print(self.IP)
        self.gateway = ip.IPv4Address(str(gateway))
        self.network = ip.IPv4Network(
            f"{'.'.join(str(self.IP).split('.')[:-1])}.0/{str(self.net_mask[1])}"
        )


        if config_data is not None:
            self.neighbors = default(config_data, "NEIGHBORS", [])
            self.tags = config_data["TAGS"]
        else:
            self.neighbors = []
            self.tags = tags

        self.help = HelpMenu(
            self,
            generic_data_keys=[
                "ID",
                "IP",
                "net_mask",
                "tags",
                # 'PORT',
                # 'network',
                # 'gateway',
                # 'neighbors',
            ],
        )

    def show(self, compact: bool = True, basic: bool = False):
        self.help.show(compact=compact, basic=basic)

    def get_basic(self) -> tuple:
        return (self.ID, self.IP, self.net_mask, self.tags)

    def get_data(self, data=["ID", "IP", "PORT", "net_mask", "tags", "neighbors"]):
        _data = {}
        for k, v in vars(self).items():
            if k in data:
                _data.update({k: v})
        return _data

    def close(self) -> None:
        self.socket.close()

    def send(self, data: str, encoding="ascii") -> None:
        self.socket.send(data.encode(encoding))

    def read(self, buff_size: int = 1024, decoding: str = "ascii") -> str:
        return self.socket.recv(buff_size).decode(decoding)

    @staticmethod
    def netmask_to_cidr(network_mask: str) -> str:
        return ip.IPv4Network(f"0.0.0.0/{network_mask}").prefixlen

    @staticmethod
    def cidr_to_netmask(cidr):
        mask = (0xFFFFFFFF >> (32 - cidr)) << (32 - cidr)
        return f"{(mask >> 24) & 0xff}.{(mask >> 16) & 0xff}.{(mask >> 8) & 0xff}.{mask & 0xff}"
    
    

class HelpMenu:
    SPACING = 80

    def __init__(self, parent, generic_data_keys=[]):
        self.parent = parent
        self.compact = False
        self.generic_data = {
            k: v for k, v in vars(self.parent).items() if k in generic_data_keys
        }

    def show(
        self, compact: bool = True, basic: bool = False, verbose: bool = True
    ) -> str:
        self.compact = compact
        title = self.get_title(basic)
        data = self.generic_data.items() if basic else vars(self.parent).items()
        message(f"{title}", width=HelpMenu.SPACING + 29 + 8)
        return table(
            self.get_attributes(data),
            headers=self.get_headers(compact),
            indent_level=1,
            verbose=verbose,
        )

    def get_title(self, basic: bool) -> str:
        style = self.get_style(basic)
        return f"Class Contents - {style} - [{self.parent.__class__.__name__}]"

    def get_style(self, basic: bool) -> str:
        if basic:
            return "Basic"
        return "Compact" if self.compact else "Easy Read"

    def get_headers(self, compact: bool) -> list[str, str]:
        return None if compact else ["Variable / Attribute", "Value"]

    def get_attributes(self, data) -> list:
        attributes = []
        for attr, value in data:
            if not isinstance(value, HelpMenu):
                if isinstance(value, dict):
                    attributes.append(self.handle_dict(attr, value))
                elif isinstance(value, list):
                    [attributes.append(a) for a in self.handle_list(attr, value)]
                else:
                    attributes.append(self.get_standard_attribute(attr, value))
        return attributes

    def handle_list(self, attr: str, value: list) -> list:
        if not self.compact:
            list_attributes = [
                self.get_list_attribute(
                    attr, f"[{len(value)}]" if not self.compact else str(value)
                )
            ]
            if len(value) == 0:
                list_attributes.append(
                    self.get_item_attributes(
                        f"⠀{'⠀':>{HelpMenu.SPACING/2+2}} {f'[] ──╯'}",
                        f"╰─── Empty List",
                    )
                )
            else:
                for i in range(len(value)):
                    list_attributes.append(
                        self.get_item_attributes(
                            f"⠀{'⠀':>{HelpMenu.SPACING/2+1}} {f'[{str(i)}] ──╯'}",
                            f"╰─>  {value[i]}",
                        )
                    )
        else:
            list_attributes = [
                self.get_standard_attribute(
                    attr, f"[{len(value)}]" if not self.compact else str(value)
                )
            ]

        return list_attributes

    def handle_dict(self, attr: str, value: dict) -> list:
        dict_attributes = [self.get_standard_attribute(attr, "[...]")]
        attributes = [
            self.get_standard_attribute(
                f"{'-':>20} {key:<15} =", self.get_name_or_val(val)
            )
            for key, val in value.items()
        ]
        return dict_attributes + attributes

    def get_standard_attribute(self, attr: str, value: any) -> list[str, str]:
        output = value
        if type(value) == socket.socket:
            output = f"SRC: {value.getpeername()[0]}:{value.getpeername()[1]}"
        return [
            f"{attr:<{int(HelpMenu.SPACING/2 + 9)}} =",
            f"{str(output):<{int(HelpMenu.SPACING/2)}}{'⠀'}",
        ]

    def get_list_attribute(self, attr: str, value: any) -> list[str, str]:
        return [
            f"{attr:<{int(HelpMenu.SPACING/2)}} {'Index ──╮' if not self.compact else '='}",
            f"╭── Values {str(value):<{int(HelpMenu.SPACING/2)}}{'⠀'}",
        ]

    def get_item_attributes(self, prefix: str, item: any) -> list[str, str]:
        item_name = item if isinstance(item, list) else [item]
        return [prefix, *item_name]

    def get_name_or_val(self, value) -> str:
        return value.__name__ if hasattr(value, "__name__") else value

