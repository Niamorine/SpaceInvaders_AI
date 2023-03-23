from Ship import Ship
from consts import YELLOW_LASER, YELLOW_SPACE_SHIP, HEIGHT
import pygame


class Player(Ship):
    def __init__(self, x, y, health=1):
        super().__init__(x, y, health)
        self.vel = 5
        self.ship_img = YELLOW_SPACE_SHIP
        self.laser_img = YELLOW_LASER
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health
        self.true_x = self.x + self.ship_img.get_width()/2
        self.true_y = self.y + self.ship_img.get_height()/2
        self.nb_enemies_killed = 0

    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        objs.remove(obj)
                        if laser in self.lasers:
                            self.lasers.remove(laser)
                        self.nb_enemies_killed += 1

    def move_left(self):
        self.x -= self.vel
        self.true_x -= self.vel

    def move_right(self):
        self.x += self.vel
        self.true_x += self.vel

    def move_up(self):
        self.y -= self.vel
        self.true_y -= self.vel

    def move_down(self):
        self.y += self.vel
        self.true_y += self.vel

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)
        # pygame.draw.circle(window, (255, 255, 255), (self.true_x, self.true_y), 5)

    def healthbar(self, window):
        pygame.draw.rect(window, (255, 0, 0),
                         (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, (0, 255, 0), (
            self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width()
            * (self.health / self.max_health),
            10))
