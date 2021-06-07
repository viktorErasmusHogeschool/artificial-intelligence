import pandas as pd
import numpy as np
import pickle
from ai_player import AIPlayer
import time

class Game():

    def __init__(self, num_cards):
        self.num_cards = num_cards
        self.connections = {}
        self.choices = {}
        self.round = 1
        self.score = {0: 0}
        self.tsar = 0
        self.checkpoint = True
        self.ai_player = AIPlayer(num_cards)
        self.choices[0] = "-1"
        df = pd.read_json("./cah-cards-full.json").set_index("id")
        #df = pd.read_json("./cah-cards-with-models.json")
        self.white_cards = df.query("cardType == 'A'")
        self.black_cards = df.query("cardType == 'Q'")
        self.black_card = self.pick_card("black")
        self.cards = {0: [self.pick_card("white")[0] for i in range(num_cards)]}
        self.copy_ = None
        self.checkpoints = self.reset_checkpoints()

    def reset_checkpoints(self):
        _ = {}
        for player in list(self.score.keys()):
            _[player] = 0
        return _

    def initialize_cards(self):
        white_sample = self.white_cards.sample(self.num_cards)
        self.white_cards = self.white_cards.drop(white_sample.index)
        return white_sample['text'].values

    def pick_card(self, type_):
        if type_ == "black":
            black_sample = self.black_cards.sample(1)
            self.black_cards = self.black_cards.drop(black_sample.index)
            return black_sample['text'].values
        else:
            white_sample = self.white_cards.sample(1)
            self.white_cards = self.white_cards.drop(white_sample.index)
            return white_sample['text'].values

    def update_choices(self, data):
        id_ = list(data.keys())[0]
        value = list(data.values())[0]
        # If a player submits a choice, update the choices
        if  value != "-1":
            print("Received: {} from Player {}".format(value, id_))
            self.choices[id_] = value

    def players_status(self):
        _ = {}
        # Check how many players have chosen their card
        for k,v in self.choices.items():
            # If player did not play, indicate 0
            if v == "-1":
                _[k] = 0
            # If player played, indicate 1
            else:
                _[k] = 1
        return _

    def parse_cards(self, cards):
        options = []
        if "_" in self.black_card[0]:
            for wc in cards:
                options.append(self.black_card[0].replace("_", wc))
        else:
            for wc in cards:
                options.append(self.black_card[0] + wc)
        return options

    def check_round(self):
        # Make ai_player vote
        if self.tsar !=0 and not self.ai_player.voted:
            self.choices[0] = self.cards[0][self.ai_player.vote(self.parse_cards(self.cards[0]))-1]
            self.ai_player.voted = True
        # Select player choices except tsar
        copy = self.choices.copy()
        copy.pop(self.tsar)
        # If all players voted
        if "-1" not in list(copy.values()):
            # Distinguish human vote from AI vote
            if self.tsar != 0:
                if self.checkpoint:
                    self.copy_ = self.cards[self.tsar]
                    self.checkpoint = False
                self.cards[self.tsar] = list(copy.values())
                winner = self.wait_for_human_vote(copy)
                # If human tsar has made a decision
                if winner is not None:
                    # print("Player {} has won the round !".format(winner))
                    self.cards[self.tsar] = self.copy_
                    # Wait until every player gets the choices
                    if sum(list(self.checkpoints.values())) == len(list(self.score.keys()))-1:
                        self.configure_new_round(winner)

            else:
                print("I am going to decide which human is the most funny !")
                # Make AI player vote
                votes = self.parse_cards(list(copy.values()))
                winner = self.ai_player.vote(votes)
                # Put Tsar's choice in the choices and sent to players
                self.choices[self.tsar] = self.choices[winner]
                print("I found sentence {} the most funny !".format(votes[winner-1]))
                # Wait until every player gets the choices (AI player does not need to be ready)
                if sum(list(self.checkpoints.values())) == len(list(self.score.keys()))-1:
                    self.configure_new_round(winner)

    def wait_for_human_vote(self, copy):
        # Look at the vote from the Tsar
        winner = None
        if self.choices[self.tsar] != "-1":
            # Search to which player the card belongs
            for key in copy.keys():
                if self.choices[self.tsar] in self.cards[key]:
                    winner = key
                    self.checkpoint = True
            if winner is None:
                print("There was an error detecting {} in :".format(self.choices[self.tsar], self.cards))
        return winner

    def configure_new_round(self, winner):
        # Renew black card
        self.black_card = self.pick_card("black")
        # Send new card to players
        for idx in list(self.choices.keys()):
            if idx != self.tsar:
                new_card = self.pick_card("white")[0]
                _ = np.where(np.asarray(self.cards[idx]) == self.choices[idx])[0][0]
                self.cards[idx][_] = new_card
                print("Replacing Card {} for Card {} for Player {}".format(self.choices[idx], new_card, idx))
        # Reinitialize player's choices
        self.choices = {key: "-1" for key in list(self.choices.keys())}
        # Set new tsar player
        self.tsar = winner
        # Update scoring table
        self.score[winner] += 1
        # Reset AI player voting status
        self.ai_player.voted = False
        # Reset checkpoints
        self.checkpoints = self.reset_checkpoints()

    def update_score(self):
        for player_id in list(self.choices.keys()):
            if player_id not in list(self.score.keys()):
                self.score[player_id] = 0
                self.checkpoints[player_id] = 0
        return self.score


