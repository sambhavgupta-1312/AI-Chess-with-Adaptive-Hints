from .game import *
import pygame
from dashboard  import dashboard_loop
pygame.init()
def run():
    game = Game()
    game.start_game()
if __name__=="__main__":
    run()
