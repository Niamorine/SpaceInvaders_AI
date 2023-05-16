import pygame
from collide import collide


class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)
        self.rect = self.mask.get_rect()
        self.true_width = self.rect.x
        self.true_height = self.rect.y
        self.true_x = self.x + self.img.get_width()/2
        self.true_y = self.y + self.img.get_height()/2

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))
        # pygame.draw.circle(window, (255, 255, 255), (self.true_x, self.true_y), 2)

    def move(self, vel):
        self.y += vel
        self.true_y += vel

    def off_screen(self, height):
        return not (height >= self.y >= 0)

    def collision(self, obj):
        return collide(self, obj)

    def get_width(self):
        return self.img.get_width()
