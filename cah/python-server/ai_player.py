import pandas as pd
import numpy as np
from bert_api import colbert


class AIPlayer():

    def __init__(self, num_cards):
        self.num_cards = num_cards
        self.voted = False
        
    def vote(self, votes):
        results = np.asarray([colbert(v).predict() for v in votes])
        print("Choosing {} as funniest statement :)".format(votes[np.argmax(results)]))
        return np.argmax(results) + 1
