import socket
import pandas as pd
import numpy as np
import pickle
from _thread import *
import sys
from ai_player import AIPlayer
from game import Game
from threads import *


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server = ''
port = 5555

server_ip = socket.gethostbyname(server)

try:
    s.bind((server, port))

except socket.error as e:
    print(str(e))

s.listen(10)
print("Waiting for a connection")

# Specify the initial parameters
num_cards = 6
player_id = 0
game = Game(num_cards)
start_new_thread(threaded_game_, (game,))

while True:
    # Accept any new player
    conn, addr = s.accept()
    print("Connected to: ", addr)
    # Assign ID to player
    player_id = 1
    assigned = False
    while not assigned:
        if player_id in list(game.connections.keys()):
            player_id += 1
        else:
            assigned = True
    # Update the number of players
    game.connections[player_id] = conn
    # Initialize the choices of the player
    game.choices[player_id] = "-1"
    # Distribute cards to player
    game.cards[player_id] = [game.pick_card("white")[0] for i in range(game.num_cards)]
    # Start new thread for this new player
    start_new_thread(threaded_client, (conn, player_id, game))
