from game import Game
import pygame
from consts import WIDTH, HEIGHT
import csv
import pandas



def save(file):
    pass

def calc_inputs(game):
    nearest_enemy_y = 0
    nearest_enemy_x = 0
    laser_above = False
    nearest_laser_dist = (WIDTH ** 2 + HEIGHT ** 2) ** 0.5
    nearest_laser_relative_x = WIDTH
    nearest_laser_relative_y = HEIGHT
    relative_enemy_x = WIDTH / 2
    relative_enemy_y = 100 * HEIGHT
    if len(game.enemies) >= 1 and game.enemies[0].y > 0:
        nearest_enemy_y = game.enemies[0].y + game.enemies[0].get_height() / 2
        nearest_enemy_x = game.enemies[0].x + game.enemies[0].get_width() / 2
    for enemy in game.enemies:
        for laser in enemy.lasers:
            laser_relative_x = laser.true_x - game.player.true_x
            laser_relative_y = laser.true_y - game.player.true_y
            dist = (laser_relative_x ** 2 + laser_relative_y ** 2) ** 0.5
            if game.player.x <= laser.true_x - laser.true_width / 2 and laser.true_x + laser.true_width / 2 <= game.player.x + game.player.get_width() and game.player.y >= laser.true_y:
                laser_above = True
            if dist < nearest_laser_dist:
                nearest_laser_dist = dist
                nearest_laser_relative_x = laser_relative_x
                nearest_laser_relative_y = laser_relative_y
    relative_enemy_y = nearest_enemy_y - game.player.y
    relative_enemy_x = nearest_enemy_x - game.player.x

    # Normalizing inputs
    norm_relative_enemy_x = relative_enemy_x / WIDTH
    norm_relative_enemy_y = relative_enemy_y / HEIGHT
    norm_player_x = game.player.x / WIDTH
    norm_player_y = game.player.y / HEIGHT
    norm_nearest_laser_dist = nearest_laser_dist / ((WIDTH ** 2 + HEIGHT ** 2) ** 0.5)
    norm_cooldown = game.player.cool_down_counter / game.player.COOLDOWN
    norm_nearest_laser_relative_x = nearest_laser_relative_x / WIDTH
    norm_nearest_laser_relative_y = nearest_laser_relative_y / HEIGHT

    return [round(norm_relative_enemy_x, 3), round(norm_relative_enemy_y, 3), round(norm_player_x, 3),
            round(norm_player_y, 3), round(norm_cooldown, 3), round(norm_nearest_laser_relative_x, 3),
            round(norm_nearest_laser_relative_y, 3), int(laser_above)]


if __name__ == "__main__":
    pygame.font.init()

    game = Game(WIDTH, HEIGHT, True, True, False, player_h=100, lives=5)

    with open('data.csv', 'w', newline='') as file:
    # with open('data.csv', 'a') as file:
        writer = csv.writer(file)

        writer.writerow(["norm_relative_enemy_x", "norm_relative_enemy_y", "norm_player_x", "norm_player_y",
                         "norm_cooldown", "norm_nearest_laser_relative_x", "norm_nearest_laser_relative_y",
                         "laser_above", "player_input"])

        i = 0
        while game.run:

            i += 1

            infos = game.loop()

            if infos.lost:
                quit()

            # if the player shoots
            if infos.decision != 0:
                inputs = calc_inputs(game)
                inputs.append(infos.decision)
                writer.writerow(inputs)
                i = 0
            elif i >= 10:
                inputs = calc_inputs(game)
                inputs.append(infos.decision)
                writer.writerow(inputs)
                i = 0







