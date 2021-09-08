#! /usr/bin/env python3

import pygame, sys, random, time, threading
import math

FPS = 120
GRAVITY = 0.068
FLAP_LEVEL = 1.6
CURRENT_SCREEN_SIZE = (640, 360)
SPEED = 1

score = 0
high_score = 0

pygame.init()
pygame.mixer.pre_init(frequency = 44100, size = 16, channels = 1, buffer = 512)
# screen = pygame.display.set_mode((0, 0), pygame.HWSURFACE, vsync=1)
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()

game_font = pygame.font.Font("assets/fonts/04B_19.ttf", 24)
game_font_high = pygame.font.Font("assets/fonts/04B_19.ttf", 32)
game_font_over = pygame.font.Font("assets/fonts/04B_19.ttf", 42)

sfx_die = pygame.mixer.Sound('assets/sounds/sfx_die.wav')
sfx_hit = pygame.mixer.Sound('assets/sounds/sfx_hit.wav')
sfx_point = pygame.mixer.Sound('assets/sounds/sfx_point.wav')
sfx_swooshing = pygame.mixer.Sound('assets/sounds/sfx_swooshing.wav')
sfx_wing = pygame.mixer.Sound('assets/sounds/sfx_wing.wav')

screen_size = screen.get_size()
screen_bounding_rect = screen.get_bounding_rect()
screen_width, screen_height = screen_size

current_surface = pygame.Surface(CURRENT_SCREEN_SIZE)

current_surface_size = current_surface.get_size()
current_surface_bounding_rect = current_surface.get_bounding_rect()
current_surface_width, current_surface_height = current_surface_size

background_surface = pygame.image.load('assets/images/background-night.png').convert()
background_surface_size = background_surface.get_size()
background_surface_width, background_surface_height = background_surface_size

floor_surface = pygame.image.load('assets/images/base.png').convert()
floor_surface_size = floor_surface.get_size()
floor_surface_width, floor_surface_height = floor_surface_size
# floor_surface = pygame.transform.scale(floor_surface, (current_surface_width, floor_surface_height))

bird_surface_images = ['assets/images/bluebird-upflap.png', 'assets/images/bluebird-midflap.png', 'assets/images/bluebird-downflap.png']

def quiet_app(message = 'quiet'):
    sys.stdout.write(message + '\n')
    pygame.quit()
    sys.exit()

def bird_surface_image (src: str):
    bird_surface = pygame.image.load(src).convert_alpha()
    bird_surface_size = bird_surface.get_size()
    bird_surface_width, bird_surface_height = bird_surface_size
    bird_surface = pygame.transform.scale(bird_surface, (math.ceil(bird_surface_width / 2), math.ceil(bird_surface_height / 2)))
    bird_surface_size = bird_surface.get_size()
    bird_surface_width, bird_surface_height = bird_surface_size
    bird_surface_rect = bird_surface.get_rect(center=(current_surface_width / 4.8, (current_surface_height - bird_surface_height) / 2))
    return bird_surface, bird_surface_size, bird_surface_rect

bird_surfaces = [
    bird_surface_image(src) for src in bird_surface_images
]

nbird_surface = 0
bird_surface, bird_surface_size, bird_surface_rect = bird_surfaces[nbird_surface]
bird_surface_width, bird_surface_height = bird_surface_size

pipe_surface = pygame.image.load('assets/images/pipe-red.png').convert()
# pipe_surface = pygame.transform.scale2x(pipe_surface)
pipe_surface_size = pipe_surface.get_size()
pipe_surface_width, pipe_surface_height = pipe_surface_size

pipe_list = []
SPAWNPIPE = pygame.USEREVENT
pygame.time.set_timer(SPAWNPIPE, 1200)
pipe_height = [80, 160, 200]

background_pos_x, background_pos_y = (0, current_surface_height - background_surface_height)
floor_pos_x, floor_pos_y = (0, current_surface_height - (floor_surface_height - (4 * floor_surface_height / 10)))

background_nspawn = 0

def draw_background():
    global background_pos_x, background_nspawn
    n = math.ceil(current_surface_width / background_surface_width)
    for i in range(background_nspawn, n + background_nspawn):
        current_surface.blit(background_surface, (background_surface_width * i + background_pos_x, background_pos_y))
        current_surface.blit(background_surface, (background_surface_width * (n + i) + background_pos_x, background_pos_y))
    c = math.floor(math.fabs(background_pos_x) / background_surface_width)
    if background_nspawn < c:
        # print('spawn', background_nspawn, n + background_nspawn)
        # current_surface.blit(background_surface, (background_surface_width * 2 * i + background_pos_x, background_pos_y))
        background_nspawn = c
    # background_pos_x = background_pos_x - SPEED if abs(background_pos_x) < current_surface_width else 0
    background_pos_x = background_pos_x - (SPEED / 10)

floor_nspawn = 0

def draw_floor():
    global floor_pos_x, floor_nspawn
    n = math.ceil(current_surface_width / floor_surface_width)
    # if 2 ** 64 - 1 <= n + floor_nspawn: quiet_app('max long long values')
    for i in range(floor_nspawn, n + floor_nspawn):
        current_surface.blit(floor_surface, (floor_surface_width * i + floor_pos_x, floor_pos_y))
        current_surface.blit(floor_surface, (floor_surface_width * (n + i) + floor_pos_x, floor_pos_y))
    c = math.floor(math.fabs(floor_pos_x) / floor_surface_width)
    if floor_nspawn < c:
        # print('spawn', floor_nspawn, n + floor_nspawn)
        # current_surface.blit(floor_surface, (floor_surface_width * 2 * i + floor_pos_x, floor_pos_y))
        floor_nspawn = c
    # floor_pos_x = floor_pos_x - SPEED if abs(floor_pos_x) < current_surface_width else 0
    floor_pos_x = floor_pos_x - SPEED

def create_pipe():
    random_pipe_pos_x = random.choice(pipe_height)
    top_pipe = pipe_surface.get_rect(midtop = ((current_surface_width / 2) + current_surface_width, random_pipe_pos_x - current_surface_height))
    bottom_pipe = pipe_surface.get_rect(midtop = ((current_surface_width / 2) + current_surface_width, random_pipe_pos_x + bird_surface_width))
    return top_pipe, bottom_pipe

def move_pipes(pipes):
    for pipe in pipes:
        pipe.centerx = pipe.centerx - SPEED
    return pipes

def draw_pipes(pipes):
    global pipe_list
    for pipe in pipes:
        if pipe.centerx <= - current_surface_width:
            # print(len(pipe_list))
            pipe_list = pipe_list[1:]
            continue
        if pipe.bottom >= current_surface_height:
            current_surface.blit(pipe_surface, pipe)
        else:
            current_surface.blit(pygame.transform.flip(pipe_surface,False,True), pipe)

def drop_shadow_text(font = game_font, text = "", color = (255, 255, 255), shadow = (15, 15, 15), pos = (0, 0)):
        score_surface = font.render(text, False, shadow)
        score_rect = score_surface.get_rect(center=pos)
        current_surface.blit(score_surface, (score_rect.x + 2, score_rect.y + 2, score_rect.w, score_rect.h))

        score_surface = font.render(text, False, color)
        score_rect = score_surface.get_rect(center=pos)
        current_surface.blit(score_surface, score_rect)

def draw_score(activate, started):
    global high_score
    if started:
        pass
    elif activate:
        
        drop_shadow_text(text = str(int(score)), pos=(current_surface_width / 2, 32))

    else:

        drop_shadow_text(text = f'Score: {int(score)}', pos=(current_surface_width / 2, 64))

        drop_shadow_text(font = game_font_over, text = 'Game Over', pos=(current_surface_width / 2, 32))
        
        high_score = score if score > high_score else high_score

        drop_shadow_text(font = game_font_high, text = f'High Score: {int(high_score)}', pos=(current_surface_width / 2, 92))

def check_collision(pipes):
    for pipe in pipes:
        if bird_surface_rect.colliderect(pipe):
            return False

    if bird_surface_rect.top <= -(bird_surface_width * 2) or bird_surface_rect.bottom >= floor_pos_y - 2:
        return False

    return True

bird_movement = 0
bird_movement_takedown = 0
bird_stuck = 0
bird_stuck_x, bird_stuck_y = (0, floor_pos_y - (bird_surface_width / 2))

def draw_bird():
    global bird_surface, bird_surface_size, bird_surface_rect, bird_surface_width, bird_surface_height
    global bird_movement, bird_surface_rect, bird_stuck, bird_stuck_y, bird_movement_takedown, nbird_surface
    keep_movement = bird_movement
    bird_movement = keep_movement + GRAVITY
    keep_bird_surface_rect = bird_surface_rect.centery
    bird_surface_rect.centery = keep_bird_surface_rect + bird_movement
    x, y, w, h = bird_surface_rect
    # y = y if 0 <= y else 0
    bird_stuck = 1 if y <= (bird_surface_width + FLAP_LEVEL) else 0
    if bird_stuck_y <= y:
        y, bird_movement, bird_surface_rect.centery = bird_stuck_y, keep_movement, keep_bird_surface_rect
    # if (bird_surface_rect.top <= 32 and bird_movement_takedown >= 24) or not bird_can_movement:
    #     current_surface.blit(pygame.transform.rotozoom(bird_surface, - math.ceil(bird_movement * 180), 1), (x, y, w, h))
    #     bird_movement_takedown = 0
    # elif nbird_surface == 2:
    #     current_surface.blit(pygame.transform.rotozoom(bird_surface, - math.ceil(bird_movement * 45), 1), (x, y, w, h))
    # else:
    #     current_surface.blit(bird_surface, (x, y, w, h))
    current_surface.blit(bird_surface, (x, y, w, h))
    if bird_movement_takedown >= 24:
        bird_surface, bird_surface_size, _ = bird_surfaces[0]
        bird_surface_rect = bird_surface.get_rect(center = (current_surface_width / 4.8, bird_surface_rect.centery))
        # bird_surface = pygame.transform.rotozoom(bird_surface, bird_movement * 6, 1)
        bird_surface_width, bird_surface_height = bird_surface_size
        bird_movement_takedown = 0
        nbird_surface = 0
    elif bird_movement_takedown >= 12:
        bird_surface, bird_surface_size, _ = bird_surfaces[2]
        bird_surface_rect = bird_surface.get_rect(center = (current_surface_width / 4.8, bird_surface_rect.centery))
        # bird_surface = pygame.transform.rotozoom(bird_surface, bird_movement * 6, 1)
        bird_surface_width, bird_surface_height = bird_surface_size
    elif bird_movement_takedown >= 6:
        bird_surface, bird_surface_size, _ = bird_surfaces[1]
        bird_surface_rect = bird_surface.get_rect(center = (current_surface_width / 4.8, bird_surface_rect.centery))
        # bird_surface = pygame.transform.rotozoom(bird_surface, bird_movement * 6, 1)
        bird_surface_width, bird_surface_height = bird_surface_size
    if nbird_surface == 2:
        bird_movement_takedown = bird_movement_takedown + 1

game_activate = False
bird_can_movement = True
keep_speed = SPEED

game_main_menu = True

def sound_thread(fn = None):
    class T:
        @staticmethod
        def play ():
            pass
    if callable(fn):
        def play ():
            thread = threading.Thread(target=fn)
            thread.start()
            # thread.join()
        T.play = play
        return T
    return T

@sound_thread
def sound_wing():
    sfx_swooshing.play()
    time.sleep(.2)
    sfx_wing.play()

@sound_thread
def sound_die():
    sfx_hit.play()
    time.sleep(.2)
    sfx_die.play()

bird_hit = False

score_countdown = 0

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            # continuously carefully
            quiet_app()
            break
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if game_activate:
                    if not bird_stuck:
                        if bird_can_movement: 
                            sound_wing.play()
                            bird_surface, bird_surface_size, _ = bird_surfaces[1]
                            bird_surface_rect = bird_surface.get_rect(center = (current_surface_width / 4.8, bird_surface_rect.centery))
                            bird_surface_width, bird_surface_height = bird_surface_size
                            bird_movement = -FLAP_LEVEL
                            # bird_surface = pygame.transform.rotozoom(bird_surface, - bird_movement * 3, 1)
                            nbird_surface = 2
                else:
                    sound_wing.play()
                    SPEED = keep_speed
                    bird_can_movement = True
                    nbird_surface = 0
                    bird_movement = 0
                    bird_movement_takedown = 0
                    bird_stuck = 0
                    bird_stuck_x, bird_stuck_y = (0, floor_pos_y - (bird_surface_width / 2))
                    bird_surface, bird_surface_size, bird_surface_rect = bird_surfaces[0]
                    # bird_surface.get_rect(center = (current_surface_width / 4.8, (current_surface_height - bird_surface_height) / 2))
                    bird_surface_width, bird_surface_height = bird_surface_size
                    bird_surface_rect.centery = (current_surface_height - bird_surface_height) / 2
                    bird_movement = 0
                    score = 0
                    pipe_list = []
                    game_activate = True
            if event.key == pygame.K_q:
                quiet_app()
        if event.type == SPAWNPIPE:
            if game_activate:
                # print('pipe has been spawn!')
                if random.choice([True, False]):
                    pipe_list.extend(create_pipe())

    draw_background()

    if game_activate:
        pipe_list = move_pipes(pipe_list)
        draw_pipes(pipe_list)
    

    draw_floor()

    if game_activate:
        game_main_menu = False
        # game_activate = check_collision(pipe_list)
        if not check_collision(pipe_list):
            if bird_surface_rect.bottom >= floor_pos_y - 2: 
                game_activate = False
                bird_hit = False
                sound_die.play()
            else:
                if not bird_hit:
                    bird_hit = True
                    sfx_hit.play()
            bird_can_movement = False
            SPEED = 0
        draw_bird()
        # if score_countdown > 1 and score > 0:
            # score_countdown = 0
            # sfx_point.play()
        # score_countdown += 1e2
        score += 1e-2
    
    draw_score(game_activate, game_main_menu)
    

    screen.blit(pygame.transform.scale(current_surface, screen_size), (0,0))
    # pygame.image.tostring(<surface>, 'RGBA', False)
    # Image.frombytes('RGBA',<surface size>, <pygame.image.tostring>)

    pygame.display.update()
    clock.tick(FPS)
