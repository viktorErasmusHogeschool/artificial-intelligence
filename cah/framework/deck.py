import pandas as pd


class Deck:

    def __init__(self):
        self.deck = pd.read_json("./cah-cards-full.json").set_index("id")