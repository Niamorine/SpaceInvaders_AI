import sys
import os

current = os.path.dirname(os.path.abspath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

import pygame
import neat
import pickle
from game.consts import WIDTH, HEIGHT
from game.game import Game
from game import visualize
from reportlab.graphics import renderPM
from PIL import Image
import numpy as np
import time

debug = False


class GameAi:
    def __init__(self, game, draw):
        self.genome = None
        self.game = game
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
        score = 0
        while run:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit()

            nearest_enemy_y = 0
            nearest_enemy_x = 0
            laser_above = False
            nearest_laser_dist = (WIDTH ** 2 + HEIGHT ** 2) ** 0.5
            nearest_laser_relative_x = WIDTH
            nearest_laser_relative_y = HEIGHT
            if len(self.game.enemies) >= 1:
                nearest_enemy_y = self.game.enemies[0].y + self.game.enemies[0].get_height() / 2
                nearest_enemy_x = self.game.enemies[0].x + self.game.enemies[0].get_width() / 2
            for enemy in self.game.enemies:
                for laser in enemy.lasers:
                    laser_relative_x = laser.true_x - self.game.player.true_x
                    laser_relative_y = laser.true_y - self.game.player.true_y
                    dist = (laser_relative_x ** 2 + laser_relative_y ** 2) ** 0.5
                    if self.game.player.x <= laser.true_x - laser.true_width / 2 and laser.true_x + laser.true_width / 2 <= self.game.player.x + self.game.player.get_width() and self.game.player.y >= laser.true_y:
                        laser_above = True
                    if dist < nearest_laser_dist:
                        nearest_laser_dist = dist
                        nearest_laser_relative_x = laser_relative_x
                        nearest_laser_relative_y = laser_relative_y
            relative_enemy_y = nearest_enemy_y - self.game.player.y
            relative_enemy_x = nearest_enemy_x - self.game.player.x

            # Normalizing inputs
            norm_relative_enemy_x = relative_enemy_x / WIDTH
            norm_relative_enemy_y = relative_enemy_y / HEIGHT
            norm_player_x = self.game.player.x / WIDTH
            norm_player_y = self.game.player.y / HEIGHT
            norm_nearest_laser_dist = nearest_laser_dist / ((WIDTH ** 2 + HEIGHT ** 2) ** 0.5)
            norm_cooldown = self.game.player.cool_down_counter / self.game.player.COOLDOWN
            norm_nearest_laser_relative_x = nearest_laser_relative_x / WIDTH
            norm_nearest_laser_relative_y = nearest_laser_relative_y / HEIGHT

            output = net.activate((norm_cooldown, norm_nearest_laser_relative_x, norm_nearest_laser_relative_y,
                                   norm_relative_enemy_x, norm_relative_enemy_y, laser_above))
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


    def train_ai(self, genome, c):
        run = True
        start_time = time.time()
        net = neat.nn.FeedForwardNetwork.create(genome, c)
        self.genome = genome

        count = 0
        while run:
            if self.draw:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        quit()

            prev_pos = self.game.player.x
            nearest_enemy_y = 0
            nearest_enemy_x = 0
            laser_above = False
            nearest_laser_dist = (WIDTH ** 2 + HEIGHT ** 2) ** 0.5
            nearest_laser_relative_x = WIDTH
            nearest_laser_relative_y = HEIGHT
            if len(self.game.enemies) >= 1:
                nearest_enemy_y = self.game.enemies[0].y + self.game.enemies[0].get_height()/2
                nearest_enemy_x = self.game.enemies[0].x + self.game.enemies[0].get_width()/2
            for enemy in self.game.enemies:
                for laser in enemy.lasers:
                    laser_relative_x = laser.true_x - self.game.player.true_x
                    laser_relative_y = laser.true_y - self.game.player.true_y
                    dist = (laser_relative_x ** 2 + laser_relative_y ** 2) ** 0.5
                    if self.game.player.x <= laser.true_x - laser.true_width/2 and laser.true_x + laser.true_width/2 <= self.game.player.x + self.game.player.get_width() and self.game.player.y >= laser.true_y:
                        laser_above = True
                    if dist < nearest_laser_dist:
                        nearest_laser_dist = dist
                        nearest_laser_relative_x = laser_relative_x
                        nearest_laser_relative_y = laser_relative_y
            relative_enemy_y = nearest_enemy_y - self.game.player.y
            relative_enemy_x = nearest_enemy_x - self.game.player.x

            # Normalizing inputs
            norm_relative_enemy_x = relative_enemy_x/WIDTH
            norm_relative_enemy_y = relative_enemy_y/HEIGHT
            norm_player_x = self.game.player.x/WIDTH
            norm_player_y = self.game.player.y/HEIGHT
            norm_nearest_laser_dist = nearest_laser_dist / ((WIDTH ** 2 + HEIGHT ** 2) ** 0.5)
            norm_cooldown = self.game.player.cool_down_counter / self.game.player.COOLDOWN
            norm_nearest_laser_relative_x = nearest_laser_relative_x / WIDTH
            norm_nearest_laser_relative_y = nearest_laser_relative_y /HEIGHT

            # Activates the neural network and returns the outputs, arguments are the inputs
            # Make sure that the number of inputs and outputs correspond to the config file
            # 6 inputs and 4 outputs (shoot, move left, move right, do nothing) so far
            output = net.activate((norm_cooldown, norm_nearest_laser_relative_x, norm_nearest_laser_relative_y,
                                   norm_relative_enemy_x, norm_relative_enemy_y, laser_above))
            decision = output.index(max(output))  # 0 is shoot, 1 is move left, 2 is move right, 3 is do nothing
            match decision:
                case 0:
                    self.shoot()
                case 1:
                    self.move_left()
                case 2:
                    self.move_right()
                case 3:
                    # penalty for not doing anything
                    genome.fitness -= 0.01

            # bonus for surviving
            genome.fitness += 0.01

            # penalty for being at the same position as before
            if self.game.player.x == prev_pos:
                genome.fitness -= 0.03

            # penalty for being under a laser
            #if laser_above:
             #   genome.fitness -= 2

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
                genome.fitness += 50 * game_info.nb_enemies_killed
                break


def eval_genomes(genomes, c):
    draw = False
    human = False
    fast = False

    for i, (genome_id, genome) in enumerate(genomes):
        genome.fitness = 0
        game = GameAi(Game(WIDTH, HEIGHT, draw, human, fast), draw)

        game.train_ai(genome, c)


def run_neat(c):
    p = neat.Checkpointer.restore_checkpoint("neat-checkpoint-173")
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

    # print(best)
    window = pygame.display.set_mode((WIDTH, HEIGHT))

    game = GameAi(Game(WIDTH, HEIGHT, draw=True, human=False, fast=False), draw=True)
    game.test_ai(best, c)


def vis_net(c):
    with open("best.pickle", "rb") as f:
        best = pickle.load(f)

    names = {-6: "laser_above", -5: "norm_relative_enemy_y", -4: "norm_relative_enemy_x",
             -3: "norm_nearest_laser_relative_y", -2: "norm_nearest_laser_relative_x", -1: "norm_cooldown",
             0: "shoot", 1: "left", 2: "right", 3: "nothing"}
    c.genome_config.input_keys = {-6: "-6", -5: "-5", -4: "-4", -3: "-3", -2: "-2", -1: "-1",
                                       0: "shoot", 1: "left", 2: "right", 3: "nothing"}
    visualize.draw_net(c, best, filename="graph_neural_network_gen_173", view=True, node_names=names)


if __name__ == "__main__":
    pygame.font.init()

    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config.txt")
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet,
                         neat.DefaultStagnation, config_path)

    # run_neat(config)
    test_ai(config)
    # vis_net(config)
