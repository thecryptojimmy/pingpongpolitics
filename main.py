import pygame
import random
import os
import sys

# Function to get the correct resource path
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

# Initialize Pygame and mixer
pygame.init()
pygame.mixer.init()

# Constants for the game
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
PADDLE_WIDTH, PADDLE_HEIGHT = 15, 90
BALL_RADIUS = 7
AI_MOVE_SPEED = 4.5  # Adjusted for easier difficulty
AI_REACTION_DELAY = 20  # Increased for easier difficulty
AI_MISTAKE_PROBABILITY = 0.15  # Adjusted for more realistic behavior
RED = (255, 0, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
NAVY_GREEN = (0, 102, 51)
BUTTON_COLOR = (100, 200, 255)
HOVER_COLOR = (150, 150, 255)

# Setup the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Ping Pong Politics")

# Font for scoring, menu, and buttons
font = pygame.font.Font(None, 74)
menu_font = pygame.font.Font(None, 50)
button_font = pygame.font.Font(None, 36)

# Load paddle images
left_paddle_image = pygame.image.load(resource_path('obama_left.png'))
right_paddle_image = pygame.image.load(resource_path('trump_right.png'))

# Load sound effect and music
ball_hit_sound = pygame.mixer.Sound(resource_path('ball_hit.wav'))
menu_music_path = resource_path('menu_sound.mp3')
game_music_path = resource_path('game_sound.mp3')

# Load menu and game backgrounds
menu_background = pygame.image.load(resource_path('menu_background.png'))
menu_background = pygame.transform.scale(menu_background, (SCREEN_WIDTH, SCREEN_HEIGHT))
game_background = pygame.image.load(resource_path('game_background.png'))
game_background = pygame.transform.scale(game_background, (SCREEN_WIDTH, SCREEN_HEIGHT))

# Background music volume control
background_music_volume = 0.5
pygame.mixer.music.set_volume(background_music_volume)

# Start playing menu music by default
pygame.mixer.music.load(menu_music_path)
pygame.mixer.music.play(-1)

# Load and set the logo
logo = pygame.image.load(resource_path('fav.png'))
pygame.display.set_icon(logo)

# Menu options and buttons
menu_options = ["1 Player", "2 Players"]
selected_option = None
game_mode_buttons = [
    pygame.Rect(SCREEN_WIDTH // 2 - 100, 200, 200, 50),
    pygame.Rect(SCREEN_WIDTH // 2 - 100, 260, 200, 50)
]
start_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, 400, 200, 50)
return_button = pygame.Rect(SCREEN_WIDTH // 2 - 100, 400, 200, 50)

# Music toggle button
music_on = True
music_toggle_button = pygame.Rect(SCREEN_WIDTH - 150, SCREEN_HEIGHT - 50, 140, 40)

def draw_button(button, text, is_hovered):
    pygame.draw.rect(screen, HOVER_COLOR if is_hovered else BUTTON_COLOR, button)
    text_surf = button_font.render(text, True, WHITE)
    screen.blit(text_surf, (button.x + (button.width - text_surf.get_width()) // 2,
                            button.y + (button.height - text_surf.get_height()) // 2))

def draw_music_toggle_button():
    text = "Music: On" if music_on else "Music: Off"
    draw_button(music_toggle_button, text, music_toggle_button.collidepoint(pygame.mouse.get_pos()))

def toggle_music():
    global music_on
    music_on = not music_on
    if music_on:
        pygame.mixer.music.unpause()
    else:
        pygame.mixer.music.pause()

def display_menu():
    screen.blit(menu_background, (0, 0))  # Draw the background image
    for i, button in enumerate(game_mode_buttons):
        draw_button(button, menu_options[i], button.collidepoint(pygame.mouse.get_pos()))
    if selected_option is not None:
        draw_button(start_button, "Start Game", start_button.collidepoint(pygame.mouse.get_pos()))
    draw_music_toggle_button()
    instructions = menu_font.render("Choose Game Mode", True, WHITE)
    screen.blit(instructions, (SCREEN_WIDTH // 2 - instructions.get_width() // 2, 150))
    pygame.display.flip()

def display_character_selection_screen(left_player_selection=None):
    screen.fill((0, 0, 0))  # Or use a background image

    # Load selection images
    obama_left_select = pygame.image.load(resource_path('obama_left_select.png'))
    obama_right_select = pygame.image.load(resource_path('obama_right_select.png'))
    trump_left_select = pygame.image.load(resource_path('trump_left_select.png'))
    trump_right_select = pygame.image.load(resource_path('trump_right_select.png'))

    # Define rects for selection images
    obama_left_rect = obama_left_select.get_rect(center=(100, SCREEN_HEIGHT // 2))
    obama_right_rect = obama_right_select.get_rect(center=(200, SCREEN_HEIGHT // 2))
    trump_left_rect = trump_left_select.get_rect(center=(300, SCREEN_HEIGHT // 2))
    trump_right_rect = trump_right_select.get_rect(center=(400, SCREEN_HEIGHT // 2))

    # Draw the images
    screen.blit(obama_left_select, obama_left_rect)
    screen.blit(obama_right_select, obama_right_rect)
    screen.blit(trump_left_select, trump_left_rect)
    screen.blit(trump_right_select, trump_right_rect)

    # Draw blue border if selected
    if left_player_selection == 'obama':
        pygame.draw.rect(screen, BLUE, obama_left_rect, 3)
    # ... Similarly for other selections

    pygame.display.flip()

def init_game():
    global paddle1_y, paddle2_y, ball_x, ball_y, ball_x_vel, ball_y_vel, score1, score2, game_active, game_mode
    global ai_reaction_counter, ai_mistake_counter, ai_correct_direction
    paddle1_y = paddle2_y = SCREEN_HEIGHT // 2 - PADDLE_HEIGHT // 2
    ball_x = SCREEN_WIDTH // 2
    ball_y = SCREEN_HEIGHT // 2
    ball_x_vel = random.choice([-5, 5])
    ball_y_vel = random.choice([-5, 5])
    score1 = 0
    score2 = 0
    game_active = True
    game_mode = selected_option if selected_option is not None else 0
    ai_reaction_counter = AI_REACTION_DELAY
    ai_mistake_counter = 0
    ai_correct_direction = True

def check_collision():
    global ball_x_vel, ball_y_vel
    collision = False
    if ball_y - BALL_RADIUS <= 0 or ball_y + BALL_RADIUS >= SCREEN_HEIGHT:
        ball_y_vel *= -1
        collision = True
    if (ball_x - BALL_RADIUS <= PADDLE_WIDTH and paddle1_y <= ball_y <= paddle1_y + PADDLE_HEIGHT) or \
       (ball_x + BALL_RADIUS >= SCREEN_WIDTH - PADDLE_WIDTH and paddle2_y <= ball_y <= paddle2_y + PADDLE_HEIGHT):
        ball_x_vel *= -1
        collision = True
    if collision:
        ball_hit_sound.play()

def ai_movement():
    global paddle2_y, ai_reaction_counter, ai_mistake_counter, ai_correct_direction

    # AI starts moving after a delay
    if ai_reaction_counter > 0:
        ai_reaction_counter -= 1
        return

    # AI movement logic
    if ball_x > SCREEN_WIDTH / 2 and ball_x_vel > 0:
        # Near-miss logic
        if random.random() < AI_MISTAKE_PROBABILITY:
            target_y = ball_y + random.randint(-30, 30)  # AI misjudges by up to 30 pixels
        else:
            target_y = ball_y

        if paddle2_y + PADDLE_HEIGHT / 2 < target_y:
            paddle2_y += AI_MOVE_SPEED
        elif paddle2_y + PADDLE_HEIGHT / 2 > target_y:
            paddle2_y -= AI_MOVE_SPEED

    paddle2_y = max(min(paddle2_y, SCREEN_HEIGHT - PADDLE_HEIGHT), 0)

def display_end_screen():
    screen.fill((0, 0, 0))
    draw_button(return_button, "Return to Menu", return_button.collidepoint(pygame.mouse.get_pos()))
    winner = "Obama" if score1 >= 10 else "Trump"
    game_over_text = font.render(f"{winner} Won!", True, WHITE)
    screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, 150))

    pygame.display.flip()

# Main game loop
running = True
clock = pygame.time.Clock()
in_menu = True
in_end_screen = False

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            if in_menu:
                if music_toggle_button.collidepoint(mouse_pos):
                    toggle_music()
                for i, button in enumerate(game_mode_buttons):
                    if button.collidepoint(mouse_pos):
                        selected_option = i
                if selected_option is not None and start_button.collidepoint(mouse_pos):
                    in_menu = False
                    game_active = True
                    pygame.mixer.music.load(game_music_path)
                    pygame.mixer.music.play(-1)
                    init_game()
            elif in_end_screen:
                if return_button.collidepoint(mouse_pos):
                    in_end_screen = False
                    in_menu = True
                    selected_option = None
                    pygame.mixer.music.load(menu_music_path)
                    pygame.mixer.music.play(-1)

    if in_menu:
        display_menu()
    elif in_end_screen:
        display_end_screen()
    else:  # Game is active (not in menu or end screen)
        screen.blit(game_background, (0, 0))  # Draw the game background

        # Game logic
        if game_active:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_z] and paddle1_y > 0:
                paddle1_y -= AI_MOVE_SPEED
            if keys[pygame.K_w] and paddle1_y < SCREEN_HEIGHT - PADDLE_HEIGHT:
                paddle1_y += AI_MOVE_SPEED

            if game_mode == 0:  # Single player mode
                ai_movement()

            else:  # Two player mode
                if keys[pygame.K_UP] and paddle2_y > 0:
                    paddle2_y -= AI_MOVE_SPEED
                if keys[pygame.K_DOWN] and paddle2_y < SCREEN_HEIGHT - PADDLE_HEIGHT:
                    paddle2_y += AI_MOVE_SPEED

            # Ball movement
            ball_x += ball_x_vel
            ball_y += ball_y_vel

            # Collision detection
            check_collision()

            # Scoring
            if ball_x < 0:
                score2 += 1
                if score2 >= 10:
                    game_active = False
                    in_end_screen = True
                    pygame.mixer.music.stop()
                else:
                    ball_x = SCREEN_WIDTH // 2
                    ball_y = SCREEN_HEIGHT // 2
                    ball_x_vel = random.choice([-5, 5])
                    ball_y_vel = random.choice([-5, 5])

            if ball_x > SCREEN_WIDTH:
                score1 += 1
                if score1 >= 10:
                    game_active = False
                    in_end_screen = True
                    pygame.mixer.music.stop()
                else:
                    ball_x = SCREEN_WIDTH // 2
                    ball_y = SCREEN_HEIGHT // 2
                    ball_x_vel = random.choice([-4.5, 4.5])
                    ball_y_vel = random.choice([-4.5, 4.5])

        # Drawing the paddles and the ball
        screen.blit(left_paddle_image, (0, paddle1_y))
        screen.blit(right_paddle_image, (SCREEN_WIDTH - PADDLE_WIDTH, paddle2_y))
        pygame.draw.circle(screen, NAVY_GREEN, (ball_x, ball_y), BALL_RADIUS)

        # Drawing the score
        text = font.render(str(score1), 1, BLUE)
        screen.blit(text, (250, 10))
        text = font.render(str(score2), 1, RED)
        screen.blit(text, (550, 10))

        pygame.display.flip()

    clock.tick(60)

pygame.quit()
