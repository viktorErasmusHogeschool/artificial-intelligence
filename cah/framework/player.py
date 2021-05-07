import pygame
import numpy as np
from cah.framework.sprite import Card


class Player:

    def __init__(self, white_cards, black_card, window):
        self.number_of_cards = white_cards.size
        self.group = Player.create_group(white_cards, black_card, window)
        self.choice = None
        self.locked = False
        self.tsar = False
        self.voting = False

    @staticmethod
    def create_group(white_cards, black_card, window):
        number_of_cards = white_cards.size
        _ = [Card((n + 1) * window.get_width() // (int(np.floor(number_of_cards/2)) + 1),
                 window.get_height()/2, " ", (220, 220, 220), False) for n in range(int(np.floor(number_of_cards/2)))]
        __ = [Card((n + 1) * window.get_width() // (int(np.ceil(number_of_cards/2)) + 1),
                 window.get_height()/2 + 200, " ", (220, 220, 220), False) for n in range(int(np.ceil(number_of_cards/2)))]
        black_card_ = Card(1/2 * window.get_width(), 1/3 * window.get_height() - 50, black_card[0], (0, 0, 0), True)
        black_card_.render_text()
        group = pygame.sprite.Group(_ + __)
        group.sprites()[0].clicked = True
        card_index = 0
        for card in group:
            card.text = white_cards[card_index]
            card.render_text()
            card_index += 1
        group.add(black_card_)
        return group

    def choose(self):
        for card in self.group:
            if card.clicked:
                self.choice = card.text

    def redraw_card(self, card_id, text, type_):
        card = self.group.sprites()[card_id]
        card.text = text
        if type_ == "black":
            pygame.draw.rect(card.original_image, (0, 0, 0), pygame.Rect(0, 0, 200, 150))
        else:
            pygame.draw.rect(card.click_image, (220, 220, 220), pygame.Rect(0, 0, 200, 150))
            pygame.draw.rect(card.click_image, (0, 128, 0), pygame.Rect(0, 0, 200, 150), 10)
            pygame.draw.rect(card.original_image, (220, 220, 220), pygame.Rect(0, 0, 200, 150))
            card.image = card.original_image
        card.render_text()
