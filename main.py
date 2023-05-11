import time
import pygame
import neat
import os
import pickle

from parallele_et_matrices.main import vis_net
from consts import WIDTH, HEIGHT
from game import Game
import visualize
# from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM
from PIL import Image
import numpy as np

debug = False


# def svg2png():
# drawing = svg2rlg('graph_best_so_far.svg')
# renderPM.drawToFile(drawing, 'graph_best_so_far.png', fmt='PNG')
# im = Image.open('graph_best_so_far.png')
# im.show()


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

            norm_cooldown = self.game.player.cool_down_counter / self.game.player.COOLDOWN

            tab_enemy_lasers = [0 for i in range(0, 30)]
            j = 0
            for enemy in self.game.enemies:
                for laser in enemy.lasers:
                    if laser.true_y > 0 and 0 < laser.true_x < WIDTH:
                        case_x = int(laser.true_x * 40 / WIDTH)
                        case_y = int(laser.true_y * 11 / HEIGHT)
                        # print(case_x, case_y)
                        tab_enemy_lasers[j] = case_x
                        tab_enemy_lasers[j + 1] = case_y
                        j = j + 2
                        # tab_enemy_lasers[case_x][case_y - 1] = 1
                        # tab_enemy_lasers[case_x][case_y + 1] = 1

            tab_player_lasers = [0 for j in range(1, 41)]
            for laser in self.game.player.lasers:
                laser_matrice_x = laser.true_x
                laser_matrice_y = laser.true_y
                case_x = int(laser.true_x * 40 / WIDTH)
                tab_player_lasers[case_x] += 1

            tab_enemy = [-1 for i in range(0, 20)]
            j = 0;
            for enemy in self.game.enemies:
                if 0 < enemy.true_y:
                    case_x = int(enemy.true_x * 40 / WIDTH)
                    case_y = int(enemy.true_y * 5 / HEIGHT)
                    # print(case_x, case_y)
                    if j < 20:
                        tab_enemy[j] = case_x
                        tab_enemy[j + 1] = case_y
                        j = j + 2

            tab_player = [0 for j in range(0, 1)]
            case_player = int(self.game.player.true_x * 40 / WIDTH) - 1
            tab_player[0] = case_player

            tab_enemy_lasers = np.ndarray.flatten(np.array(tab_enemy_lasers))
            tab_player_lasers = np.ndarray.flatten((np.array(tab_player_lasers)))
            tab_enemy = np.ndarray.flatten(np.array(tab_enemy))
            tab_player = np.ndarray.flatten(np.array(tab_player))

            elts = np.array([norm_cooldown, laser_above])
            array = np.concatenate((tab_player_lasers, tab_enemy_lasers, tab_enemy, tab_player, elts), None)

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

            # Normalizing inputs
            norm_cooldown = self.game.player.cool_down_counter / self.game.player.COOLDOWN

            tab_enemy_lasers = [0 for i in range(0, 30)]
            j = 0
            for enemy in self.game.enemies:
                for laser in enemy.lasers:
                    if laser.true_y > 0 and 0 < laser.true_x < WIDTH:
                        case_x = int(laser.true_x * 40 / WIDTH)
                        case_y = int(laser.true_y * 11 / HEIGHT)
                        # print(case_x, case_y)
                        tab_enemy_lasers[j] = case_x
                        tab_enemy_lasers[j + 1] = case_y
                        j = j + 2
                        # tab_enemy_lasers[case_x][case_y - 1] = 1
                        # tab_enemy_lasers[case_x][case_y + 1] = 1

            tab_player_lasers = [0 for j in range(1, 41)]
            for laser in self.game.player.lasers:
                laser_matrice_x = laser.true_x
                laser_matrice_y = laser.true_y
                case_x = int(laser.true_x * 40 / WIDTH)
                tab_player_lasers[case_x] += 1

            tab_enemy = [-1 for i in range(0, 20)]
            j = 0;
            for enemy in self.game.enemies:
                matrice_x = enemy.true_x
                matrice_y = enemy.true_y
                if 0 < enemy.true_y:
                    case_x = int(enemy.true_x * 40 / WIDTH)
                    case_y = int(enemy.true_y * 5 / HEIGHT)
                    # print(case_x, case_y)
                    if (j < 20):
                        tab_enemy[j] = case_x
                        tab_enemy[j + 1] = case_y
                        j = j + 2

            i = 0
            while i < 20:
                if tab_enemy[i] != -1:
                    j = tab_enemy[i]
                    if tab_player_lasers[j] == 0:
                        genome.fitness -= 0.02
                    elif tab_enemy[i + 1] == 4:
                        genome.fitness -= 0.1
                i = i + 2

            tab_player = [0 for j in range(0, 1)]
            case_player = int(self.game.player.true_x * 40 / WIDTH) - 1
            tab_player[0] = case_player

            tab_enemy_lasers = np.ndarray.flatten(np.array(tab_enemy_lasers))
            tab_player_lasers = np.ndarray.flatten((np.array(tab_player_lasers)))
            tab_enemy = np.ndarray.flatten(np.array(tab_enemy))
            tab_player = np.ndarray.flatten(np.array(tab_player))

            elts = np.array([norm_cooldown, laser_above])
            array = np.concatenate((tab_player_lasers, tab_enemy_lasers, tab_enemy, tab_player, elts), None)

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

    vis_net(c, view=False)
    # svg2png()


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
    # vis_net(c, view=False)
    # svg2png()


def run_neat(c):
    p = neat.Checkpointer.restore_checkpoint("neat-checkpoint-81")
    # p = neat.Population(c)
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    p.add_reporter(neat.Checkpointer(1))
    pe = neat.ParallelEvaluator(3, parallelEval)

    best = None
    # best = p.run(eval_genomes, 100)
    best = p.run(pe.evaluate, 4)

    with open("best.pickle", "wb") as f:
        pickle.dump(best, f)
        print("best saved")


def test_ai(c):
    with open("best.pickle", "rb") as f:
        best = pickle.load(f)

    # print(best)
    # vis_net(c, view=False)
    window = pygame.display.set_mode((WIDTH, HEIGHT))

    game = GameAi(Game(WIDTH, HEIGHT, draw=True, human=False, fast=False), draw=True)
    game.test_ai(best, c)


# def vis_net(c, view=True):
# with open("best.pickle", "rb") as f:
#    best = pickle.load(f)

# names = {-6: "laser_above", -5: "norm_relative_enemy_y", -4: "norm_relative_enemy_x",
#         -3: "norm_nearest_laser_relative_y", -2: "norm_nearest_laser_relative_x", -1: "norm_cooldown",
#         0: "shoot", 1: "left", 2: "right", 3: "nothing"}
# c.genome_config.input_keys = {-6: "-6", -5: "-5", -4: "-4", -3: "-3", -2: "-2", -1: "-1",
#                                   0: "shoot", 1: "left", 2: "right", 3: "nothing"}
# visualize.draw_net(c, best, filename="graph_neural_network", view=view, node_names=names)


if __name__ == "__main__":
    pygame.font.init()

    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config.txt")
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet,
                         neat.DefaultStagnation, config_path)

    run_neat(config)
    #test_ai(config)
    # vis_net(config)
