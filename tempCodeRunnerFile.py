import pygame
from PIL import Image
import random

# Initialize Pygame and Mixer
pygame.init()
pygame.mixer.init()

# Screen dimensions
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 400

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Automata Game")

# Load the background image
background = pygame.image.load("background.png").convert()
background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))

# Load music and sound effects
pygame.mixer.music.load("menumusic.mp3")  # Menu background music
jump_sound = pygame.mixer.Sound("jumpmusic.mp3")  # Jump sound effect
game_over_sound = pygame.mixer.Sound("gameovermusic.mp3")  # Game over sound effect
playing_music = "playingmusic.mp3"  # Playing background music (loaded later)

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
            jump_sound.play()  # Play jump sound effect when jumping

# Define the Obstacle class
class Obstacle(pygame.sprite.Sprite):
    def __init__(self, frames, speed):
        super().__init__()
        self.frames = frames
        self.current_frame = 0
        self.image = self.frames[self.current_frame]
        self.image = pygame.transform.scale(self.image, (45, 45))
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH + random.randint(0, 200)
        self.rect.y = random.randint(SCREEN_HEIGHT - 150, SCREEN_HEIGHT - 100)
        self.speed = speed  # Set the initial speed of the obstacle
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
obstacle_spawn_time = 120  # Initial obstacle spawn time
obstacle_speed = 10  # Initial obstacle speed
speed_increase_interval = 500  # Score interval to increase speed
MAX_OBSTACLES = 5

# Scoring system
score = 0  # Initialize score
score_font = pygame.font.Font(None, 36)  # Font for displaying the score

# Function to reset the game
def reset_game():
    global state, obstacle_spawn_timer, all_sprites, obstacles, score, obstacle_speed, obstacle_spawn_time
    state = "menu"  # Set state to menu
    obstacle_spawn_timer = 0  # Reset obstacle spawn timer
    obstacles.empty()  # Clear obstacles
    all_sprites.empty()  # Clear all sprites
    score = 0  # Reset score
    obstacle_speed = 5  # Reset obstacle speed
    obstacle_spawn_time = 120  # Reset spawn time

    # Initialize a new player and add to sprite groups
    new_player = Player()
    all_sprites.add(new_player)
    return new_player

# Initialize player
player = reset_game()

# Start menu music
pygame.mixer.music.play(-1)  # Loop menu music

# Game loop
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if state == "menu" and event.key == pygame.K_SPACE:  # Start the game
                state = "playing"
                pygame.mixer.music.stop()  # Stop menu music
                pygame.mixer.music.load(playing_music)  # Load playing music
                pygame.mixer.music.play(-1)  # Loop playing music
            elif state == "playing" and event.key == pygame.K_SPACE:  # Jump
                player.jump()
            elif state == "game_over" and event.key == pygame.K_r:  # Restart game
                game_over_sound.stop()  # Stop the game over sound effect
                player = reset_game()  # Call reset function
                pygame.mixer.music.stop()  # Stop any music
                pygame.mixer.music.load("menumusic.mp3")  # Load and play menu music again
                pygame.mixer.music.play(-1)  # Loop menu music

    if state == "playing":
        all_sprites.update()

        # Increment score over time
        score += 2

        # Check if score has reached the interval for increasing speed
        if score % speed_increase_interval == 0:
            obstacle_speed += 40 # Increase obstacle speed
            obstacle_spawn_time = max(30, obstacle_spawn_time - 10)  # Decrease spawn time (minimum 30)

        if pygame.sprite.spritecollide(player, obstacles, False):
            state = "game_over"  # Change state to game over
            pygame.mixer.music.stop()  # Stop playing music
            game_over_sound.play()  # Play game over sound

        # Manage obstacle spawning
        obstacle_spawn_timer += 1
        if obstacle_spawn_timer >= obstacle_spawn_time:
            if len(obstacles) < 2:
                new_obstacle = Obstacle(obstacle_frames, obstacle_speed)  # Pass the current obstacle speed
                obstacles.add(new_obstacle)
                all_sprites.add(new_obstacle)
            obstacle_spawn_timer = 0

    # Clear the screen
    screen.fill((255, 255, 255))

    # Draw the background
    screen.blit(background, (0, 0))

    if state == "menu":
        # Draw the game title
        title_text = pygame.font.Font(None, 48).render("Endless Escape: The Infinite Run", True, (0, 0, 0))
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, SCREEN_HEIGHT // 2 - 100))
        
        # Draw menu text below the title
        menu_text = pygame.font.Font(None, 36).render("Press SPACE to Start", True, (0, 0, 0))
        screen.blit(menu_text, (SCREEN_WIDTH // 2 - menu_text.get_width() // 2, SCREEN_HEIGHT // 2 - 30))

    elif state == "playing":
        all_sprites.draw(screen)

        # Display the score in the top-left corner
        score_text = score_font.render(f"Score: {score}", True, (0, 0, 0))
        screen.blit(score_text, (10, 10))

    elif state == "game_over":
        game_over_text = pygame.font.Font(None, 36).render("GAME OVER!", True, (255, 0, 0))
        restart_text = pygame.font.Font(None, 36).render("Press R to Restart", True, (255, 0, 0))
        screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 100))
        screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))

        # Display final score on game over screen
        final_score_text = score_font.render(f"Final Score: {score}", True, (255, 0, 0))
        screen.blit(final_score_text, (SCREEN_WIDTH // 2 - final_score_text.get_width() // 2, SCREEN_HEIGHT // 2 - 10))

    # Flip the display
    pygame.display.flip()
    clock.tick(60)

# Quit Pygame
pygame.quit()
