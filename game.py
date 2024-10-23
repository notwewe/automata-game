import pygame
from PIL import Image
import random

pygame.init()
pygame.mixer.init()

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 400

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Automata Game")

background = pygame.image.load("background.png").convert()
background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))

pygame.mixer.music.load("menumusic.mp3") 
jump_sound = pygame.mixer.Sound("jumpmusic.mp3") 
game_over_sound = pygame.mixer.Sound("gameovermusic.mp3")  
playing_music = "playingmusic.mp3"  

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
            jump_sound.play() 

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
        self.speed = speed 
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

    def set_speed(self, speed):
        """Update the speed of the obstacle."""
        self.speed = speed

# Load obstacle frames
obstacle_frames = load_gif_frames("devil.gif")

# Create sprite groups
all_sprites = pygame.sprite.Group()
obstacles = pygame.sprite.Group()

# Game loop variables
running = True
clock = pygame.time.Clock()

# FSM Variables
state = "menu"  
obstacle_spawn_timer = 0
obstacle_spawn_time = 120  
obstacle_speed = 5 
speed_increase_interval = 1000 
MAX_OBSTACLES = 5

# Scoring system
score = 0  
score_font = pygame.font.Font(None, 36)  
speed_font = pygame.font.Font(None, 36)

# Function to reset the game
def reset_game():
    global state, obstacle_spawn_timer, all_sprites, obstacles, score, obstacle_speed, obstacle_spawn_time
    state = "menu"  
    obstacle_spawn_timer = 0  
    obstacles.empty()  
    all_sprites.empty() 
    score = 0  
    obstacle_speed = 5 
    obstacle_spawn_time = 120  

    new_player = Player()
    all_sprites.add(new_player)
    return new_player

player = reset_game()

pygame.mixer.music.play(-1)  # Loop menu music

# Game loop
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if state == "menu" and event.key == pygame.K_SPACE:  # Start the game
                state = "playing"
                pygame.mixer.music.stop()  
                pygame.mixer.music.load(playing_music)  
                pygame.mixer.music.play(-1)  
            elif state == "playing" and event.key == pygame.K_SPACE:  # Jump
                player.jump()
            elif state == "game_over" and event.key == pygame.K_r:  # Restart game
                game_over_sound.stop()  
                player = reset_game()  # Call reset function
                pygame.mixer.music.stop()  
                pygame.mixer.music.load("menumusic.mp3")  
                pygame.mixer.music.play(-1)

    if state == "playing":
        all_sprites.update()

        # Increment score over time only if the game is playing
        score += 2

        if score % speed_increase_interval == 0 and score != 0:
            obstacle_speed += 1 
            # Update the speed of all existing obstacles
            for obstacle in obstacles:
                obstacle.set_speed(obstacle_speed)

        if pygame.sprite.spritecollide(player, obstacles, False):
            state = "game_over" 
            pygame.mixer.music.stop() 
            game_over_sound.play() 

        # Manage obstacle spawning
        obstacle_spawn_timer += 1
        if obstacle_spawn_timer >= obstacle_spawn_time:
            if len(obstacles) < 2:  
                new_obstacle = Obstacle(obstacle_frames, obstacle_speed) 
                obstacles.add(new_obstacle)
                all_sprites.add(new_obstacle)
            obstacle_spawn_timer = 0

    screen.fill((255, 255, 255))

    screen.blit(background, (0, 0))

    if state == "menu":
        title_text = pygame.font.Font(None, 48).render("Endless Escape", True, (0, 0, 0))
        screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, SCREEN_HEIGHT // 2 - 100))
        
        menu_text = pygame.font.Font(None, 36).render("Press SPACE to Start", True, (0, 0, 0))
        screen.blit(menu_text, (SCREEN_WIDTH // 2 - menu_text.get_width() // 2, SCREEN_HEIGHT // 2 - 30))

    elif state == "playing":
        all_sprites.draw(screen)

        score_text = score_font.render(f"Score: {score}", True, (0, 0, 0))
        screen.blit(score_text, (10, 10))

        speed_text = speed_font.render(f"Speed: {obstacle_speed}", True, (0, 0, 0))
        screen.blit(speed_text, (10, 50))

    elif state == "game_over":
        game_over_text = pygame.font.Font(None, 36).render("GAME OVER!", True, (255, 0, 0))
        restart_text = pygame.font.Font(None, 36).render("Press R to Restart", True, (255, 0, 0))
        screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 100))
        screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))

        final_score_text = score_font.render(f"Final Score: {score}", True, (255, 0, 0))
        screen.blit(final_score_text, (SCREEN_WIDTH // 2 - final_score_text.get_width() // 2, SCREEN_HEIGHT // 2 - 10))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
