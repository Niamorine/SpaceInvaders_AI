from Ship import Ship
from Laser import Laser
from consts import GREEN_SPACE_SHIP, RED_LASER, RED_SPACE_SHIP, GREEN_LASER, BLUE_LASER, BLUE_SPACE_SHIP
import pygame


class Enemy(Ship):
    COLOR_MAP = {
        "red": (RED_SPACE_SHIP, RED_LASER),
        "green": (GREEN_SPACE_SHIP, GREEN_LASER),
        "blue": (BLUE_SPACE_SHIP, BLUE_LASER)
    }

    def __init__(self, x, y, color="red", health=100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.true_x = self.x + self.ship_img.get_width()/2
        self.true_y = self.y + self.ship_img.get_height()/2

    def move(self, vel):
        self.y += vel
        self.true_y += vel

    def draw(self, window):
        super().draw(window)
        # pygame.draw.circle(window, (255, 255, 255), (self.true_x, self.true_y), 5)

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x - 20, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1
