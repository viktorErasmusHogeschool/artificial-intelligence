import pygame
import numpy as np
from . import Network
from . import Player
from . import Canvas
from . import Button
from _thread import *
import sys
sys.path.append("../")
from speech.speech_synthesis import say
from gans.image_synthesis import gen_image


class Game:

    def __init__(self, width, height):
        self.font = pygame.font.SysFont('Arial', 25)
        self.net = Network()
        self.id = list(self.net.initiate.keys())[0]
        self.canvas = Canvas(width, height, "Player {}".format(self.id))
        self.white_cards, self.black_card = np.asarray(self.net.initiate[self.id][0]), self.net.initiate[self.id][1]
        self.player = Player(self.white_cards, self.black_card, self.canvas.screen)
        self.button = Button(self.canvas.width/2, self.canvas.height - 60)
        self.all_sprites = None
        self.score = {0: 0}
        self.tsar = 0
        self.black_card = None
        self.rounds = 1
        self.players_status = {}
        self.voted = False
        self.resume = False
        self.choices = None
        self.image = None

    def run(self):

        print("You are Player {}! Best of luck!!".format(self.id))
        clock = pygame.time.Clock()
        # Initialize card deck
        self.all_sprites = self.player.group.copy()
        self.all_sprites.add(self.button)
        run = True

        while run:

            clock.tick(60)
            event_list = pygame.event.get()

            for event in event_list:
                if event.type == pygame.QUIT:
                    run = False

            # Check for clicks
            self.update(event_list)
            _ = list(self.players_status.values())
            self.all_sprites.draw(self.canvas.screen)

            # Check for submissions
            self.submit(event_list)

            choices, bc = self.choices, self.black_card

            # Send & Receive data from server
            self.parse_data(self.send_data())

            # Set the Tsar player
            if self.id == self.tsar:
                self.player.tsar = True
            else:
                self.player.tsar = False

            # Check the beginning of a new round
            if sum(list(self.score.values())) == self.rounds:
                # Announce end of round
                say("Attention please, here is the winning sentence by player {}".format(self.tsar))
                # Update round number
                self.rounds += 1
                # Fetch winning phrase
                win = self.winning_phrase(choices, bc[0])
                # Say winning phrase out loud
                say(win)
                # Check if their is a GAN associated to the winning phrase
                gen_image(choices[self.tsar])
                try:
                    image = pygame.image.load(r'gan.jpg')
                    image = pygame.transform.scale(image, (180, 180))
                    self.image = image
                except:
                    print("Could not load image !")
                # Print winning phrase in terminal and unlock player
                say("We're now moving towards round {} with Player {} as new tsar !".format(self.rounds, self.tsar))
                # Unlock player in beginning of new round, but be careful to reset its choice to None after sending
                self.player.locked = False

            # Draw current scoring
            self.print_scoring()
            pygame.display.flip()

            # Update Canvas
            self.canvas.draw_background()

        pygame.quit()
        exit()

    def winning_phrase(self, choices, black_card):
        if "_" in black_card:
            win = black_card.replace('_', choices[self.tsar])
        else:
            win = black_card + choices[self.tsar]
        print("The winning phrase is: {}".format(win))
        return win

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
                    self.parse_data(self.send_data())
                    # Once submitted, lock player
                    self.player.locked = True

    def print_scoring(self):
        margin = 50
        delta = (self.canvas.screen.get_width() - margin) / (len(self.players_status) + 1)
        idx = 1
        # Print header of screen
        for player in list(self.players_status.keys()):
            _ = "Waiting" if self.players_status[player] == 0 else "Locked!"
            if player == self.tsar:
                _ = "Tsar"
            self.canvas.screen.blit(self.font.render("Player {}".format(player), True, (0, 0, 0)), (delta * idx, 10))
            self.canvas.screen.blit(self.font.render(_, True, (0, 0, 0)), (delta * idx, 50))
            self.canvas.screen.blit(self.font.render(str(self.score[player]), True, (0, 0, 0)), (delta * idx + 40, 90))
            idx += 1
            # Display picture as of 2nd round
            if self.rounds >= 2:
                try:
                    self.canvas.screen.blit(self.image, (650, 120))
                except:
                    print("Could not display image !")

    def send_data(self):
        # Retrieve player's choice
        data = self.player.choice
        _ = list(self.players_status.values())
        # Send the player's choice to server if he/she/it has not yet played, otherwise send -1
        if data is not None and not self.player.locked and not self.player.tsar:
            print("Sending {}".format(data))
            self.player.choice = None
            return self.net.send({self.id: data})
        elif self.voted and data is not None:
            self.player.choice = None
            self.resume = True
            return self.net.send({self.id: data})
        else:
            return self.net.send({self.id: "-1"})

    def parse_data(self, data):
        if len(data) == 6:
            # Status Score Tsar Black_Card
            self.players_status, self.score, self.tsar, self.white_cards, self.black_card, self.choices = data[0], data[1], data[2], data[3], data[4], data[5]

            # If player is tsar
            if len(self.white_cards) == len(list(self.players_status.values())) - 1:
                if not self.voted:
                    print("Received the following votes:", self.white_cards)
                    self.player.group = Player.create_group(np.asarray(self.white_cards), self.black_card, self.canvas.screen)
                    self.all_sprites = self.player.group.copy()
                    self.all_sprites.add(self.button)
                    self.voted = True
                    self.player.choice = None
            else:
                self.voted = False
                if self.resume:
                    print("Resuming the game after vote")
                    self.player.group = Player.create_group(np.asarray(self.white_cards), self.black_card, self.canvas.screen)
                    self.all_sprites = self.player.group.copy()
                    self.all_sprites.add(self.button)
                    self.resume = False
                    self.player.choice = None
                # Redraw white cards
                for i in range(len(self.white_cards)):
                    self.player.redraw_card(i, self.white_cards[i], "white")
            # Update game's black card
            self.player.redraw_card(-1, self.black_card[0], "black")
