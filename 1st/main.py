import sys
import os

current = os.path.dirname(os.path.abspath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

import time
import pygame
import neat
import pickle
from game.consts import WIDTH, HEIGHT
from game.game import Game

debug = False


class GameAi:
    def __init__(self, game, window, draw):
        self.genome = None
        self.game = game
        self.window = window
        self.draw = draw

    def move_left(self):
        if self.game.player.x - self.game.player_vel > 0:
            self.game.player.move_left()

    def move_right(self):
        if self.game.player.x + self.game.player_vel + self.game.player.get_width() < WIDTH:
            self.game.player.move_right()

    def shoot(self):
        self.game.player.shoot()

    def test_ai(self, genome, c):
        net = neat.nn.FeedForwardNetwork.create(genome, c)

        run = True
        while run:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit()

            nearest_enemy_y = 1000000
            nearest_enemy_x = 0
            laser_above = False
            nearest_laser_dist = 1000000
            if len(self.game.enemies) >= 1:
                nearest_enemy_y = self.game.enemies[0].y + self.game.enemies[0].get_height() / 2
                nearest_enemy_x = self.game.enemies[0].x + self.game.enemies[0].get_width() / 2
            for enemy in self.game.enemies:
                for laser in enemy.lasers:
                    dist = ((laser.true_x - self.game.player.true_x) ** 2 + (
                                laser.true_y - self.game.player.true_y) ** 2) ** 0.5
                    if self.game.player.x <= laser.true_x - laser.true_width / 2 and laser.true_x + laser.true_width / 2 <= self.game.player.x + self.game.player.get_width() and self.game.player.y >= laser.true_y:
                        laser_above = True
                    if dist < nearest_laser_dist:
                        nearest_laser_dist = dist

            output = net.activate((self.game.player.x, self.game.player.y, self.game.player.cool_down_counter,
                                   nearest_enemy_x, nearest_enemy_y, laser_above, nearest_laser_dist))
            decision = output.index(max(output))  # 0 is shoot, 1 is move left, 2 is move right, 3 is do nothing
            match decision:
                case 0:
                    self.shoot()
                case 1:
                    self.move_left()
                case 2:
                    self.move_right()
                case 3:
                    pass

            self.game.loop()


    def calculate_fitness(self, genome, game_info):
        genome.fitness += game_info.nb_enemies_killed

    def train_ai(self, genome, c):
        run = True
        start_time = time.time()
        net = neat.nn.FeedForwardNetwork.create(genome, c)
        self.genome = genome

        count = 0
        while run:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit()

            nearest_enemy_y = 1000000
            nearest_enemy_x = 0
            laser_above = False
            nearest_laser_dist = 1000000
            if len(self.game.enemies) >= 1:
                nearest_enemy_y = self.game.enemies[0].y + self.game.enemies[0].get_height()/2
                nearest_enemy_x = self.game.enemies[0].x + self.game.enemies[0].get_width()/2
            for enemy in self.game.enemies:
                for laser in enemy.lasers:
                    dist = ((laser.true_x - self.game.player.true_x)**2 + (laser.true_y - self.game.player.true_y)**2)**0.5
                    if self.game.player.x <= laser.true_x - laser.true_width/2 and laser.true_x + laser.true_width/2 <= self.game.player.x + self.game.player.get_width() and self.game.player.y >= laser.true_y:
                        laser_above = True
                    if dist < nearest_laser_dist:
                        nearest_laser_dist = dist

            # Activates the neural network and returns the outputs, arguments are the inputs
            # Make sure that the number of inputs and outputs correspond to the config file
            # 7 inputs and 4 outputs (shoot, move left, move right, do nothing) so far
            output = net.activate((self.game.player.x, self.game.player.y, self.game.player.cool_down_counter,
                                   nearest_enemy_x, nearest_enemy_y, laser_above, nearest_laser_dist))
            decision = output.index(max(output))  # 0 is shoot, 1 is move left, 2 is move right, 3 is do nothing
            match decision:
                case 0:
                    self.shoot()
                case 1:
                    self.move_left()
                case 2:
                    self.move_right()
                case 3:
                    genome.fitness -= 0.001

            if debug:
                count += 1
                nb_laser = 0
                if count == 20:
                    for enemy in self.game.enemies:
                        nb_laser += len(enemy.lasers)
                    # print(f"nb_laser: {nb_laser}, laser above : {laser_above}, distance laser-player: {nearest_laser_dist}")
                    print(output)
                    count = 0

            game_info = self.game.loop()

            if game_info.lost:
                self.calculate_fitness(genome, game_info)
                break


def eval_genomes(genomes, c):
    window = pygame.display.set_mode((WIDTH, HEIGHT))
    draw = False
    human = False
    fast = False

    for i, (genome_id, genome) in enumerate(genomes):
        genome.fitness = 0
        game = GameAi(Game(WIDTH, HEIGHT, draw, human, fast), window, draw)

        game.train_ai(genome, c)


def run_neat(c):
    p = neat.Checkpointer.restore_checkpoint("neat-checkpoint-1702")
    # p = neat.Population(c)
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    p.add_reporter(neat.Checkpointer(1))

    best = p.run(eval_genomes, 1)

    with open("best.pickle", "wb") as f:
        pickle.dump(best, f)
        print("best saved")


def test_ai(c):
    with open("best.pickle", "rb") as f:
        best = pickle.load(f)

    window = pygame.display.set_mode((WIDTH, HEIGHT))

    game = GameAi(Game(WIDTH, HEIGHT, draw=True, human=False, fast=False), window, draw=True)
    game.test_ai(best, c)


if __name__ == "__main__":
    pygame.font.init()

    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config.txt")
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet,
                         neat.DefaultStagnation, config_path)

    # run_neat(config)
    test_ai(config)