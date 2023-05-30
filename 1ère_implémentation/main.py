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

"""

1ère implémentation

Seule version commentée

"""


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

    def compute_inputs(self):
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

        # Norme les valeurs
        norm_relative_enemy_x = relative_enemy_x/WIDTH
        norm_relative_enemy_y = relative_enemy_y/HEIGHT
        norm_player_x = self.game.player.x/WIDTH
        norm_player_y = self.game.player.y/HEIGHT
        norm_nearest_laser_dist = nearest_laser_dist / ((WIDTH ** 2 + HEIGHT ** 2) ** 0.5)
        norm_cooldown = self.game.player.cool_down_counter / self.game.player.COOLDOWN
        norm_nearest_laser_relative_x = nearest_laser_relative_x / WIDTH
        norm_nearest_laser_relative_y = nearest_laser_relative_y /HEIGHT

        return (norm_cooldown, norm_nearest_laser_relative_x, norm_nearest_laser_relative_y,
                                   norm_relative_enemy_x, norm_relative_enemy_y, laser_above)
    
    def test_ai(self, genome, c):
        net = neat.nn.FeedForwardNetwork.create(genome, c)
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit()
            inputs = self.compute_inputs()
            output = net.activate(inputs)
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
            game_info = self.game.loop()
            if game_info.lost:
                print(f"Total d'ennemies tués: {game_info.nb_enemies_killed}")
                break

    # Entrainement
    def train_ai(self, genome, c):
        net = neat.nn.FeedForwardNetwork.create(genome, c) # réseau du génome
        self.genome = genome
        prev_pos = 0

        # Boucle de jeu
        while True:
            if self.draw:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        quit()

            inputs = self.compute_inputs() # calcule des valeurs que l'on donne en entrée

            output = net.activate(inputs) # on donne les inputs au réseau et il nous renvoie les valeurs de sorties
            decision = output.index(max(output))  # 0 = tirer, 1 = aller à gauche, 2 = aller à droite, 3 = ne rien faire
            match decision:
                case 0: self.shoot()
                case 1: self.move_left()
                case 2: self.move_right()
                case 3: genome.fitness -= 0.01 # pénalité dans ce cas là

            genome.fitness += 0.01 # bonus pour toujours être en vie

            if self.game.player.x == prev_pos:
                genome.fitness -= 0.03 # pénalité pour être au même endroit

            prev_pos = self.game.player.x

            #laser_above = inputs[5]
            #if laser_above:
            #    genome.fitness -= 1 # pénalité si directement sous un laser

            # fait avancer le jeu d'un pas
            game_info = self.game.loop() # contient des infos (si on a perdu, nombres d'enemies tué)

            if game_info.lost: # on a perdu
                genome.fitness += 50 * game_info.nb_enemies_killed # gros bonus pour le nombre d'enemies tué
                break # fin de la partie, retour à la fonction d'appel

# fonction qui va entrainer l'ensemble de la population 1 fois
def eval_genomes(genomes, c):
    draw = False # pour ne pas ouvrir la fenêtre de jeu et dessiner
    human = False # pour faire jouer l'ia au lieu d'une vraie personne
    fast = False # pour ne pas attendre entre chaque frame
    nb_game = 3

    # Entrainement de génome 1 à 1
    for i, (genome_id, genome) in enumerate(genomes):
        genome.fitness = 0 # initialisation du fitness du génome
        for _ in range(nb_game): # le génome joue nb_game parties
            game = GameAi(Game(WIDTH, HEIGHT, draw, human, fast), draw) # instanciation de l'ia avec le jeu
            game.train_ai(genome, c) # entrainnement, joue 1 partie avec le génome
        
# idem à eval_genomes, juste adapter pour foncitonner avec plusieurs thread afin d'accélérer l'entrainement
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
    # vis_net(c, view=True)
    # svg2png()

# Entrainement de l'ia
def run_neat(c):
    p = neat.Checkpointer.restore_checkpoint("neat-checkpoint-167") # reprend l'entrainemnt à partir d'un checkpoint
    # p = neat.Population(c) # commence une nouvelle population

    # pour avoir les informations dans la console pendant l'évolution
    p.add_reporter(neat.StdOutReporter(True)) 
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    p.add_reporter(neat.Checkpointer(1)) #checkpoint à chaque génération

    pe = neat.ParallelEvaluator(num_workers=4, eval_function=parallelEval) # pour entrainer en parrallel, accélère grandement l'entrainement

    best = None
    # lance l'évolution pour n générations, la fonction de fitness sera appelé 1 fois à chaque génération
    # best = p.run(fitness_function=eval_genomes, n=1) # version séquentielle
    best = p.run(pe.evaluate, 1) # version en parallel

    # sauvegarde le meilleur génome obtenu
    with open("best.pickle", "wb") as f:
        pickle.dump(best, f)
        print("best saved")

# Test de l'ia
def test_ai(c):
    with open("best.pickle", "rb") as f:
        best = pickle.load(f)

    # print(best)
    window = pygame.display.set_mode((WIDTH, HEIGHT))

    game = GameAi(Game(WIDTH, HEIGHT, draw=True, human=False, fast=False), draw=True)
    game.test_ai(best, c)

# Créer le diagramme du réseau du génome sauvegardé
def vis_net(c):
    with open("best.pickle", "rb") as f:
        best = pickle.load(f)

    names = {-6: "laser_above", -5: "norm_relative_enemy_y", -4: "norm_relative_enemy_x",
             -3: "norm_nearest_laser_relative_y", -2: "norm_nearest_laser_relative_x", -1: "norm_cooldown",
             0: "shoot", 1: "left", 2: "right", 3: "nothing"}
    c.genome_config.input_keys = {-6: "-6", -5: "-5", -4: "-4", -3: "-3", -2: "-2", -1: "-1",
                                       0: "shoot", 1: "left", 2: "right", 3: "nothing"}
    visualize.draw_net(c, best, filename="graph_final", view=True, node_names=names)


if __name__ == "__main__":
    pygame.font.init()

    # Charge les configurations de neat à partir du fichier configs.txt
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config.txt")
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet,
                         neat.DefaultStagnation, config_path)

    # run_neat(config) # pour entrainer l'ia
    test_ai(config) # pour tester l'ia
    # vis_net(config) # pour générer le diagramme du réseau
