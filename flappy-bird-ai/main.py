import sys
from time import time
import pygame

from player import Player
from pipe import PipePair
from population import Population

bird_yellow = (250, 239, 32)
pipe_green = (105, 214, 21)
sky_blue = (52, 213, 235)

window_size = (500, 720)
font_size = 60
debug = False

def game_loop(screen, size, font, player, pipe_pairs):
    prev_time = time()

    while True:
        if not player.is_alive:
            print("Player dead!")
            break

        for event in pygame.event.get():
            curr_time = time()
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    player.flap(curr_time)
        
        curr_time = time()
        surf = pygame.Surface(size)
        surf.fill(sky_blue)

        delta_time = curr_time - prev_time
        for pair in pipe_pairs:
            if pair.active:
                if pair.top_pipe.position[0] < size[0] / 2 - 50:
                    pipe_pairs[1].start()
                pair.update(delta_time)
        player.update(delta_time)

        for pair in pipe_pairs:
            if pair.active:
                pair.draw(surf)
        player.draw(surf)

        text_surf = font.render(f'{player.score}', True, (255,255,255))
        if debug:
            debug_surf = font.render(f'{player.velocity}', True, (0,0,0))

        screen.blit(surf, (0,0))
        screen.blit(text_surf, (size[0]/2 - font_size/2, 0))
        if debug:
            screen.blit(debug_surf, (0, 0))
        pygame.display.flip()
        prev_time = curr_time


def game_loop_ai(screen, size, font, population, pipe_pairs):
    prev_time = time()

    while True:
        for event in pygame.event.get():
            curr_time = time()
            if event.type == pygame.QUIT:
                pygame.quit()
        
        curr_time = time()
        surf = pygame.Surface(size)
        surf.fill(sky_blue)

        delta_time = curr_time - prev_time
        for pair in pipe_pairs:
            if pair.active:
                if pair.top_pipe.position[0] < size[0] / 2 - 50:
                    pipe_pairs[1].start()
                pair.update(delta_time)

        for pair in pipe_pairs:
            if pair.active:
                pair.draw(surf)

        if not population.done():
            population.update_alive(surf, delta_time)
        else:
            population.natural_selection()
            reset(pipe_pairs)

        text_surf = font.render(f'{population.global_best_score}', True, (255,255,255))

        screen.blit(surf, (0,0))
        screen.blit(text_surf, (size[0]/2 - font_size/2, 0))
        pygame.display.flip()
        prev_time = curr_time


def reset(pipe_pairs):
    for pipe in pipe_pairs:
        pipe.reset()
    pipe_pairs[0].start()


def main():
    pygame.init()
    pygame.font.init()

    font = pygame.font.SysFont('Arial', font_size, True)

    screen = pygame.display.set_mode(window_size)
    pipe_pairs = [PipePair(500), PipePair(500)]
    pipe_pairs[0].start()
    player = Player(pipes=pipe_pairs)
    population = Population(100)

    # game_loop(screen, window_size, font, player, pipe_pairs)
    game_loop_ai(screen, window_size, font, population, pipe_pairs)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()