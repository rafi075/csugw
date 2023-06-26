from random import randint
import time
import lib_cli as CLI



# Psuedo Intercepted packet
def drop_packet(chance):
    rand = randint(0, 100)
    if rand <= chance:
        CLI.message_error(f"ATTACK: PACKET DROPPED")
        return True
    
# Psuedo DDOS attack    
def ddos(length_of_attack:int):
    CLI.message_error(f"ATTACK DDOS: {length_of_attack}s")
    time.sleep(length_of_attack)
    return True

def attack_lib():
    # 10% chance of dropping a packet
    rand = randint(0, 100)
    if rand <= 10:
        return drop_packet(10)
    

    # 10% chance of DDOS attack
    rand = randint(0, 100)
    if rand <= 10:
        return ddos(randint(1, 5))