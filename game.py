import pygame
from PIL import Image
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 400

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)  # Color for hitbox

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Infinite Runner Game")

# Load the background image
background = pygame.image.load("background.png").convert()
background = pygame.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))  # Scale background to fit the screen

# Function to load GIF frames
def load_gif_frames(filename):  
    img = Image.open(filename)
    frames = []
    try:
        while True:
            # Convert each frame to a Pygame surface
            frame = img.convert("RGBA")
            frame = pygame.image.fromstring(frame.tobytes(), frame.size, "RGBA")
            frames.append(frame)
            img.seek(img.tell() + 1)  # Move to the next frame
    except EOFError:
        pass  # End of the GIF
    return frames

# Define the Player class
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.sprite_sheet = pygame.image.load("seratojeans32x32.png").convert_alpha()  # Load the sprite sheet
        self.frames = self.load_frames()  # Load the individual frames
        self.current_frame = 0  # Start at the first frame
        self.image = self.frames[self.current_frame]  # Set the initial image
        self.rect = self.image.get_rect()
        self.rect.x = 100  # Initial x position
        self.rect.y = SCREEN_HEIGHT - 100  # Initial y position
        self.is_jumping = False
        self.gravity = 1.0
        self.jump_height = -20
        self.jump_velocity = self.jump_height
        self.animation_speed = 0.1  # Speed of the animation
        self.frame_count = 0  # To control frame updates

    def load_frames(self):
        # Assuming there are 4 frames in the sprite sheet, adjust the number as necessary
        frame_width = 32  # Width of each frame
        frame_height = 32  # Height of each frame
        frames = []

        for i in range(4):  # Change 4 to the number of frames in your sprite sheet
            frame = self.sprite_sheet.subsurface(i * frame_width, 0, frame_width, frame_height)
            frames.append(pygame.transform.scale(frame, (50, 50)))  # Scale frame to desired size

        return frames

    def update(self):
        if self.is_jumping:
            self.rect.y += self.jump_velocity
            self.jump_velocity += self.gravity
            
            if self.rect.y >= SCREEN_HEIGHT - 100:  # Back to ground
                self.rect.y = SCREEN_HEIGHT - 100
                self.is_jumping = False
                self.jump_velocity = self.jump_height

        # Update the animation
        self.frame_count += self.animation_speed
        if self.frame_count >= 1:
            self.frame_count = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames)  # Cycle through frames
        self.image = self.frames[self.current_frame]  # Update the image to the current frame

    def jump(self):
        if not self.is_jumping:  # Can only jump if not already jumping
            self.is_jumping = True
            self.jump_velocity = self.jump_height  # Reset jump velocity when jumping

# Define the Obstacle class
class Obstacle(pygame.sprite.Sprite):
    def __init__(self, frames):
        super().__init__()
        self.frames = frames  # Pass frames directly
        self.current_frame = 0  # Start at the first frame
        self.image = self.frames[self.current_frame]  # Set the initial image
        
        # Set the size of the obstacle
        self.image = pygame.transform.scale(self.image, (45, 45))  # Set the obstacle size to 45x45
        self.rect = self.image.get_rect()

        self.rect.x = SCREEN_WIDTH + random.randint(0, 200)  # Random initial x position
        
        # Set a random initial y position within a specified range
        self.rect.y = random.randint(SCREEN_HEIGHT - 150, SCREEN_HEIGHT - 100)  # Random y position within the range
        self.speed = 5  # Initial speed of the obstacle
        self.animation_speed = 0.2  # Speed of the animation
        self.frame_count = 0  # To control frame updates

    def update(self):
        self.rect.x -= self.speed  # Move the obstacle to the left
        if self.rect.x < -50:  # Check if it goes off-screen
            # Reset position with a random x-coordinate and random y-coordinate within a specified range
            self.rect.x = SCREEN_WIDTH + random.randint(0, 200)  # Random x position from right side
            self.rect.y = random.randint(SCREEN_HEIGHT - 150, SCREEN_HEIGHT - 100)  # Random y position within range

        # Update the animation
        self.frame_count += self.animation_speed
        if self.frame_count >= 1:
            self.frame_count = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames)  # Cycle through frames
        self.image = self.frames[self.current_frame]  # Update the image to the current frame
        self.image = pygame.transform.scale(self.image, (45, 45))  # Ensure the size remains consistent
        
# Load obstacle frames (You can add more GIFs here)
obstacle_frames = load_gif_frames("devil.gif")

# Initialize player
player = Player()

# Create sprite groups
all_sprites = pygame.sprite.Group()
all_sprites.add(player)
obstacles = pygame.sprite.Group()  # Separate group for obstacles

# Score variable
score = 0
score_increment_rate = 30  # Increase score every 30 frames initially
frame_count = 0  # Count frames to control score increment speed
font = pygame.font.Font(None, 36)  # Default font and size

# Game loop variables
running = True
clock = pygame.time.Clock()
obstacle_spawn_timer = 0  # Timer to control obstacle spawn
obstacle_spawn_time = 120  # Time (in frames) before a new obstacle can appear
MAX_OBSTACLES = 5  # Maximum number of obstacles on the screen

# Game loop
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:  # Jump with spacebar
                player.jump()

    # Update game state
    all_sprites.update()
    
    # Check for collision between player and obstacles
    if pygame.sprite.spritecollide(player, obstacles, False):
        print("Game Over!")
        running = False

    # Increment frame count
    frame_count += 10  # You can adjust this for faster scoring

    # Increment score based on frame count
    if frame_count >= score_increment_rate:
        score += 1  # Increase score
        frame_count = 0  # Reset frame count

        # Speed up scoring mechanism and game speed every 500 points
        if score % 500 == 0 and score_increment_rate > 5:
            score_increment_rate -= 2  # Decrease increment rate (faster scoring)

    # Manage obstacle spawning
    obstacle_spawn_timer += 1
    if obstacle_spawn_timer >= obstacle_spawn_time:
        # Only spawn new obstacles if the current number is less than MAX_OBSTACLES
        if len(obstacles) < 2:
            # Spawn a new obstacle randomly
            new_obstacle = Obstacle(obstacle_frames)
            obstacles.add(new_obstacle)
            all_sprites.add(new_obstacle)
        obstacle_spawn_timer = 0  # Reset spawn timer

    # Clear the screen
    screen.fill(WHITE)

    # Draw the static background
    screen.blit(background, (0, 0))

    # Draw all sprites
    all_sprites.draw(screen)

    # Draw the hitbox of the obstacles
    #for obstacle in obstacles:
        #pygame.draw.rect(screen, RED, obstacle.rect, 2)  # Draw hitbox as a red rectangle

    # Render the score
    score_text = font.render(f"Score: {score}", True, BLACK)
    screen.blit(score_text, (10, 10))  # Draw score text at the top-left corner

    # Flip the display
    pygame.display.flip()

    # Control the frame rate
    clock.tick(60)

# Quit Pygame
pygame.quit()