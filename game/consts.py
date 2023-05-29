import pygame
from os import path

script_path = path.dirname(path.abspath(__file__))
assets_path = path.join(script_path, "assets")
WIDTH, HEIGHT = 750, 750

RED_SPACE_SHIP = pygame.image.load(path.join(assets_path, "pixel_ship_red_small.png"))
GREEN_SPACE_SHIP = pygame.image.load(path.join(assets_path, "pixel_ship_green_small.png"))
BLUE_SPACE_SHIP = pygame.image.load(path.join(assets_path, "pixel_ship_blue_small.png"))

YELLOW_SPACE_SHIP = pygame.image.load(path.join(assets_path, "pixel_ship_yellow.png"))

RED_LASER = pygame.image.load(path.join(assets_path, "pixel_laser_red.png"))
GREEN_LASER = pygame.image.load(path.join(assets_path, "pixel_laser_green.png"))
BLUE_LASER = pygame.image.load(path.join(assets_path, "pixel_laser_blue.png"))
YELLOW_LASER = pygame.image.load(path.join(assets_path, "pixel_laser_yellow.png"))

BG =  pygame.transform.scale(pygame.image.load(path.join(assets_path, "background-black.png")), (WIDTH, HEIGHT))