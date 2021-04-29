import pygame
from cah.framework.network import Network
from cah.framework.player import Player
from cah.framework.canvas import Canvas
from cah.framework.sprite import Button
from _thread import *


class Game:

    def __init__(self, width, height):
        self.font = pygame.font.SysFont('Arial', 25)
        self.net = Network()
        self.id = list(self.net.initiate.keys())[0]
        self.canvas = Canvas(width, height, "Cards Against Humanity")
        white_cards, black_card = self.net.initiate[self.id][0], self.net.initiate[self.id][1]
        self.player = Player(white_cards, black_card, self.canvas.screen)
        self.button = Button(self.canvas.width/2, self.canvas.height - 60)
        self.score = {}
        self.rounds = 1
        self.players_status = {}

    def run(self):

        print("You are Player {}! Best of luck!!".format(self.id))
        clock = pygame.time.Clock()
        all_sprites = self.player.group.copy()
        all_sprites.add(self.button)
        run = True

        while run:

            clock.tick(60)
            event_list = pygame.event.get()

            for event in event_list:
                if event.type == pygame.QUIT:
                    run = False

            # Check for clicks
            self.update(event_list)
            all_sprites.draw(self.canvas.screen)

            # Check for submissions
            self.submit(event_list)

            # Send & Receive data from server
            self.players_status, self.score, tsar, black_card = self.parse_data(self.send_data())

            # Set the Tsar player
            if self.id == tsar:
                self.player.tsar = True
            else:
                self.player.tsar = False

            # Check the beginning of a new round
            if sum(list(self.score.values())) == self.rounds:
                self.rounds += 1
                print("We're moving towards round {} with Player {} as new tsar !".format(self.rounds, tsar))
                # Unlock player in beginning of new round, but be careful to reset its choice to None after sending
                self.player.locked = False

            # Update game's black card
            self.player.redraw_card(-1, black_card[0])

            # Draw current scoring
            self.print_scoring()
            pygame.display.flip()

            # Update Canvas
            self.canvas.draw_background()

        pygame.quit()
        exit()

    def update(self, event_list):
        # Check if the card was clicked
        for card in self.player.group:
            card.update(event_list)
            # Draw green rectangle around clicked card and
            # Force all other cards to be not selected
            if card.clicked:
                card.image = card.click_image
                for c in self.player.group:
                    c.clicked = False if c != card else True
            # If not selected, do nothing
            else:
                card.image = card.original_image

    def submit(self, event_list):
        for event in event_list:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.button.rect.collidepoint(event.pos):
                    # Set the player's choice
                    self.player.choose()
                    # Send & Receive data from server
                    self.status = self.parse_data(self.send_data())
                    # Once submitted, lock player
                    self.player.locked = True

    def print_scoring(self):
        margin = 50
        delta = (self.canvas.screen.get_width() - margin) / (len(self.players_status) + 1)
        idx = 1
        for player in list(self.players_status.keys()):
            _ = "Waiting" if self.players_status[player] == 0 else "Locked!"
            self.canvas.screen.blit(self.font.render("Player {}".format(player), True, (0, 0, 0)), (delta * idx, 30))
            self.canvas.screen.blit(self.font.render(_, True, (0, 0, 0)), (delta * idx, 80))
            self.canvas.screen.blit(self.font.render(str(self.score[player]), True, (0, 0, 0)), (delta * idx + 40, 130))
            idx += 1

    def send_data(self):
        # Retrieve player's choice
        data = self.player.choice
        # Send the player's choice to server if he/she/it has not yet played, otherwise send -1
        if data is not None and not self.player.locked and not self.player.tsar:
            # Send player's choice
            self.player.choice = None
            return self.net.send({self.id: data})
        else:
            return self.net.send({self.id: "-1"})

    def parse_data(self, data):
        #Status Score Tsar Black_Card
        return data[0], data[1], data[2], data[3]
