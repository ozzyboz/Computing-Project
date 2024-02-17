import pygame
from sys import exit
import math
from settings import *
from levels import levels
import logging
#comment
pygame.init()

# Game Window
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Sandstorm')
clock = pygame.time.Clock()
pygame_icon = pygame.image.load('Images/sandstormicon.PNG')
pygame.display.set_icon(pygame_icon)

# Loads Player
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.pos = pygame.math.Vector2(PLAYER_START_X, PLAYER_START_Y)
        self.image = pygame.transform.rotozoom(pygame.image.load('Images/player1.png').convert_alpha(), 0, PLAYER_SIZE)
        self.base_player_image = self.image
        self.hitbox_rect = self.base_player_image.get_rect(center=self.pos)
        self.rect = self.hitbox_rect.copy()
        self.speed = PLAYER_SPEED
        self.velocity_x = 0
        self.velocity_y = 0
        self.shoot = False
        self.shoot_cooldown = 0
        self.gun_barrel_offset = pygame.math.Vector2(GUN_OFFSET_X, GUN_OFFSET_Y)

    def player_rotation(self):
        self.mouse_coords = pygame.mouse.get_pos()
        self.x_change_mouse_player = (self.mouse_coords[0] - self.hitbox_rect.centerx)
        self.y_change_mouse_player = (self.mouse_coords[1] - self.hitbox_rect.centery)
        self.angle = math.degrees(math.atan2(self.y_change_mouse_player, self.x_change_mouse_player))
        self.image = pygame.transform.rotate(self.base_player_image, -self.angle)
        self.rect = self.image.get_rect(center=self.hitbox_rect.center)
    def player_input(self):
        self.velocity_x = 0
        self.velocity_y = 0
        keys = pygame.key.get_pressed()

        if keys[pygame.K_w]:
            self.velocity_y = -self.speed
        if keys[pygame.K_s]:
            self.velocity_y = self.speed
        if keys[pygame.K_a]:
            self.velocity_x = -self.speed
        if keys[pygame.K_d]:
            self.velocity_x = self.speed
        # Moving Diagonally
        if self.velocity_x != 0 and self.velocity_y != 0:
            self.velocity_x /= math.sqrt(2)
            self.velocity_y /= math.sqrt(2)

        if pygame.mouse.get_pressed() == (1, 0, 0) or keys[pygame.K_SPACE]:
            self.shoot = True
            self.is_shooting()
        else:
            self.shoot = False

    def move(self):
        self.rect.x += self.velocity_x
        self.rect.y += self.velocity_y
        self.hitbox_rect.x += self.velocity_x
        self.hitbox_rect.y += self.velocity_y

        # self.pos += pygame.math.Vector2(self.velocity_x, self.velocity_y)
        # self.hitbox_rect.center = self.pos
        # self.rect.center = self.hitbox_rect.center

    def is_shooting(self):
        if self.shoot_cooldown == 0:
            self.shoot_cooldown = SHOOT_COOLDOWN
            spawn_bullet_pos = self.pos + self.gun_barrel_offset.rotate(self.angle)
            self.bullet = Bullet(spawn_bullet_pos[0], spawn_bullet_pos[1], self.angle)
            bullet_group.add(self.bullet)
            # player_group.add(self.bullet)

    def set_position(self, x, y):
        dx = self.rect.x - x
        dy = self.rect.y - y
        self.rect.x = x
        self.rect.y = y
        self.hitbox_rect.x -= dx
        self.hitbox_rect.y -= dy

    def update(self):
        self.player_rotation()
        self.player_input()
        self.move()

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle):
        super().__init__()
        self.image = pygame.image.load("Images/Bullet.png").convert_alpha()
        self.image = pygame.transform.rotozoom(self.image, 0, BULLET_SCALE)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.x = x
        self.y = y
        self.angle = angle
        self.speed = BULLET_SPEED
        self.x_vel = math.cos(self.angle * (2 * math.pi / 360)) * self.speed
        self.y_vel = math.sin(self.angle * (2 * math.pi / 360)) * self.speed
        self.bullet_lifetime = BULLET_LIFETIME
        self.spawn_time = pygame.time.get_ticks()  # gets the time that the bullet was created

    def update_angle(self, new_angle):
        self.angle = new_angle
        self.x_vel = math.cos(self.angle * (2 * math.pi / 360)) * self.speed
        self.y_vel = math.sin(self.angle * (2 * math.pi / 360)) * self.speed

    def bullet_movement(self):
        self.x += self.x_vel
        self.y += self.y_vel

        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

        if pygame.time.get_ticks() - self.spawn_time > self.bullet_lifetime:
            self.kill()

    def update(self):
        self.bullet_movement()


class Wall(pygame.sprite.Sprite):

    def __init__(self, x, y, width=64, height=64):
        super().__init__()
        self.image = pygame.image.load('images/Wall.png').convert_alpha()

        # self.image = pygame.Surface((width, height))
        # self.image.fill((255,100,180))

        self.rect = self.image.get_rect()

        self.rect.x = x
        self.rect.y = y

    def shift_world(self, shift_x, shift_y):
        self.rect.x += shift_x
        self.rect.y += shift_y

    def draw(self, window):
        window.blit(self.image, (self.rect.x, self.rect.y))


def create_instances():
    global current_level, running, player, player_group
    global all_sprites_group, bullet_group, walls_group, enemies_group

    player = Player()
    player_group = pygame.sprite.Group()
    player_group.add(player)

    bullet_group = pygame.sprite.Group()

    current_level = 0
    # running = True


    walls_group = pygame.sprite.Group()
    enemies_group = pygame.sprite.Group()

def run_viewbox(player_x, player_y):
    left_viewbox = WIDTH/2 - WIDTH/8
    right_viewbox = WIDTH/2 + WIDTH/8
    top_viewbox = HEIGHT/2 - HEIGHT/8
    bottom_viewbox = HEIGHT/2 + HEIGHT/8
    dx, dy = 0, 0

    if(player_x <= left_viewbox):
        dx = left_viewbox - player_x
        # logging.warning(f'dx {dx} left_viewbox {left_viewbox} playerx {player_x}')
        player.set_position(left_viewbox, player.rect.y)

    elif(player_x >= right_viewbox):
        dx = right_viewbox - player_x
        player.set_position(right_viewbox, player.rect.y)

    if(player_y <= top_viewbox):
        dy = top_viewbox - player_y
        player.set_position(player.rect.x, top_viewbox)

    elif(player_y >= bottom_viewbox):
        dy = bottom_viewbox - player_y
        player.set_position(player.rect.x, bottom_viewbox)

    if (dx != 0 or dy != 0):
        for wall in walls_group:
            wall.shift_world(dx, dy)

def setup_maze(current_level):
    for y in range(len(levels[current_level])):
        for x in range(len(levels[current_level][y])):
            character = levels[current_level][y][x]
            pos_x = (x * 64)
            pos_y = (y * 64)

            if character == "X":
                # Update wall coordinates
                walls_group.add(Wall(pos_x, pos_y))
            elif character == "P":
                # TODO - fix this
                PLAYER_START_X = pos_x
                PLAYER_START_Y = pos_y


def main():
    loading = True
    isGameOver = False
    create_instances()
    setup_maze(current_level)

    running = True

    while running:

        bullet_group.update()
        player_group.update()
        walls_group.update()

        run_viewbox(player.rect.x, player.rect.y)
        window.fill((0, 0, 0))

        for wall in walls_group:
            if (wall.rect.x < WIDTH) and (wall.rect.y < HEIGHT):
                wall.draw(window)
        player_group.draw(window)
        bullet_group.draw(window)

        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        pygame.draw.rect(window, 'red', player.hitbox_rect, width=2)
        pygame.draw.rect(window, 'yellow', player.rect, width=2)

        pygame.display.update()
        clock.tick(FPS)

main()
