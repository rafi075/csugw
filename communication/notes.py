
from server import Server
from client import Client
import protocol

#TODO:
# generalize process_message function to allow OSU
#   to give their own parsing logic
#   
#   
#
# 'Counter Method'
#
#   Send:
#       - be able to send data based on 'TAG'
#       - 
#       - 
#       - 
#
#

def taglogic():
    print("TAG Logic")


def logic(message:protocol.Protocol):
    if message.TAG == protocol.TAG_SEND:
        taglogic()

s = Server()
c = Client(s)


c.process_message("", "", logic)
