import pygame
pygame.font.init()

FONT = pygame.font.SysFont('Arial', 20)
FONT_COLOR = pygame.Color('black')


class Card(pygame.sprite.Sprite):
    def __init__(self, x, y, text, color):
        super().__init__()
        # Surface of un-clicked object
        self.original_image = pygame.Surface((200, 200), pygame.SRCALPHA)
        pygame.draw.rect(self.original_image, color, pygame.Rect(0, 0, 200, 200))
        # Surface of clicked object
        self.click_image = pygame.Surface((200, 200), pygame.SRCALPHA)
        pygame.draw.rect(self.click_image, color, pygame.Rect(0, 0, 200, 200))
        pygame.draw.rect(self.click_image, (0, 128, 0), pygame.Rect(0, 0, 200, 200), 10)
        # Define text
        self.image = self.original_image
        self.render_text(text)
        # Set additional attributes
        self.rect = self.image.get_rect(center=(x, y))
        self.clicked = False

    def update(self, event_list):
        for event in event_list:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.rect.collidepoint(event.pos):
                    self.clicked = not self.clicked

    @staticmethod
    def blit_text(surface, text, pos, font, color=pygame.Color('black')):
        words = [word.split(' ') for word in text.splitlines()]  # 2D array where each row is a list of words.
        space = font.size(' ')[0]  # The width of a space.
        max_width, max_height = surface.get_size()
        x, y = pos
        for line in words:
            for word in line:
                word_surface = font.render(word, 0, color)
                word_width, word_height = word_surface.get_size()
                if x + word_width >= max_width:
                    x = pos[0]  # Reset the x.
                    y += word_height  # Start on new row.
                surface.blit(word_surface, (x, y))
                x += word_width + space
            x = pos[0]  # Reset the x.
            y += word_height  # Start on new row.

    def render_text(self, text):
        Card.blit_text(self.image, text, (self.image.get_rect().left + 10, self.image.get_rect().top + 10), FONT)
        Card.blit_text(self.click_image, text, (self.image.get_rect().left + 10, self.image.get_rect().top + 10), FONT)


class Button(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        # Surface of object
        self.image = pygame.Surface((100, 50), pygame.SRCALPHA)
        pygame.draw.rect(self.image, (0, 128, 0), pygame.Rect(0, 0, 100, 50))
        # Define text surface
        text_surface = FONT.render("Submit", True, FONT_COLOR)
        text_rect = text_surface.get_rect(center=self.image.get_rect().center)
        # Render text
        self.image.blit(text_surface, text_rect)
        # Set additional attributes
        self.rect = self.image.get_rect(center=(x, y))
        self.clicked = False
