import pygame
import random

class Particle:
    """A single particle for visual effects."""
    def __init__(self, x, y, dx, dy, size, color, lifespan):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.size = size
        self.color = color
        self.lifespan = lifespan

    def update(self):
        """Update the particle's position and lifespan."""
        self.x += self.dx
        self.y += self.dy
        self.lifespan -= 1
        self.size -= 0.1
        if self.size < 0:
            self.size = 0

    def draw(self, surface):
        """Draw the particle on the screen."""
        if self.lifespan > 0 and self.size > 0:
            pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), int(self.size))

class TextParticle(Particle):
    """A particle that displays text."""
    def __init__(self, x, y, dx, dy, text_surface, lifespan):
        super().__init__(x, y, dx, dy, 0, (0,0,0), lifespan)
        self.text_surface = text_surface

    def draw(self, surface):
        """Draw the text particle on the screen."""
        if self.lifespan > 0:
            surface.blit(self.text_surface, (int(self.x), int(self.y)))

class ParticleManager:
    """Manages all active particles for visual effects."""
    def __init__(self):
        self.particles = []

    def clear(self):
        """Remove all particles."""
        self.particles = []

    def update(self):
        """Update all active particles."""
        self.particles = [p for p in self.particles if p.lifespan > 0]
        for particle in self.particles:
            particle.update()

    def draw(self, surface):
        """Draw all active particles."""
        for particle in self.particles:
            particle.draw(surface)

    def create_blood_splatter(self, x, y, num_particles=20):
        """Create a blood splatter effect."""
        for _ in range(num_particles):
            dx = random.uniform(-2, 2)
            dy = random.uniform(-2, 2)
            size = random.uniform(2, 5)
            color = (random.randint(150, 255), 0, 0)
            lifespan = random.randint(20, 40)
            self.particles.append(Particle(x, y, dx, dy, size, color, lifespan))

    def create_damage_text(self, x, y, text, font, color=(255, 255, 255), lifespan=60):
        """Create a text-based particle for damage numbers."""
        text_surface = font.render(str(text), True, color)
        dx = random.uniform(-0.5, 0.5)
        dy = -1  # Move upwards
        self.particles.append(TextParticle(x, y, dx, dy, text_surface, lifespan))