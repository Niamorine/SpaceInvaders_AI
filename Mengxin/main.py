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
import numpy as np

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
        count = 0
        while run:
            count += 1
            if count > 10:
                count = 0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit()

            laser_above = False
            nearest_laser_dist = (WIDTH ** 2 + HEIGHT ** 2) ** 0.5

            for enemy in self.game.enemies:
                for laser in enemy.lasers:
                    laser_relative_x = laser.true_x - self.game.player.true_x
                    laser_relative_y = laser.true_y - self.game.player.true_y
                    dist = (laser_relative_x ** 2 + laser_relative_y ** 2) ** 0.5
                    if self.game.player.x <= laser.true_x - laser.true_width / 2 and laser.true_x + laser.true_width / 2 <= self.game.player.x + self.game.player.get_width() and self.game.player.y >= laser.true_y:
                        laser_above = True
                    if dist < nearest_laser_dist:
                        nearest_laser_dist = dist

            norm_cooldown = self.game.player.cool_down_counter / self.game.player.COOLDOWN

            tab_enemy_lasers = [0 for i in range(0, 24)]
            j = 0
            for enemy in self.game.enemies:
                for laser in enemy.lasers:
                    if laser.true_y > 0 and 0 < laser.true_x < WIDTH and j < 24:
                        case_x = int((laser.true_x - self.game.player.true_x) * 80 / WIDTH)
                        case_y = int(laser.true_y * 80 / HEIGHT)
                        # print(case_x, case_y)
                        tab_enemy_lasers[j] = case_x
                        tab_enemy_lasers[j + 1] = case_y
                        j = j + 2

            tab_player_lasers = [0 for j in range(0, 12)]
            i = 0
            for laser in self.game.player.lasers:
                case_x = int(( laser.true_x - self.game.player.true_x) * 80 / WIDTH)
                case_y = int(laser.true_y * 80 / HEIGHT)
                tab_player_lasers[i] = case_x
                tab_player_lasers[i + 1] = case_y
                i = i + 2

            tab_enemy = [0 for i in range(0, 20)]
            j = 0
            for enemy in self.game.enemies:
                if 0 < enemy.true_y and j < 20:
                    case_x = int((enemy.true_x - self.game.player.true_x) * 80 / WIDTH)
                    case_y = int(enemy.true_y* 80 / HEIGHT)
                    # print(case_x, case_y)
                    tab_enemy[j] = case_x
                    tab_enemy[j + 1] = case_y
                    j = j + 2

            tab_enemy_lasers = np.ndarray.flatten(np.array(tab_enemy_lasers))
            tab_player_lasers = np.ndarray.flatten((np.array(tab_player_lasers)))
            tab_enemy = np.ndarray.flatten(np.array(tab_enemy))

            elts = np.array([norm_cooldown, laser_above])
            array = np.concatenate((tab_player_lasers, tab_enemy_lasers, tab_enemy, elts), None)

            # Activates the neural network and returns the outputs, arguments are the inputs
            # Make sure that the number of inputs and outputs correspond to the config file
            # 448 inputs and 4 outputs (shoot, move left, move right, do nothing) so far
            output = net.activate(array)
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
            laser_above = False

            for enemy in self.game.enemies:
                for laser in enemy.lasers:
                    laser_relative_x = laser.true_x - self.game.player.true_x
                    laser_relative_y = laser.true_y - self.game.player.true_y
                    dist = (laser_relative_x ** 2 + laser_relative_y ** 2) ** 0.5
                    if self.game.player.x <= laser.true_x - laser.true_width / 2 and laser.true_x + laser.true_width / 2 <= self.game.player.x + self.game.player.get_width() and self.game.player.y >= laser.true_y:
                        laser_above = True

            # Normalizing inputs
            norm_cooldown = self.game.player.cool_down_counter / self.game.player.COOLDOWN

            tab_enemy_lasers = [0 for i in range(0, 24)]
            j = 0
            for enemy in self.game.enemies:
                for laser in enemy.lasers:
                    if laser.true_y > 0 and 0 < laser.true_x < WIDTH and j < 24:
                        case_x = int((laser.true_x - self.game.player.true_x) * 80 / WIDTH)
                        case_y = int(laser.true_y * 80 / HEIGHT)
                        # print(case_x, case_y)
                        tab_enemy_lasers[j] = case_x
                        tab_enemy_lasers[j + 1] = case_y
                        j = j + 2

            tab_player_lasers = [0 for j in range(0, 12)]
            i = 0
            for laser in self.game.player.lasers:
                case_x = int(( laser.true_x - self.game.player.true_x) * 80 / WIDTH)
                case_y = int(laser.true_y * 80 / HEIGHT)
                tab_player_lasers[i] = case_x
                tab_player_lasers[i + 1] = case_y
                i = i + 2

            tab_enemy = [0 for i in range(0, 20)]
            j = 0
            for enemy in self.game.enemies:
                if 0 < enemy.true_y and j < 20:
                    case_x = int((enemy.true_x - self.game.player.true_x) * 80 / WIDTH)
                    case_y = int(enemy.true_y* 80 / HEIGHT)
                    # print(case_x, case_y)
                    tab_enemy[j] = case_x
                    tab_enemy[j + 1] = case_y
                    j = j + 2

            i = 0
            while i < 20:
                if tab_enemy[i+1] > 0:
                    j = tab_enemy[i]
                    exist = 0
                    x = 0
                    while (x < 10) & (exist == 0):
                        if j - 3 < tab_player_lasers[x] < 3 + j:
                            exist = 1
                        x = x + 2
                    if exist == 0:
                        genome.fitness -= 0.03
                    if tab_enemy[i + 1] > 64:
                        genome.fitness -= 0.1
                i = i + 2

            i = 0
            while i < 24:
                if tab_enemy_lasers[i + 1] > 70:
                    if 3 > tab_enemy_lasers[i] > -3:
                        genome.fitness -= 0.5
                i = i + 2

            tab_enemy_lasers = np.ndarray.flatten(np.array(tab_enemy_lasers))
            tab_player_lasers = np.ndarray.flatten((np.array(tab_player_lasers)))
            tab_enemy = np.ndarray.flatten(np.array(tab_enemy))

            elts = np.array([norm_cooldown, laser_above])
            array = np.concatenate((tab_player_lasers, tab_enemy_lasers, tab_enemy, elts), None)

            # Activates the neural network and returns the outputs, arguments are the inputs
            # Make sure that the number of inputs and outputs correspond to the config file
            # 448 inputs and 4 outputs (shoot, move left, move right, do nothing) so far
            output = net.activate(array)
            decision = output.index(max(output))  # 0 is shoot, 1 is move left, 2 is move right, 3 is do nothing
            match decision:
                case 0:
                    self.shoot()
                    genome.fitness += 0.01
                case 1:
                    self.move_left()
                case 2:
                    self.move_right()
                case 3:
                    # penalty for not doing anything
                    # genome.fitness -= 0.1
                    pass

            # penalty for being at the same position as before
            if self.game.player.x == prev_pos:
                genome.fitness -= 0.03

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
    nb_game = 3

    for i, (genome_id, genome) in enumerate(genomes):
        genome.fitness = 0
        for i in range(nb_game):
            game = GameAi(Game(WIDTH, HEIGHT, draw, human, fast), draw)
            game.train_ai(genome, c)



def parallelEval(genome, c):
    draw = False
    human = False
    fast = False
    nb_game = 3
    genome.fitness = 0
    pygame.font.init()

    for i in range(nb_game):
        game = GameAi(Game(WIDTH, HEIGHT, draw, human, fast), draw)
        game.train_ai(genome, c)

    return genome.fitness


def run_neat(c):
    p = neat.Checkpointer.restore_checkpoint("neat-checkpoint-213")
    #p = neat.Population(c)
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    p.add_reporter(neat.Checkpointer(1))
    pe = neat.ParallelEvaluator(10, parallelEval)

    best = None
    # best = p.run(eval_genomes, 100)
    best = p.run(pe.evaluate, 100)

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


if __name__ == "__main__":
    pygame.font.init()

    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config.txt")
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet,
                         neat.DefaultStagnation, config_path)

    # run_neat(config)
    test_ai(config)
