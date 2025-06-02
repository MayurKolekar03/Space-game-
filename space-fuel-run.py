
"""
Space Fuel Run - A simple 2D side-scrolling space game
"""
import pygame
import random
import sys
import os
import math

# Initialize pygame
pygame.init()
pygame.mixer.init()

# Game constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
TITLE = "Space Fuel Run"

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (50, 50, 50)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

class GameObject:
    """Base class for all game objects"""
    def __init__(self, x, y, width, height, speed):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.speed = speed
        self.rect = pygame.Rect(x, y, width, height)
    
    def update(self):
        """Update the object's position and rect"""
        self.rect.x = self.x
        self.rect.y = self.y
    
    def draw(self, screen):
        """Draw the object on the screen"""
        pass

class Player(GameObject):
    """Player rocket class"""
    def __init__(self, x, y):
        super().__init__(x, y, 50, 30, 0)
        self.vertical_speed = 5
        self.tilt = 0  # Tilt angle in degrees
        self.max_tilt = 15  # Maximum tilt angle
        self.tilt_speed = 2  # How quickly the rocket tilts
        self.moving_up = False
        self.moving_down = False
    
    def update(self):
        """Update player position based on input"""
        # Reset tilt if not moving
        if not self.moving_up and not self.moving_down:
            if self.tilt > 0:
                self.tilt -= self.tilt_speed
            elif self.tilt < 0:
                self.tilt += self.tilt_speed
        
        # Handle keyboard input
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            self.y -= self.vertical_speed
            self.moving_up = True
            self.moving_down = False
            # Tilt up (negative angle)
            self.tilt = max(self.tilt - self.tilt_speed, -self.max_tilt)
        elif keys[pygame.K_DOWN]:
            self.y += self.vertical_speed
            self.moving_down = True
            self.moving_up = False
            # Tilt down (positive angle)
            self.tilt = min(self.tilt + self.tilt_speed, self.max_tilt)
        else:
            self.moving_up = False
            self.moving_down = False
        
        # Keep player within screen bounds
        if self.y < 0:
            self.y = 0
        elif self.y > SCREEN_HEIGHT - self.height:
            self.y = SCREEN_HEIGHT - self.height
        
        # Update rect position
        super().update()
    
    def draw(self, screen):
        """Draw the rocket with tilt effect"""
        # Create a simple rocket shape
        rocket_points = [
            (self.x, self.y + self.height // 2),  # Nose
            (self.x + self.width - 10, self.y),  # Top back
            (self.x + self.width, self.y + self.height // 2),  # Back
            (self.x + self.width - 10, self.y + self.height)  # Bottom back
        ]
        
        # Create a surface for the rocket
        rocket_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.polygon(rocket_surf, RED, [(p[0] - self.x, p[1] - self.y) for p in rocket_points])
        
        # Add a window
        window_pos = (self.width - 25, self.height // 2 - 5)
        pygame.draw.circle(rocket_surf, BLUE, window_pos, 8)
        
        # Add flames at the back
        flame_points = [
            (5, self.height // 2 - 10),
            (0, self.height // 2),
            (5, self.height // 2 + 10)
        ]
        pygame.draw.polygon(rocket_surf, YELLOW, flame_points)
        
        # Rotate the rocket based on tilt
        rotated_rocket = pygame.transform.rotate(rocket_surf, -self.tilt)  # Negative because pygame rotates clockwise
        
        # Get the rect of the rotated surface
        rotated_rect = rotated_rocket.get_rect(center=(self.x + self.width // 2, self.y + self.height // 2))
        
        # Draw the rotated rocket
        screen.blit(rotated_rocket, rotated_rect.topleft)

class Fuel(GameObject):
    """Fuel cell class"""
    def __init__(self, speed):
        # Start off-screen to the right
        super().__init__(
            SCREEN_WIDTH, 
            random.randint(50, SCREEN_HEIGHT - 50),
            30, 30, speed
        )
    
    def update(self):
        """Move the fuel cell from right to left"""
        self.x -= self.speed
        super().update()
    
    def draw(self, screen):
        """Draw the fuel cell"""
        # Draw a simple fuel cell
        pygame.draw.rect(screen, YELLOW, self.rect)
        # Add some details to make it look like a fuel cell
        pygame.draw.rect(screen, BLACK, (self.x + 5, self.y + 5, 20, 20))
        pygame.draw.rect(screen, YELLOW, (self.x + 10, self.y - 5, 10, 5))

class Asteroid(GameObject):
    """Asteroid class"""
    def __init__(self, speed):
        # Start off-screen to the right
        size = random.randint(20, 50)  # Random asteroid size
        super().__init__(
            SCREEN_WIDTH,
            random.randint(50, SCREEN_HEIGHT - 50),
            size, size, speed
        )
        self.rotation = 0
        self.rotation_speed = random.uniform(-2, 2)  # Random rotation speed
    
    def update(self):
        """Move the asteroid from right to left"""
        self.x -= self.speed
        self.rotation = (self.rotation + self.rotation_speed) % 360
        super().update()
    
    def draw(self, screen):
        """Draw the asteroid with rotation"""
        # Create a surface for the asteroid
        asteroid_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Draw a circle as the base
        pygame.draw.circle(asteroid_surf, GRAY, (self.width // 2, self.height // 2), self.width // 2)
        
        # Add some craters
        for _ in range(3):
            crater_x = random.randint(5, self.width - 5)
            crater_y = random.randint(5, self.height - 5)
            crater_size = random.randint(3, 8)
            pygame.draw.circle(asteroid_surf, BLACK, (crater_x, crater_y), crater_size)
        
        # Rotate the asteroid
        rotated_asteroid = pygame.transform.rotate(asteroid_surf, self.rotation)
        
        # Get the rect of the rotated surface
        rotated_rect = rotated_asteroid.get_rect(center=(self.x + self.width // 2, self.y + self.height // 2))
        
        # Draw the rotated asteroid
        screen.blit(rotated_asteroid, rotated_rect.topleft)

class Star:
    """Background star for parallax effect"""
    def __init__(self):
        self.x = random.randint(0, SCREEN_WIDTH)
        self.y = random.randint(0, SCREEN_HEIGHT)
        self.size = random.randint(1, 3)
        self.speed = random.uniform(0.5, 2.0)
    
    def update(self):
        """Move the star from right to left"""
        self.x -= self.speed
        if self.x < 0:
            self.x = SCREEN_WIDTH
            self.y = random.randint(0, SCREEN_HEIGHT)
    
    def draw(self, screen):
        """Draw the star"""
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.size)

class Game:
    """Main game class"""
    def __init__(self):
        # Set up the display
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        
        # Game state
        self.running = True
        self.game_active = False
        self.score = 0
        self.base_speed = 3
        self.current_speed = self.base_speed
        
        # Create game objects
        self.player = Player(100, SCREEN_HEIGHT // 2)
        self.fuels = []
        self.asteroids = []
        self.stars = [Star() for _ in range(100)]  # Create background stars
        
        # Timing variables
        self.last_fuel_time = 0
        self.last_asteroid_time = 0
        self.fuel_interval = 2000  # milliseconds
        self.asteroid_interval = 1500  # milliseconds
        
        # Load sounds
        self.load_sounds()
        
        # Font for text
        self.font = pygame.font.SysFont(None, 36)
        self.title_font = pygame.font.SysFont(None, 72)
    
    def load_sounds(self):
        """Load game sounds or create placeholders"""
        try:
            # Try to load actual sound files if they exist
            self.fuel_sound = pygame.mixer.Sound("fuel_collect.wav")
            self.crash_sound = pygame.mixer.Sound("crash.wav")
        except:
            # Create silent sounds as placeholders
            self.fuel_sound = pygame.mixer.Sound(buffer=bytes([0] * 44))
            self.crash_sound = pygame.mixer.Sound(buffer=bytes([0] * 44))
            print("Using placeholder sounds. Add sound files for actual effects.")
    
    def handle_events(self):
        """Handle game events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_SPACE and not self.game_active:
                    self.start_game()
    
    def start_game(self):
        """Start a new game"""
        self.game_active = True
        self.score = 0
        self.current_speed = self.base_speed
        self.player = Player(100, SCREEN_HEIGHT // 2)
        self.fuels = []
        self.asteroids = []
        self.last_fuel_time = pygame.time.get_ticks()
        self.last_asteroid_time = pygame.time.get_ticks()
    
    def spawn_objects(self):
        """Spawn fuel cells and asteroids at intervals"""
        current_time = pygame.time.get_ticks()
        
        # Spawn fuel cells
        if current_time - self.last_fuel_time > self.fuel_interval:
            self.fuels.append(Fuel(self.current_speed))
            self.last_fuel_time = current_time
        
        # Spawn asteroids
        if current_time - self.last_asteroid_time > self.asteroid_interval:
            self.asteroids.append(Asteroid(self.current_speed * 1.2))  # Asteroids move slightly faster
            self.last_asteroid_time = current_time
    
    def update(self):
        """Update game state"""
        if not self.game_active:
            return
        
        # Update player
        self.player.update()
        
        # Spawn new objects
        self.spawn_objects()
        
        # Update stars (background)
        for star in self.stars:
            star.update()
        
        # Update fuel cells
        for fuel in self.fuels[:]:
            fuel.update()
            # Check for collision with player
            if self.player.rect.colliderect(fuel.rect):
                self.fuels.remove(fuel)
                self.score += 1
                self.fuel_sound.play()
                # Increase speed based on score
                self.current_speed = self.base_speed + (self.score * 0.1)
            # Remove if off-screen
            elif fuel.x < -fuel.width:
                self.fuels.remove(fuel)
        
        # Update asteroids
        for asteroid in self.asteroids[:]:
            asteroid.update()
            # Check for collision with player
            if self.player.rect.colliderect(asteroid.rect):
                self.game_active = False
                self.crash_sound.play()
            # Remove if off-screen
            elif asteroid.x < -asteroid.width:
                self.asteroids.remove(asteroid)
    
    def draw(self):
        """Draw everything to the screen"""
        # Fill the background
        self.screen.fill(BLACK)
        
        # Draw stars
        for star in self.stars:
            star.draw(self.screen)
        
        if self.game_active:
            # Draw player
            self.player.draw(self.screen)
            
            # Draw fuel cells
            for fuel in self.fuels:
                fuel.draw(self.screen)
            
            # Draw asteroids
            for asteroid in self.asteroids:
                asteroid.draw(self.screen)
            
            # Draw score
            score_text = self.font.render(f"Score: {self.score}", True, WHITE)
            self.screen.blit(score_text, (20, 20))
        else:
            # Draw start/game over screen
            if self.score == 0:
                # Start screen
                title_text = self.title_font.render("Space Fuel Run", True, WHITE)
                start_text = self.font.render("Press SPACE to start", True, WHITE)
                
                self.screen.blit(title_text, (SCREEN_WIDTH // 2 - title_text.get_width() // 2, 200))
                self.screen.blit(start_text, (SCREEN_WIDTH // 2 - start_text.get_width() // 2, 300))
            else:
                # Game over screen
                game_over_text = self.title_font.render("Game Over", True, WHITE)
                score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
                restart_text = self.font.render("Press SPACE to restart", True, WHITE)
                
                self.screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, 200))
                self.screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 300))
                self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, 350))
        
        # Update the display
        pygame.display.flip()
    
    def run(self):
        """Main game loop"""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        pygame.quit()
        sys.exit()

# Run the game if this script is executed
if __name__ == "__main__":
    game = Game()
    game.run()
