import time
import pygame
import neat
import os
import pickle
from consts import WIDTH, HEIGHT
from game import Game


class GameAi:
    def __init__(self, game, window, draw):
        self.genome = None
        self.game = game
        self.window = window
        self.draw = draw

    def train_ai(self, genome, c):
        run = True
        start_time = time.time()
        net = neat.nn.FeedForwardNetwork.create(genome, c)
        self.genome = genome

        while run:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit()

            game_info = self.game.loop() # need to add count for number of kills


def eval_genomes(genomes, c):
    window = pygame.display.set_mode((WIDTH, HEIGHT))
    draw = False

    for i, (genome_id, genome) in enumerate(genomes):
        genome.fitness = 0
        game = GameAi(Game(window, WIDTH, HEIGHT, draw), window, draw)

        game.train_ai(genome, c)


def run_neat(c):
    # p = neat.Checkpointer.restore_checkpoint("checkpoint_name")
    p = neat.Population(c)
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    p.add_reporter(neat.Checkpointer(1))

    best = p.run(eval_genomes, 50)

    with open("best.pickle", "wb") as f:
        pickle.dump(best, f)


if __name__ == "__main__":

    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config.txt")
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet,
                         neat.DefaultStagnation, config_path)
