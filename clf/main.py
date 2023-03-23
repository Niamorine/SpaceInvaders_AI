import pickle
from game import Game
import pygame
from consts import HEIGHT, WIDTH
from save_to_csv import calc_inputs
import pandas


def move_left():
    if game.player.x - game.player_vel > 0:
        game.player.move_left()


def move_right():
    if game.player.x + game.player_vel + game.player.get_width() < WIDTH:
        game.player.move_right()


def move_up():
    if game.player.y - game.player_vel > 0:
        game.player.move_up()


def move_down():
    if game.player.y + game.player_vel + game.player.get_height() > HEIGHT:
        game.player.move_down()


def shoot():
    game.player.shoot()





if __name__ == "__main__":
    pygame.font.init()

    game = Game(WIDTH, HEIGHT, draw=True, human=False, fast=False, player_h=100, lives=5)

    with open("gb_clf.pickle", "rb") as f:
        clf = pickle.load(f)

    while True:
        game.loop()

        inputs = calc_inputs(game)
        col_names = ["norm_relative_enemy_x", "norm_relative_enemy_y", "norm_player_x", "norm_player_y",
                     "norm_cooldown", "norm_nearest_laser_relative_x", "norm_nearest_laser_relative_y", "laser_above"]
        d = [inputs]

        df = pandas.DataFrame(d, columns=col_names)
        res = clf.predict(df)

        action = res[0]
        match action:
            case 0:
                pass
            case 1:
                move_left()
            case 2:
                move_right()
            case 3:
                move_up()
            case 4:
                move_down()
            case 5:
                shoot()



