import sys
from time import time
import pygame

from player import Player, Status
from pipe import PipePair

bird_yellow = (250, 239, 32)
pipe_green = (105, 214, 21)
sky_blue = (52, 213, 235)

def game_loop(screen, size, player, pipe_pairs):
    prev_time = time()

    while True:
        if player.status == Status.DEAD:
            print("Player dead!")
            break

        for event in pygame.event.get():
            curr_time = time()
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.handle_input(curr_time)
        
        curr_time = time()
        surf = pygame.Surface(size)
        surf.fill(sky_blue)

        delta_time = curr_time - prev_time
        pipe_list = []
        for pair in pipe_pairs:
            if pair.active:
                if pair.top_pipe.position[0] < size[0] / 2 - 50:
                    pipe_pairs[1].start()
                pair.update(delta_time)
                pipe_list += pair.get_pipes()
        player.update(2, delta_time, pipe_list)

        for pair in pipe_pairs:
            if pair.active:
                pair.draw(surf)
        player.draw(surf)

        screen.blit(surf, (0,0))
        pygame.display.flip()
        prev_time = curr_time


def main():
    pygame.init()

    size = (500, 720)

    screen = pygame.display.set_mode(size)
    player = Player((200, size[1] / 3), 30.0, bird_yellow)
    pipe_pairs = [PipePair(500), PipePair(500)]
    pipe_pairs[0].start()

    game_loop(screen, size, player, pipe_pairs)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()