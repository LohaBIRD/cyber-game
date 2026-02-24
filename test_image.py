import pygame
import sys

# Initialize Pygame
try:
    pygame.init()
    # Set up a dummy display to allow image loading
    pygame.display.set_mode((1, 1))
except pygame.error as e:
    print(f"Failed to initialize Pygame: {e}")
    sys.exit(1)

# Test loading character image
try:
    character_image = pygame.image.load('trollface.jpg').convert_alpha()
    character_image = pygame.transform.scale(character_image, (20, 50))
    print("Character image loaded and scaled successfully.")
except (pygame.error, FileNotFoundError) as e:
    print(f"Failed to load character image: {e}")
    character_image = None

# Test loading background image
try:
    background = pygame.image.load('background.jpg').convert()
    print("Background image loaded successfully.")
except (pygame.error, FileNotFoundError) as e:
    print(f"Failed to load background image: {e}")
    background = None

pygame.quit()
print("Pygame quit successfully.")
