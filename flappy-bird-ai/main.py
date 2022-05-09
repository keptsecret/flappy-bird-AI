import argparse
import sys
from time import time
import pygame

from player import Player
from pipe import PipePair
from population import Population

bird_yellow = (250, 239, 32)
pipe_green = (105, 214, 21)
sky_blue = (52, 213, 235)
white = (255, 255, 255)

window_size = (500, 720)
font_size = 60
manual_mode = False


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
                    player.flap()
        
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

        text_surf = font.render(f'{player.score}', True, white)

        screen.blit(surf, (0,0))
        screen.blit(text_surf, (size[0]/2 - font_size/2, 0))
        pygame.display.flip()
        prev_time = curr_time


def game_loop_ai(screen, size, font, population, pipe_pairs):
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
        
        surf = pygame.Surface(size)
        surf.fill(sky_blue)

        delta_time = 0.0027
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

        score_surf = font.render(f'{population.global_best_score}', True, white)
        gen_surf = font.render(f'Gen: {population.gen}', True, white)

        screen.blit(surf, (0,0))
        screen.blit(score_surf, (size[0]/2 - font_size/2, 5))
        screen.blit(gen_surf, (5, 5))
        pygame.display.flip()


def reset(pipe_pairs):
    for pipe in pipe_pairs:
        pipe.reset()
    pipe_pairs[0].start()


def main():
    parser = argparse.ArgumentParser(description='Watch AI learn to play Flappy Bird!')
    parser.add_argument('--manual', action='store_true', help='manual option to play it yourself')
    args = parser.parse_args()
    manual_mode = args.manual

    pygame.init()
    pygame.font.init()

    font = pygame.font.SysFont('Calibri', font_size, True)

    screen = pygame.display.set_mode(window_size)
    pipe_pairs = [PipePair(500), PipePair(500)]
    pipe_pairs[0].start()
    player = Player(pipes=pipe_pairs)
    
    if manual_mode:
        game_loop(screen, window_size, font, player, pipe_pairs)
    else:
        population = Population(500)
        game_loop_ai(screen, window_size, font, population, pipe_pairs)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()