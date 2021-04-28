import pygame
from cah.framework.network import Network
from cah.framework.player import Player
from cah.framework.canvas import Canvas
from cah.framework.sprite import Button


class Game:

    def __init__(self, width, height):
        self.net = Network()
        self.id = list(self.net.initiate.keys())[0]
        self.canvas = Canvas(width, height, "Cards Against Humanity")
        self.player = Player(list(self.net.initiate.values())[0], self.canvas.screen)
        self.button = Button(self.canvas.width/2, self.canvas.height - 60)
        self.status = None

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
            pygame.display.flip()

            # Check for submissions
            self.submit(event_list)

            # Send Network Stuff
            self.status = self.parse_data(self.send_data())

            # Update Canvas
            self.canvas.draw_background()
            #self.player.draw(self.canvas.get_canvas())
            #self.player2.draw(self.canvas.get_canvas())
            #self.canvas.update()

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

    def send_data(self):
        data = self.player.choice
        # Send the player's to server and retrieve response from the same server
        reply = self.net.send({self.id: data}) if data is not None else self.net.send({self.id: "-1"})
        return reply

    @staticmethod
    def parse_data(data):
        return data
