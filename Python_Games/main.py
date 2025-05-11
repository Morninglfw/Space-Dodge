# Designed by: Anthony Chipner
# Date: 05/07/2025
# Sounds are all from https://www.youtube.com/audiolibrary
# Images are from https://www.vecteezy.com/free-vector/space
# Game is a simple space dodge game where the player controls a ship and dodges asteroids and aliens.
# The player can shoot aliens after reaching level 10. The game tracks the player's score and allows them to enter their name for the top scores list.
import os
import pygame
import time
import random
import json  # For saving and loading top scores

print(f"Current working directory: {os.getcwd()}")
pygame.font.init()
pygame.mixer.init()

WIDTH, HEIGHT = 1920, 800
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
PLAYER_WIDTH, PLAYER_HEIGHT = 40, 60
LEVEL = 1
PLAYER_VEL = 5
STAR_WIDTH = 50
STAR_HEIGHT = 30
STAR_VEL = 3
FONT = pygame.font.SysFont("comicsans", 30)
pygame.display.set_caption("Space Dodge")

# Add after other constants
LASER_WIDTH = 30  # Increased from 20
LASER_HEIGHT = 75  # Increased from 50
LASER_VEL = 7
LASER_COOLDOWN = 500  # milliseconds between shots

def load_image(path, fallback_color=(255, 0, 0)):
    """Load an image and return a fallback surface if the file is missing."""
    try:
        return pygame.image.load(path).convert_alpha()
    except FileNotFoundError:
        print(f"Error: File '{path}' not found. Using fallback color.")
        surface = pygame.Surface((50, 50), pygame.SRCALPHA)
        surface.fill(fallback_color)
        return surface

# Load images with error handling
BG = pygame.transform.scale(load_image("images/Spacebg.jpg"), (WIDTH, HEIGHT))  # Use spacebg.jpg as the background
SH = load_image("images/spacecraft.png") # Ship with transparency
MS = load_image("images/asteroid.png")  # Asteroid with transparency
BG_LAYER_1 = pygame.transform.scale(load_image("images/Spacebg.jpg"), (WIDTH, HEIGHT))  # Parallax layer 1
BG_LAYER_2 = pygame.transform.scale(load_image("images/Spacebg.jpg"), (WIDTH, HEIGHT))  # Parallax layer 2
# Load alien image
ALIEN_IMG = pygame.transform.scale(load_image("images/Aliens.png", fallback_color=(255, 0, 0)), (STAR_WIDTH, STAR_HEIGHT))  # Same size as asteroids

# Add after other image loading
LASER_IMG = pygame.transform.scale(load_image("images/LaserShot.gif"), (LASER_WIDTH, LASER_HEIGHT))
LASER_SOUND = "Sounds/Laser Gun.mp3"

# Load explosion image and sound
EXPLOSION_IMG = pygame.transform.scale(load_image("images/vecteezy_explosion-with-pixel-art-vector-illustration_8202202.png"), (100, 100))
EXPLOSION_SOUND = "Sounds/Big Explosion Cut Off.mp3"

TOP_SCORES_FILE = "top_scores.json"

def load_top_scores():
    try:
        with open(TOP_SCORES_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def save_top_scores(top_scores):
    with open(TOP_SCORES_FILE, "w") as file:
        json.dump(top_scores, file)

def get_player_name():
    """Custom function to get the player's name using pygame."""
    name = ""
    run = True
    while run:
        WIN.fill((0, 0, 0))  # Clear the screen
        prompt_text = FONT.render("New high score! Enter your name:", 1, ("White"))
        name_text = FONT.render(name, 1, ("White"))
        WIN.blit(prompt_text, (WIDTH // 2 - prompt_text.get_width() // 2, HEIGHT // 2 - 50))
        WIN.blit(name_text, (WIDTH // 2 - name_text.get_width() // 2, HEIGHT // 2))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:  # Press Enter to confirm
                    run = False
                elif event.key == pygame.K_BACKSPACE:  # Press Backspace to delete a character
                    name = name[:-1]
                else:
                    name += event.unicode  # Add the typed character to the name
    return name

def update_top_scores(score):  # Changed parameter from elapsed_time to score
    top_scores = load_top_scores()
    if len(top_scores) < 5 or score > min(score["score"] for score in top_scores):
        name = get_player_name()
        top_scores.append({"name": name, "score": score})  # Store the actual score
        top_scores = sorted(top_scores, key=lambda x: x["score"], reverse=True)[:5]
        save_top_scores(top_scores)
        print("Top Scores:")
        for score in top_scores:
            print(f"{score['name']}: {score['score']} points")  # Changed display text

def draw_background(scroll_y1, scroll_y2):
    # Parallax scrolling effect
    WIN.blit(BG_LAYER_1, (0, scroll_y1 % HEIGHT))
    WIN.blit(BG_LAYER_1, (0, (scroll_y1 % HEIGHT) - HEIGHT))
    WIN.blit(BG_LAYER_2, (0, scroll_y2 % HEIGHT))
    WIN.blit(BG_LAYER_2, (0, (scroll_y2 % HEIGHT) - HEIGHT))

def draw(player, elapsed_time, stars, aliens, LEVEL, score):
    WIN.blit(BG, (0, 0))

    # Score text (simplified, just show total score)
    score_text = FONT.render(f"Score: {score}", 1, ("White"))
    WIN.blit(score_text, (10, 10))

    # Time text (below score)
    time_text = FONT.render(f"Time: {round(elapsed_time)}s", 1, ("White"))
    WIN.blit(time_text, (10, 40))

    # Level text (top right)
    level_text = FONT.render(f"Level: {LEVEL}", 1, ("White"))
    WIN.blit(level_text, (WIDTH - level_text.get_width() - 10, 10))

    # Draw the player and its lasers
    player.draw(WIN)  # This will draw both the player and lasers

    # Draw asteroids
    for star in stars:
        scaled_star = pygame.transform.scale(MS, (STAR_WIDTH, STAR_HEIGHT))
        WIN.blit(scaled_star, (star.x, star.y))

    # Draw aliens
    for alien in aliens:
        WIN.blit(ALIEN_IMG, (alien.x, alien.y))

    pygame.display.update()

class Background:
    def __init__(self, image_path):
        self.image = pygame.transform.scale(pygame.image.load(image_path), (WIDTH, HEIGHT))
        self.scroll_y1 = 0
        self.scroll_y2 = -HEIGHT

    def update(self):
        self.scroll_y1 += 1
        self.scroll_y2 += 1
        if self.scroll_y1 >= HEIGHT:
            self.scroll_y1 = -HEIGHT
        if self.scroll_y2 >= HEIGHT:
            self.scroll_y2 = -HEIGHT

    def draw(self, window):
        window.blit(self.image, (0, self.scroll_y1))
        window.blit(self.image, (0, self.scroll_y2))

class Player:
    def __init__(self, x, y, width, height, image_path):
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.transform.scale(pygame.image.load(image_path), (width, height))
        self.lasers = []
        self.last_shot = 0
        self.forward_movement_enabled = False  # Add this line

    def move(self, keys):
        if keys[pygame.K_a] and self.rect.x - PLAYER_VEL >= 0:
            self.rect.x -= PLAYER_VEL
        if keys[pygame.K_d] and self.rect.x + PLAYER_VEL <= WIDTH - PLAYER_WIDTH:
            self.rect.x += PLAYER_VEL
        # Only allow forward/backward movement if enabled
        if self.forward_movement_enabled:
            if keys[pygame.K_w] and self.rect.y - PLAYER_VEL >= 0:
                self.rect.y -= PLAYER_VEL
            if keys[pygame.K_s] and self.rect.y + PLAYER_VEL <= HEIGHT - PLAYER_HEIGHT:
                self.rect.y += PLAYER_VEL

    def shoot(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_shot >= LASER_COOLDOWN:
            laser = Laser(
                self.rect.centerx - LASER_WIDTH//2,  # Center the laser on the ship
                self.rect.y  # Start from the top of the ship
            )
            self.lasers.append(laser)
            self.last_shot = current_time
            try:
                laser_sound = pygame.mixer.Sound(LASER_SOUND)
                laser_sound.set_volume(0.3)  # Adjust volume as needed
                laser_sound.play()
            except:
                print("Could not play laser sound")

    def update_lasers(self):
        for laser in self.lasers[:]:
            laser.move()
            if laser.rect.bottom < 0:
                self.lasers.remove(laser)

    def draw(self, window):
        window.blit(self.image, (self.rect.x, self.rect.y))
        # Draw all active lasers
        for laser in self.lasers:
            laser.draw(window)

class Alien:
    def __init__(self, x, y, width, height, image_path):
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.transform.scale(pygame.image.load(image_path), (width, height))

    def move(self):
        self.rect.y += STAR_VEL

    def draw(self, window):
        window.blit(self.image, (self.rect.x, self.rect.y))

class Asteroid:
    def __init__(self, x, y, width, height, image_path):
        self.rect = pygame.Rect(x, y, width, height)
        self.image = pygame.transform.scale(pygame.image.load(image_path), (width, height))

    def move(self):
        self.rect.y += STAR_VEL

    def draw(self, window):
        window.blit(self.image, (self.rect.x, self.rect.y))

class Laser:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, LASER_WIDTH, LASER_HEIGHT)
        self.image = LASER_IMG

    def move(self):
        self.rect.y -= LASER_VEL

    def draw(self, window):
        window.blit(self.image, (self.rect.x, self.rect.y))

class Game:
    def __init__(self):
        self.background = Background("images/Spacebg.jpg")
        self.player = Player(200, HEIGHT - PLAYER_HEIGHT, PLAYER_WIDTH, PLAYER_HEIGHT, "images/spacecraft.png")
        self.aliens = []
        self.asteroids = []
        self.clock = pygame.time.Clock()  # Changed from pygame.Clock()
        self.run = True
        self.level = 1
        self.score = 0
        self.start_time = time.time()
        self.alien_spawn_time = time.time()  # Track time for alien spawning

    def spawn_asteroid(self):
        x = random.randint(0, WIDTH - STAR_WIDTH)
        asteroid = Asteroid(x, -STAR_HEIGHT, STAR_WIDTH, STAR_HEIGHT, "images/asteroid.png")
        self.asteroids.append(asteroid)

    def spawn_alien(self):
        x = random.randint(0, WIDTH - STAR_WIDTH)
        alien = Alien(x, -STAR_HEIGHT, STAR_WIDTH, STAR_HEIGHT, "images/Aliens.png")
        print(f"Spawning alien at x={x}, y={-STAR_HEIGHT}")  # Debugging output
        self.aliens.append(alien)

    def update(self):
        keys = pygame.key.get_pressed()
        self.player.move(keys)

        # Handle shooting when space is pressed and level is 10 or higher
        if LEVEL >= 10 and keys[pygame.K_SPACE]:
            self.player.shoot()

        # Update lasers and check for collisions with aliens
        self.player.update_lasers()
        for laser in self.player.lasers[:]:
            for alien in self.aliens[:]:
                if laser.rect.colliderect(alien):
                    # Calculate explosion position at the alien's location
                    explosion_x = alien.rect.x + STAR_WIDTH // 2 - EXPLOSION_IMG.get_width() // 2
                    explosion_y = alien.rect.y + STAR_HEIGHT // 2 - EXPLOSION_IMG.get_height() // 2
                    
                    # Remove alien and laser
                    self.aliens.remove(alien)
                    self.player.lasers.remove(laser)
                    self.score += 1
                    
                    # Show explosion effect
                    WIN.blit(EXPLOSION_IMG, (explosion_x, explosion_y))
                    pygame.display.update()
                    
                    # Play explosion sound
                    try:
                        explosion_sound = pygame.mixer.Sound(EXPLOSION_SOUND)
                        explosion_sound.set_volume(0.3)
                        explosion_sound.play()
                    except:
                        print("Could not play explosion sound")
                        
                    # Increased delay to make explosion more visible
                    pygame.time.delay(100)  # Increased from 50ms to 100ms
                    break

        # Update asteroids
        for asteroid in self.asteroids[:]:
            asteroid.move()
            if asteroid.rect.y > HEIGHT:
                self.asteroids.remove(asteroid)

        # Update aliens
        for alien in self.aliens[:]:
            alien.move()
            if alien.rect.y > HEIGHT:
                self.aliens.remove(alien)

        # Spawn new asteroids and aliens at intervals
        if time.time() - self.start_time > 3:
            self.spawn_asteroid()
            self.start_time = time.time()

        if time.time() - self.alien_spawn_time > 2:  # Spawn aliens every 2 seconds
            self.spawn_alien()
            self.alien_spawn_time = time.time()

        # Debugging: Print the number of aliens
        print(f"Number of aliens: {len(self.aliens)}")

    def draw(self):
        # Draw background first
        self.background.draw(WIN)

        # Draw asteroids (or stars)
        for asteroid in self.asteroids:
            asteroid.draw(WIN)

        # Draw aliens
        for alien in self.aliens:
            alien.draw(WIN)

        # Draw player
        self.player.draw(WIN)

        # Draw score
        score_text = FONT.render(f"Score: {self.score}", 1, ("White"))
        WIN.blit(score_text, (10, 10))

        # Draw laser instruction message when level is 10
        if LEVEL == 10:
            instruction_text = FONT.render("Press SPACE to shoot aliens! +10 points per hit!", 1, ("Yellow"))
            WIN.blit(instruction_text, (WIDTH // 2 - instruction_text.get_width() // 2, 50))

        # Draw level message
        level_text = FONT.render(f"Level: {LEVEL}", 1, ("White"))
        WIN.blit(level_text, (WIDTH - level_text.get_width() - 10, 10))

        pygame.display.update()

    def run_game(self):
        while self.run:
            self.clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.run = False

            self.update()  # Update game state
            self.draw()    # Draw everything

def main():
    global LEVEL, STAR_VEL, BG

    # Reset game variables
    LEVEL = 1  
    STAR_VEL = 3

    pygame.mixer.music.load("Sounds/Sun Machine One - Loopop.mp3")
    pygame.mixer.music.play(-1)

    run = True
    # Create a Player instance instead of a Rect
    player = Player(200, HEIGHT - PLAYER_HEIGHT, PLAYER_WIDTH, PLAYER_HEIGHT, "images/spacecraft.png")

    clock = pygame.time.Clock()
    start_time = time.time()
    elapsed_time = 0
    score = 0
    base_score = 0  # Track time-based score separately

    star_add_increment = 2000
    star_count = 0
    stars = []
    aliens = []  # List to store aliens
    alien_spawn_time = 0  # Track time for alien spawning
    hit = False

    scroll_y1 = 0
    scroll_y2 = 0

    level_5_message_shown = False  # Track if the level 5 message has been displayed

    while run:
        scroll_y1 += 1  # Slow scroll for layer 1
        scroll_y2 += 2  # Faster scroll for layer 2

        star_count += clock.tick(60)
        elapsed_time = time.time() - start_time

        # Update base score every 10 seconds
        time_points = int(elapsed_time) // 10  # 1 point for every 10 seconds
        if time_points > base_score:  # Only update when a new 10-second interval is reached
            score += (time_points - base_score)  # Add only the new points
            base_score = time_points  # Update the base score

        # Spawn stars
        if star_count >= star_add_increment:
            for _ in range(3):
                star_x = random.randint(0, WIDTH - STAR_WIDTH)
                star = pygame.Rect(star_x, -STAR_HEIGHT, STAR_WIDTH, STAR_HEIGHT)
                stars.append(star)
            star_add_increment = max(200, star_add_increment - 50)
            star_count = 0

        # Spawn aliens starting at level 10
        if LEVEL >= 10 and time.time() - alien_spawn_time >= 3:  # Spawn every 3 seconds
            alien_x = random.randint(0, WIDTH - STAR_WIDTH)
            alien = pygame.Rect(alien_x, -STAR_HEIGHT, STAR_WIDTH, STAR_HEIGHT)
            aliens.append(alien)
            alien_spawn_time = time.time()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

        keys = pygame.key.get_pressed()
        player.move(keys)  # Use the Player's move method

        # Handle shooting
        if LEVEL >= 10 and keys[pygame.K_SPACE]:
            player.shoot()

        # Update lasers
        player.update_lasers()

        # Check laser collisions with aliens
        for laser in player.lasers[:]:
            for alien in aliens[:]:
                if laser.rect.colliderect(alien):
                    # Calculate explosion position at the alien's location
                    explosion_x = alien.x + STAR_WIDTH // 2 - EXPLOSION_IMG.get_width() // 2
                    explosion_y = alien.y + STAR_HEIGHT // 2 - EXPLOSION_IMG.get_height() // 2
                    
                    # Remove alien and laser
                    aliens.remove(alien)
                    player.lasers.remove(laser)
                    score += 1
                    
                    # Show explosion effect
                    WIN.blit(EXPLOSION_IMG, (explosion_x, explosion_y))
                    pygame.display.update()
                    
                    # Play explosion sound
                    try:
                        explosion_sound = pygame.mixer.Sound(EXPLOSION_SOUND)
                        explosion_sound.set_volume(0.3)
                        explosion_sound.play()
                    except:
                        print("Could not play explosion sound")
                        
                    # Small delay to make explosion visible
                    pygame.time.delay(50)  # 50ms delay, adjust if needed
                    break

        draw_background(scroll_y1, scroll_y2)
        draw(player, elapsed_time, stars, aliens, LEVEL, score)  # Pass the updated score

        # Update stars
        for star in stars[:]:
            star.y += STAR_VEL
            if star.y > HEIGHT:
                stars.remove(star)
            elif star.y + star.height >= player.rect.y and star.colliderect(player.rect):
                stars.remove(star)
                hit = True
                break

        # Update aliens
        for alien in aliens[:]:
            alien.y += STAR_VEL  # Aliens move at the same speed as stars
            if alien.y > HEIGHT:
                aliens.remove(alien)
            elif alien.colliderect(player.rect):
                aliens.remove(alien)
                hit = True
                break

        # Draw aliens
        for alien in aliens:
            WIN.blit(ALIEN_IMG, (alien.x, alien.y))

        if hit:
            # Play explosion sound
            pygame.mixer.Sound(EXPLOSION_SOUND).play()

            # Display explosion image
            WIN.blit(EXPLOSION_IMG, (player.rect.x + PLAYER_WIDTH // 2 - EXPLOSION_IMG.get_width() // 2,
                                     player.rect.y + PLAYER_HEIGHT // 2 - EXPLOSION_IMG.get_height() // 2))
            pygame.display.update()
            pygame.time.delay(1000)  # Show explosion for 1 second

            lost_text = FONT.render("You lost!", 1, ("Red"))
            WIN.blit(lost_text, (WIDTH // 2 - lost_text.get_width() // 2, HEIGHT // 2 - lost_text.get_height() // 2))
            pygame.display.update()
            pygame.time.delay(2000)

            # Check if the score is a top score
            update_top_scores(score)  # Update this line to pass score instead of elapsed_time

            # Ask if the player wants to play again
            play_again = ask_play_again()
            if play_again:
                main()  # Restart the game
            else:
                menu()  # Return to the main menu
            return  # Exit the current game loop

        if int(elapsed_time) // 10 + 1 > LEVEL:
            LEVEL += 1
            if LEVEL == 10:
                # Show message about new shooting ability
                shoot_text = FONT.render("Level 10! Press SPACE to shoot aliens!", 1, ("Yellow"))
                WIN.blit(shoot_text, (WIDTH // 2 - shoot_text.get_width() // 2, HEIGHT // 2 - 100))
                pygame.display.update()
                pygame.time.delay(3000)  # Display for 3 seconds
            if LEVEL < 5:
                STAR_VEL += 1
            else:
                STAR_VEL += 0.5

        if LEVEL >= 5 and not level_5_message_shown:
            # Show congratulatory message at level 5
            congrats_text = FONT.render("Level 5! You can now move forward and backward!", 1, ("Yellow"))
            WIN.blit(congrats_text, (WIDTH // 2 - congrats_text.get_width() // 2, HEIGHT // 2 - 100))
            pygame.display.update()
            pygame.time.delay(3000)  # Display for 3 seconds
            level_5_message_shown = True
            player.forward_movement_enabled = True  # Enable forward movement ability

    pygame.quit()

def ask_play_again():
    """Ask the player if they want to play again or return to the main menu."""
    run = True
    while run:
        WIN.fill((0, 0, 0))  # Clear the screen
        prompt_text = FONT.render("Play again? (Y/N)", 1, ("White"))
        WIN.blit(prompt_text, (WIDTH // 2 - prompt_text.get_width() // 2, HEIGHT // 2))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_y:  # Press 'Y' to play again
                    return True
                elif event.key == pygame.K_n:  # Press 'N' to return to the main menu
                    return False

def display_top_scores():
    WIN.fill((0, 0, 0))  # Clear the screen with a black background
    top_scores = load_top_scores()
    title_text = FONT.render("Top Scores", 1, ("White"))
    WIN.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 50))

    if not top_scores:
        no_scores_text = FONT.render("No scores yet!", 1, ("White"))
        WIN.blit(no_scores_text, (WIDTH // 2 - no_scores_text.get_width() // 2, 150))
    else:
        for i, score in enumerate(top_scores):
            score_text = FONT.render(f"{i + 1}. {score['name']}: {score['score']}s", 1, ("White"))
            WIN.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 150 + i * 40))

    pygame.display.update()
    pygame.time.delay(3000)  # Display for 3 seconds

def draw_button(surface, rect, color, text, text_color, font, border_radius=10, shadow_offset=4):
    """Draws a button with rounded corners and shadow."""
    shadow_color = (50, 50, 50)  # Shadow color
    shadow_rect = rect.move(shadow_offset, shadow_offset)  # Offset for shadow
    pygame.draw.rect(surface, shadow_color, shadow_rect, border_radius=border_radius)  # Draw shadow
    pygame.draw.rect(surface, color, rect, border_radius=border_radius)  # Draw button
    text_surface = font.render(text, True, text_color)
    surface.blit(text_surface, (rect.x + rect.width // 2 - text_surface.get_width() // 2,
                                rect.y + rect.height // 2 - text_surface.get_height() // 2))

def menu():
    # Initialize the mixer and load the background music
    pygame.mixer.init()
    pygame.mixer.music.load("Sounds/Badlands - ELPHNT.mp3")  # Ensure the file is in the same directory or provide the full path
    pygame.mixer.music.play(-1)  # Play the music in a loop
    volume = 0.5  # Default volume (50%)
    pygame.mixer.music.set_volume(volume)

    run = True
    while run:
        WIN.fill((30, 30, 30))  # Dark gray background
        title_font = pygame.font.SysFont("comicsans", 50)
        button_font = pygame.font.SysFont("comicsans", 30)

        # Title
        title_text = title_font.render("Space Dodge", True, ("White"))
        WIN.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 50))

        # Define button properties
        play_button = pygame.Rect(WIDTH // 2 - 100, 150, 200, 50)
        scores_button = pygame.Rect(WIDTH // 2 - 100, 220, 200, 50)
        options_button = pygame.Rect(WIDTH // 2 - 100, 290, 200, 50)
        exit_button = pygame.Rect(WIDTH // 2 - 100, 360, 200, 50)

        # Draw buttons with shadows and rounded corners
        draw_button(WIN, play_button, (70, 130, 180), "Play", ("White"), button_font)  # Steel blue
        draw_button(WIN, scores_button, (34, 139, 34), "Top Scores", ("White"), button_font)  # Forest green
        draw_button(WIN, options_button, (255, 165, 0), "Options", ("White"), button_font)  # Orange
        draw_button(WIN, exit_button, (178, 34, 34), "Exit", ("White"), button_font)  # Firebrick red

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    mouse_pos = pygame.mouse.get_pos()
                    if play_button.collidepoint(mouse_pos):
                        pygame.mixer.music.stop()  # Stop the music when the play button is pressed
                        main()  # Start the game
                    elif scores_button.collidepoint(mouse_pos):
                        display_top_scores()  # Show top scores
                    elif options_button.collidepoint(mouse_pos):
                        options_menu(volume)  # Open the options menu
                    elif exit_button.collidepoint(mouse_pos):
                        run = False
                        pygame.quit()
                        return

def options_menu(volume):
    """Options menu for controlling volume."""
    run = True
    while run:
        WIN.fill((30, 30, 30))  # Dark gray background
        title_font = pygame.font.SysFont("comicsans", 50)
        button_font = pygame.font.SysFont("comicsans", 30)

        # Title
        title_text = title_font.render("Options", True, ("White"))
        WIN.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 50))

        # Volume controls
        volume_text = button_font.render(f"Volume: {int(volume * 100)}%", True, ("White"))
        WIN.blit(volume_text, (WIDTH // 2 - volume_text.get_width() // 2, 150))

        volume_increase_button = pygame.Rect(WIDTH // 2 + 110, 150, 40, 40)
        volume_decrease_button = pygame.Rect(WIDTH // 2 - 150, 150, 40, 40)
        mute_button = pygame.Rect(WIDTH // 2 - 50, 220, 100, 50)
        back_button = pygame.Rect(WIDTH // 2 - 100, 300, 200, 50)

        draw_button(WIN, volume_increase_button, (70, 130, 180), "+", ("White"), button_font)
        draw_button(WIN, volume_decrease_button, (70, 130, 180), "-", ("White"), button_font)
        draw_button(WIN, mute_button, (178, 34, 34), "Mute", ("White"), button_font)
        draw_button(WIN, back_button, (70, 130, 180), "Back", ("White"), button_font)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    mouse_pos = pygame.mouse.get_pos()
                    if volume_increase_button.collidepoint(mouse_pos):
                        volume = min(1.0, volume + 0.05)  # Increase volume by 5%, max is 100%
                        pygame.mixer.music.set_volume(volume)
                    elif volume_decrease_button.collidepoint(mouse_pos):
                        volume = max(0.0, volume - 0.05)  # Decrease volume by 5%, min is 0%
                        pygame.mixer.music.set_volume(volume)
                    elif mute_button.collidepoint(mouse_pos):
                        volume = 0.0  # Mute the sound
                        pygame.mixer.music.set_volume(volume)
                    elif back_button.collidepoint(mouse_pos):
                        run = False  # Return to the main menu

if __name__ == "__main__":
    print("Initializing game...")
    pygame.init()

    try:
        menu()
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        pygame.quit()
