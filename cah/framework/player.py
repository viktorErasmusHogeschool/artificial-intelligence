import pygame
import numpy as np
from cah.framework.sprite import Card


class Player:

    def __init__(self, initial_sample, window):
        self.number_of_cards = initial_sample.size
        self.group = self.create_group(initial_sample, window)
        self.choice = " "

    def create_group(self, initial_sample, window):
        _ = [Card((n + 1) * window.get_width() // (int(np.floor(self.number_of_cards/2)) + 1),
                 800 - 500, " ", (128, 128, 128)) for n in range(int(np.floor(self.number_of_cards/2)))]
        __ = [Card((n + 1) * window.get_width() // (int(np.ceil(self.number_of_cards/2)) + 1),
                 800 - 250, " ", (128, 128, 128)) for n in range(int(np.ceil(self.number_of_cards/2)))]
        group = pygame.sprite.Group(_ + __)
        group.sprites()[0].clicked = True
        card_index = 0
        for card in group:
            card.render_text(initial_sample[card_index])
            card_index += 1
        return group

    def choose(self):
        for card in self.group:
            if card.clicked:
                self.choice = card.text