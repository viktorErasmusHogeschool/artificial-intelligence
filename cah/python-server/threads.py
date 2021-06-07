import pandas as pd
import numpy as np
import pickle


def threaded_game_(game):
    while True:
        if len(game.connections) >= 1:
            game.check_round()
        else:
            pass

def threaded_client(conn, player_id, game):
    # Send initial sample to player
    conn.send(pickle.dumps({player_id: [game.cards[player_id], game.black_card]}))
    while True:
        try:
            data = pickle.loads(conn.recv(4096))
            if data is None:
                conn.send(str.encode("Goodbye"))
                break
            else:
                # Check for card submission
                if isinstance(data, dict):
                    game.update_choices(data)
                # Flag to begin new round
                elif isinstance(data, str):
                    game.checkpoints[player_id] = 1
                    print("Received {} from Player {}".format(data, player_id))

                # Return game status in any case
                reply = [game.players_status(), game.update_score(), game.tsar, game.cards[player_id], game.black_card, game.choices]
            
            conn.sendall(pickle.dumps(reply))
        except:
            print("Could not execute threaded client !")
            game.connections.pop(player_id)
            game.choices.pop(player_id)
            game.cards.pop(player_id)
            if game.tsar == player_id:
                game.tsar = np.random.choice(np.asarray(list(game.choices.keys())), 1)[0]
            break

    print("Connection Closed")
    conn.close()   
