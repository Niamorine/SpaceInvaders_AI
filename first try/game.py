from Enemy import Enemy
from Player import Player
import random
from collide import collide
from consts import *


class GameInformation:
    def __init__(self, lost, nb_enemies_killed):
        self.lost = lost
        self.nb_enemies_killed = nb_enemies_killed


class Game:
    def __init__(self, window, width, height, draw, human, fast):
        self.fast = fast
        self.human = human
        self.draw = draw
        self.width = width
        self.height = height
        self.window = window
        self.run = True
        self.FPS = 60
        self.clock = pygame.time.Clock()
        self.level = 0
        self.lives = 5
        self.main_font = pygame.font.SysFont("comicsans", 50)
        self.lost_font = pygame.font.SysFont("comicsans", 60)

        self.enemies = []
        self.wave_lenght = 0
        self.enemy_vel = 1

        self.player_vel = 5
        self.laser_vel = 6

        self.player = Player(300, 650)

        self.lost = False
        self.lost_count = 0

    def redraw_window(self):
        self.window.blit(BG, (0, 0))
        lives_label = self.main_font.render(f"lives: {self.lives}", True, (255, 255, 255))
        level_label = self.main_font.render(f"level: {self.level}", True, (255, 255, 255))

        self.window.blit(lives_label, (10, 10))
        self.window.blit(level_label, (WIDTH - level_label.get_width() - 10, 10,))

        for an_enemy in self.enemies:
            an_enemy.draw(self.window)

        self.player.draw(self.window)

        if self.lost:
            lost_label = self.lost_font.render("You lost !!", True, (255, 255, 255))
            self.window.blit(lost_label, (WIDTH / 2 - lost_label.get_width() / 2, 350))
        pygame.display.update()

    def loop(self):
        if self.draw:
            if not self.fast:
                self.clock.tick(self.FPS)
            self.redraw_window()

        if self.lives <= 0 or self.player.health <= 0:
            self.lost = True
            self.lost_count += 1

        if self.lost:
            if self.lost_count > self.FPS * 3:
                self.run = False

        if len(self.enemies) == 0:
            self.level += 1
            self.wave_lenght += 5
            for i in range(self.wave_lenght):
                enemy = Enemy(random.randrange(50, WIDTH - 100), random.randrange(-1500, -100),
                              random.choice(["red", "blue", "green"]))
                self.enemies.append(enemy)
            # Sort enemies by their y value, reversed order (max y ends up first)
            self.enemies.sort(key=lambda e: e.y, reverse=True)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

        if self.human:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_q] and self.player.x - self.player_vel > 0:  # left
                self.player.move_left()
            if keys[pygame.K_d] and self.player.x + self.player_vel + self.player.get_width() < WIDTH:  # right
                self.player.move_right()
            if keys[pygame.K_z] and self.player.y - self.player_vel > 0:  # up
                self.player.move_up()
            if keys[pygame.K_s] and self.player.y + self.player_vel + self.player.get_height() + 15 < HEIGHT:  # down
                self.player.move_down()
            if keys[pygame.K_SPACE]:
                self.player.shoot()

        for enemy in self.enemies:
            enemy.move(self.enemy_vel)
            enemy.move_lasers(self.laser_vel, self.player)

            if random.randrange(0, 120) == 1:
                enemy.shoot()

            if collide(enemy, self.player):
                self.player.health -= 10
                self.enemies.remove(enemy)
            elif enemy.y + enemy.get_height() > HEIGHT:
                self.lives -= 1
                self.enemies.remove(enemy)

        self.player.move_lasers(-self.laser_vel, self.enemies)

        return GameInformation(self.lost, self.player.nb_enemies_killed)


if __name__ == "__main__":
    pygame.font.init()

    WIN = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Space Shooter Tutorial")
    game = Game(WIN, WIDTH, HEIGHT, True, True, False)
    while game.run:
        game.loop()