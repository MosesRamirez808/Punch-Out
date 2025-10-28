import pygame
import sys
import random

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Shoot-Out with Wall")

clock = pygame.time.Clock()
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (200, 0, 0)
BLUE = (0, 0, 200)
GREEN = (0, 200, 0)
GRAY = (150, 150, 150)

# Bullet & wall constants
BULLET_SPEED = 8
WALL_MAX_HP = 50

# Stick figure constants
BODY_LENGTH = 60
LEG_LENGTH = 40
HEAD_RADIUS = 15
ARM_LENGTH = 30

# Hat drawing: simple wide-brim “Stetson” style above the head
def draw_stetson(surface, x, y):
    # x, y is center of head
    brim_width = 40
    brim_height = 6
    crown_width = 20
    crown_height = 12
    # Brim
    brim_rect = pygame.Rect(x - brim_width//2, y - HEAD_RADIUS - 4, brim_width, brim_height)
    pygame.draw.ellipse(surface, BLACK, brim_rect)
    # Crown
    crown_rect = pygame.Rect(x - crown_width//2, y - HEAD_RADIUS - 4 - crown_height, crown_width, crown_height)
    pygame.draw.ellipse(surface, BLACK, crown_rect)

class Bullet:
    def __init__(self, x, y, direction, owner):
        self.rect = pygame.Rect(x, y, 6, 4)
        self.direction = direction  # ±1
        self.owner = owner

    def move(self):
        self.rect.x += self.direction * BULLET_SPEED

    def draw(self, surface):
        pygame.draw.rect(surface, BLACK, self.rect)

    def off_screen(self):
        return self.rect.right < 0 or self.rect.left > WIDTH

class Shooter:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.health = 100
        self.bullets = []
        self.shoot_cooldown = 0
        # vertical movement allowed
        self.speed = 4

    def draw(self, surface):
        # Draw stick figure (no arms for punching now, maybe arms can aim)
        head = (self.x, self.y)
        body_start = (self.x, self.y + HEAD_RADIUS)
        body_end = (self.x, self.y + HEAD_RADIUS + BODY_LENGTH)
        left_leg = (self.x - 10, self.y + HEAD_RADIUS + BODY_LENGTH + LEG_LENGTH)
        right_leg = (self.x + 10, self.y + HEAD_RADIUS + BODY_LENGTH + LEG_LENGTH)

        pygame.draw.circle(surface, self.color, head, HEAD_RADIUS)
        pygame.draw.line(surface, self.color, body_start, body_end, 3)
        pygame.draw.line(surface, self.color, body_end, left_leg, 3)
        pygame.draw.line(surface, self.color, body_end, right_leg, 3)

        # Draw hat
        draw_stetson(surface, self.x, self.y)

        # Draw bullets
        for b in self.bullets:
            b.draw(surface)

    def move_vert(self, dir):  # dir = +1 or -1
        self.y += dir * self.speed
        # Clamp within screen
        self.y = max(HEAD_RADIUS + 5, min(self.y, HEIGHT - (HEAD_RADIUS + BODY_LENGTH + LEG_LENGTH + 5)))

    def shoot(self, direction):
        if self.shoot_cooldown == 0:
            # bullet originates near middle of body
            bx = self.x + direction * (ARM_LENGTH + 5)
            by = self.y + HEAD_RADIUS + 10
            self.bullets.append(Bullet(bx, by, direction, self))
            self.shoot_cooldown = 20

    def update(self):
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        # Bullets update
        for b in self.bullets[:]:
            b.move()
            if b.off_screen():
                self.bullets.remove(b)

# Wall between them
class Wall:
    def __init__(self):
        self.hp = WALL_MAX_HP
        self.width = 20
        self.left = WIDTH//2 - self.width//2
        self.height = HEIGHT
        # optional: store initial hp to compute opacity

    def draw(self, surface):
        # The more damage, the more transparent or lighter
        alpha = max(50, int(255 * (self.hp / WALL_MAX_HP)))
        wall_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        wall_color = (100, 100, 100, alpha)
        wall_surf.fill(wall_color)
        surface.blit(wall_surf, (self.left, 0))

    def take_damage(self, amount):
        self.hp -= amount
        if self.hp < 0:
            self.hp = 0

    def is_destroyed(self):
        return self.hp <= 0

# AI behavior for shooter
def ai_control(ai: Shooter, player: Shooter, wall: Wall):
    # move up/down randomly toward player’s y sometimes
    if random.random() < 0.02:
        if player.y < ai.y:
            ai.move_vert(-1)
        elif player.y > ai.y:
            ai.move_vert(1)
    # shoot when wall still exists (else maybe shoot directly through)
    if random.randint(0, 50) == 1:
        ai.shoot(-1)  # shoots leftwards

def draw_health_bar(f, x, y):
    w = 100
    h = 10
    fill = int((f.health / 100) * w)
    pygame.draw.rect(screen, BLACK, (x, y, w, h), 1)
    pygame.draw.rect(screen, GREEN, (x, y, fill, h))

def main():
    player = Shooter(100, HEIGHT//2, RED)
    enemy = Shooter(WIDTH - 100, HEIGHT//2, BLUE)
    wall = Wall()

    running = True
    while running:
        clock.tick(FPS)
        screen.fill(WHITE)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        # Player vertical move
        if keys[pygame.K_UP]:
            player.move_vert(-1)
        if keys[pygame.K_DOWN]:
            player.move_vert(1)
        if keys[pygame.K_SPACE]:
            # shoot to the right
            player.shoot(1)

        # AI
        ai_control(enemy, player, wall)

        # Update
        player.update()
        enemy.update()

        # Bullet collisions
        # Player’s bullets
        for b in player.bullets[:]:
            # hit wall?
            if not wall.is_destroyed():
                # check collision with wall rectangle
                if b.rect.colliderect(pygame.Rect(wall.left, 0, wall.width, wall.height)):
                    wall.take_damage(1)
                    player.bullets.remove(b)
                    continue
            else:
                # wall destroyed => can hit enemy
                if b.rect.colliderect(pygame.Rect(enemy.x - HEAD_RADIUS, enemy.y, HEAD_RADIUS*2, BODY_LENGTH + LEG_LENGTH + HEAD_RADIUS)):
                    enemy.health -= 15
                    player.bullets.remove(b)

        # Enemy’s bullets
        for b in enemy.bullets[:]:
            if not wall.is_destroyed():
                if b.rect.colliderect(pygame.Rect(wall.left, 0, wall.width, wall.height)):
                    wall.take_damage(1)
                    enemy.bullets.remove(b)
                    continue
            else:
                if b.rect.colliderect(pygame.Rect(player.x - HEAD_RADIUS, player.y, HEAD_RADIUS*2, BODY_LENGTH + LEG_LENGTH + HEAD_RADIUS)):
                    player.health -= 15
                    enemy.bullets.remove(b)

        # Draw elements
        player.draw(screen)
        enemy.draw(screen)
        wall.draw(screen)

        draw_health_bar(player, 20, 20)
        draw_health_bar(enemy, WIDTH - 120, 20)

        # Check for win
        font = pygame.font.SysFont(None, 60)
        if player.health <= 0:
            screen.blit(font.render("YOU LOSE", True, BLACK), (WIDTH//2 - 100, HEIGHT//2))
        elif enemy.health <= 0:
            screen.blit(font.render("YOU WIN", True, BLACK), (WIDTH//2 - 100, HEIGHT//2))

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
