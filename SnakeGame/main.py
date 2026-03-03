import pygame
import settings
from game import Game


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode(
        (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)
    )
    pygame.display.set_caption(settings.TITLE)

    game = Game(screen)
    game.run()


if __name__ == "__main__":
    main()
