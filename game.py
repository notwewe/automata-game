import pygame
from PIL import Image
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 400

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Automata Game")

# Load the background image
background = pygame.image.load("background.png").convert()
background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))

# Function to load GIF frames
def load_gif_frames(filename):  
    img = Image.open(filename)
    frames = []
    try:
        while True:
            frame = img.convert("RGBA")
            frame = pygame.image.fromstring(frame.tobytes(), frame.size, "RGBA")
            frames.append(frame)
            img.seek(img.tell() + 1)
    except EOFError:
        pass
    return frames

# Define the Player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.sprite_sheet = pygame.image.load("seratojeans32x32.png").convert_alpha()
        self.frames = self.load_frames()
        self.current_frame = 0
        self.image = self.frames[self.current_frame]
        self.rect = self.image.get_rect()
        self.rect.x = 100
        self.rect.y = SCREEN_HEIGHT - 100
        self.is_jumping = False
        self.gravity = 1.0
        self.jump_height = -20
        self.jump_velocity = self.jump_height
        self.animation_speed = 0.1
        self.frame_count = 0

    def load_frames(self):
        frame_width = 32
        frame_height = 32
        frames = []
        for i in range(4):
            frame = self.sprite_sheet.subsurface(i * frame_width, 0, frame_width, frame_height)
            frames.append(pygame.transform.scale(frame, (50, 50)))
        return frames

    def update(self):
        if self.is_jumping:
            self.rect.y += self.jump_velocity
            self.jump_velocity += self.gravity
            
            if self.rect.y >= SCREEN_HEIGHT - 100:
                self.rect.y = SCREEN_HEIGHT - 100
                self.is_jumping = False
                self.jump_velocity = self.jump_height

        self.frame_count += self.animation_speed
        if self.frame_count >= 1:
            self.frame_count = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames)
        self.image = self.frames[self.current_frame]

    def jump(self):
        if not self.is_jumping:
            self.is_jumping = True
            self.jump_velocity = self.jump_height

# Define the Obstacle class
class Obstacle(pygame.sprite.Sprite):
    def __init__(self, frames):
        super().__init__()
        self.frames = frames
        self.current_frame = 0
        self.image = self.frames[self.current_frame]
        self.image = pygame.transform.scale(self.image, (45, 45))
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH + random.randint(0, 200)
        self.rect.y = random.randint(SCREEN_HEIGHT - 150, SCREEN_HEIGHT - 100)
        self.speed = 5
        self.animation_speed = 0.2
        self.frame_count = 0

    def update(self):
        self.rect.x -= self.speed
        if self.rect.x < -50:
            self.rect.x = SCREEN_WIDTH + random.randint(0, 200)
            self.rect.y = random.randint(SCREEN_HEIGHT - 150, SCREEN_HEIGHT - 100)

        self.frame_count += self.animation_speed
        if self.frame_count >= 1:
            self.frame_count = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames)
        self.image = self.frames[self.current_frame]
        self.image = pygame.transform.scale(self.image, (45, 45))

# Load obstacle frames
obstacle_frames = load_gif_frames("devil.gif")

# Create sprite groups
all_sprites = pygame.sprite.Group()
obstacles = pygame.sprite.Group()

# Game loop variables
running = True
clock = pygame.time.Clock()

# FSM Variables
state = "menu"  # Starting state
obstacle_spawn_timer = 0
obstacle_spawn_time = 120
MAX_OBSTACLES = 5

# Function to reset the game
def reset_game():
    global state, obstacle_spawn_timer, all_sprites, obstacles
    state = "menu"  # Set state to menu
    obstacle_spawn_timer = 0  # Reset obstacle spawn timer
    obstacles.empty()  # Clear obstacles
    all_sprites.empty()  # Clear all sprites

    # Initialize a new player and add to sprite groups
    new_player = Player()
    all_sprites.add(new_player)
    return new_player

# Initialize player
player = reset_game()

# Game loop
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if state == "menu" and event.key == pygame.K_SPACE:  # Start the game
                state = "playing"
            elif state == "playing" and event.key == pygame.K_SPACE:  # Jump
                player.jump()
            elif state == "game_over" and event.key == pygame.K_r:  # Restart game
                player = reset_game()  # Call reset function

    if state == "playing":
        all_sprites.update()
        
        if pygame.sprite.spritecollide(player, obstacles, False):
            state = "game_over"  # Change state to game over

        # Manage obstacle spawning
        obstacle_spawn_timer += 1
        if obstacle_spawn_timer >= obstacle_spawn_time:
            if len(obstacles) < 2:
                new_obstacle = Obstacle(obstacle_frames)
                obstacles.add(new_obstacle)
                all_sprites.add(new_obstacle)
            obstacle_spawn_timer = 0

    # Clear the screen
    screen.fill((255, 255, 255))

    # Draw the background
    screen.blit(background, (0, 0))

    if state == "menu":
        # Draw menu text
        menu_text = pygame.font.Font(None, 36).render("Press SPACE to Start", True, (0, 0, 0))
        screen.blit(menu_text, (SCREEN_WIDTH // 2 - menu_text.get_width() // 2, SCREEN_HEIGHT // 2))

    elif state == "playing":
        all_sprites.draw(screen)

    elif state == "game_over":
        game_over_text = pygame.font.Font(None, 36).render("Game Over!", True, (0, 0, 0))
        restart_text = pygame.font.Font(None, 36).render("Press R to Restart", True, (0, 0, 0))
        screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 20))
        screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 20))

    # Flip the display
    pygame.display.flip()
    clock.tick(60)

# Quit Pygame
pygame.quit()
