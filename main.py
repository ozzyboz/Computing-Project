import time

import pygame
from sys import exit
import math

import utils
from settings import *
from levels import levels
from random import randint
import logging

#comment
pygame.init()
pygame.mixer.music.load('Sounds/fsm-team-banger.mp3')
# Game Window
info = pygame.display.Info()
screen_width,screen_height = info.current_w,info.current_h
window_width,window_height = screen_width-10,screen_height-50
window = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption('Zombie Squad')
# Clock for Timer
clock = pygame.time.Clock()
pygame.time.set_timer(pygame.USEREVENT, 1000)
pygame_icon = pygame.image.load('Images/sandstormicon.PNG')
pygame.display.set_icon(pygame_icon)
# Endgame Text
font = pygame.font.Font(None, 72)
gameover_text_surface = font.render("Mission Failed",True, (255,0,0))
win_text_surface = font.render("Mission Successful", True, (0,255,0))
timesup_text_surface = font.render("Times Up", True, (255,0,0))
restart_text_surface = font.render("Press V to restart level.", True, (255, 0, 0))
restartwin_text_surface = font.render("Press V to restart level.", True, (0, 255, 0))
winScreen_width, winScreen_height = win_text_surface.get_size()
winScreen_x = (window_width - winScreen_width)//2
winScreen_y = (window_height - winScreen_height)//2
# Loads Music
pistol_shot_sound = pygame.mixer.Sound("Sounds/Pistol_Firing.wav")
pistol_reload_sound = pygame.mixer.Sound("Sounds/Gun Reload sound effect.mp3")
pistol_empty_sound = pygame.mixer.Sound("Sounds/Empty gun shot.mp3")


class MovingCharacter(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.velocity_x = 0
        self.velocity_y = 0

    def move(self, walls):
        # Adjusts the position by the velocity
        self.is_collided_with_wall(walls)
        self.rect.x += self.velocity_x
        self.rect.y += self.velocity_y
        self.hitbox_rect.x += self.velocity_x
        self.hitbox_rect.y += self.velocity_y

    def is_collided_with_wall(self, walls):
        collision_list = pygame.sprite.spritecollide(self, walls, False)

        # if intersection with collidable object in collision_list ( horizontal x direction )
        for collided_object in collision_list:
            # if only moving left, ignore collisions to the top or bottom
            if self.velocity_x != 0 and self.velocity_y == 0 and (self.hitbox_rect.top >= collided_object.rect.centery or self.hitbox_rect.bottom <= collided_object.rect.centery):
                continue
            if self.velocity_y != 0 and self.velocity_x == 0 and (self.hitbox_rect.left >= collided_object.rect.centerx or self.hitbox_rect.right <= collided_object.rect.centerx):
                continue

            # Moving Left
            if self.velocity_x < 0 and self.hitbox_rect.left <= collided_object.rect.right and self.hitbox_rect.right >= collided_object.rect.right:
                self.velocity_x = 0
            # Moving Up
            if self.velocity_y < 0 and self.hitbox_rect.top <= collided_object.rect.bottom and self.hitbox_rect.bottom >= collided_object.rect.bottom:
                self.velocity_y = 0
            # Moving Right
            if self.velocity_x > 0 and self.hitbox_rect.right >= collided_object.rect.left and self.hitbox_rect.left <= collided_object.rect.left:
                self.velocity_x = 0
            # Moving Down
            if self.velocity_y > 0 and self.hitbox_rect.bottom >= collided_object.rect.top and self.hitbox_rect.top <= collided_object.rect.top:
                self.velocity_y = 0

class Player(MovingCharacter):
    score = 0
    ammo = 8
    rounds = 4
    key = 0
    exit = 0
    def __init__(self):
        super().__init__()
        self.image = pygame.transform.rotozoom(pygame.image.load('Images/player1.png').convert_alpha(), 0, 0.8)
        self.base_player_image = self.image
        self.hitbox_rect = self.base_player_image.get_rect()
        self.rect = self.hitbox_rect.copy()
        self.speed = PLAYER_SPEED
        self.health = 100
        self.shoot = False
        self.shoot_cooldown = 0
        self.gun_barrel_offset = pygame.math.Vector2(GUN_OFFSET_X, GUN_OFFSET_Y)

    def player_rotation(self):
        # Player faces mouse cursor
        self.mouse_coords = pygame.mouse.get_pos()
        self.x_change_mouse_player = (self.mouse_coords[0] - self.hitbox_rect.centerx)
        self.y_change_mouse_player = (self.mouse_coords[1] - self.hitbox_rect.centery)
        self.angle = math.degrees(math.atan2(self.y_change_mouse_player, self.x_change_mouse_player))
        self.image = pygame.transform.rotate(self.base_player_image, -self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

    def player_input(self):
        self.velocity_x = 0
        self.velocity_y = 0
        # Player Movement
        keys = pygame.key.get_pressed()
        # Moving Up
        if keys[pygame.K_w]:
            self.velocity_y = -self.speed
        # Moving Down
        if keys[pygame.K_s]:
            self.velocity_y = self.speed
        # Moving Left
        if keys[pygame.K_a]:
            self.velocity_x = -self.speed
        # Moving Right
        if keys[pygame.K_d]:
            self.velocity_x = self.speed
        # Moving Diagonally
        if self.velocity_x != 0 and self.velocity_y != 0:
            self.velocity_x /= math.sqrt(2)
            self.velocity_y /= math.sqrt(2)
        # Reload
        if keys[pygame.K_r]:
            if self.rounds > 0 and self.ammo == 0:
                self.ammo += 8
                self.rounds -= 1
                pygame.mixer.Sound.play(pistol_reload_sound)

        if pygame.mouse.get_pressed() == (1, 0, 0) or keys[pygame.K_SPACE]:
            self.shoot = True
            self.is_shooting()
        else:
            self.shoot = False

    def is_shooting(self):
        if self.shoot_cooldown == 0 and self.ammo > 0:
            self.shoot_cooldown = SHOOT_COOLDOWN
            spawn_bullet_pos = self.rect.center + self.gun_barrel_offset.rotate(self.angle)
            self.bullet = Bullet(spawn_bullet_pos[0], spawn_bullet_pos[1], self.angle)
            bullet_group.add(self.bullet)
            self.ammo -= 1
            pygame.mixer.Sound.play(pistol_shot_sound)
            # player_group.add(self.bullet)
        elif self.shoot_cooldown == 0 and self.ammo == 0:
            self.shoot_cooldown = SHOOT_COOLDOWN
            pygame.mixer.Sound.play(pistol_empty_sound)

    def is_collided_with_ammo(self, collidable):
        collision_list = pygame.sprite.spritecollide(self, collidable, False)
        for collided_object in collision_list:
            if isinstance(collided_object, Ammunition):
                self.rounds += 1
                collided_object.kill()
                collidable.remove(collided_object)

    def is_collided_with_key(self, collidable):
        collision_list = pygame.sprite.spritecollide(self, collidable, False)
        for collided_object in collision_list:
            if isinstance(collided_object, Key):
                self.key += 1
                collided_object.kill()
                collidable.remove(collided_object)

    def is_collided_with_door(self, collidable):
        collision_list = pygame.sprite.spritecollide(self, collidable, False)
        for collided_object in collision_list:
            if isinstance(collided_object, Door):
                if self.key == 1:
                    self.exit = 1

    def is_collided_with_treasure(self, collidable):
        collision_list = pygame.sprite.spritecollide(self, collidable, False)
        for collided_object in collision_list:
            if isinstance(collided_object, Treasure):
                Player.score += 250
                collided_object.kill()
                collidable.remove(collided_object)

    def set_position(self, x, y):
        # Sets Player Position
        dx = self.rect.x - x
        dy = self.rect.y - y
        self.rect.x = x
        self.rect.y = y
        self.hitbox_rect.x -= dx
        self.hitbox_rect.y -= dy

    def update(self, collidable = pygame.sprite.Group(), counter = 0):
        # Runs all player functions
        self.player_rotation()
        self.player_input()
        self.is_collided_with_ammo(ammunition_group)
        self.is_collided_with_key(key_group)
        self.is_collided_with_door(door_group)
        self.is_collided_with_treasure(treasure_group)
        self.move(collidable)
        if counter <= 0:
            self.kill()
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

class Enemy(MovingCharacter):
    def __init__(self, pos_x, pos_y):
        super().__init__()
        self.image = pygame.transform.rotozoom(pygame.image.load('Images/zombie_idle01.png').convert_alpha(), 0, 0.8)
        self.original_enemy_image = self.image
        self.hitbox_rect = self.image.get_rect(x=pos_x, y=pos_y)
        self.rect = self.hitbox_rect.copy()
        self.health = randint(30,60)
        self.rect.x = pos_x
        self.rect.y = pos_y

    def enemy_rotation(self):
        # Enemy Faces Player
        player_x = player.rect.centerx
        player_y = player.rect.centery
        # Works out distance from player
        x_change_player = (player_x - self.rect.centerx)
        y_change_player = (player_y - self.rect.centery)
        # Works out angle to face player
        angle = math.degrees(math.atan2(y_change_player, x_change_player))
        # Sets image to face player
        self.image = pygame.transform.rotate(self.original_enemy_image, -angle)
        self.hitbox_rect = self.image.get_rect(center=self.rect.center)
        self.rect = self.hitbox_rect.copy()

    def move(self, wall_group):
        # Enemy Hunts Player
        playerx = player.rect.centerx
        playery = player.rect.centery
        dx = playerx - self.rect.centerx
        dy = playery - self.rect.centery
        if utils.distance(playerx, playery, self.rect.centerx, self.rect.centery) < 900:
            if dx < 0:
                self.velocity_x = -8
            elif dx > 0:
                self.velocity_x = 8
            else:
                self.velocity_x = 0
            if dy < 0:
                self.velocity_y = -8
            elif dy > 0:
                self.velocity_y = 8
            else:
                self.velocity_y = 0
            # Moving Diagonally
            if self.velocity_x != 0 and self.velocity_y != 0:
                self.velocity_x /= math.sqrt(2)
                self.velocity_y /= math.sqrt(2)
        super().move(wall_group)

    def is_collided_with_player(self, collidable):
        collision_list = pygame.sprite.spritecollide(self, collidable, False)
        for collided_object in collision_list:
            if isinstance(collided_object, Player):
                if utils.distance(collided_object.rect.x, collided_object.rect.y, self.rect.x, self.rect.y) < self.rect.width//2:
                    # game over
                    player.health = 0
                    collided_object.kill()
                    collidable.remove(collided_object)
                    self.kill()

    def shift_world(self, shift_x, shift_y):
        self.rect.x += shift_x
        self.rect.y += shift_y

    def update(self):
        self.is_collided_with_player(player_group)
        self.enemy_rotation()
        self.move(walls_group)


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
        # Angle of bullet is taken from Player Class
        self.angle = new_angle
        # X and Y velocity worked out from angle
        self.x_vel = math.cos(self.angle * (2 * math.pi / 360)) * self.speed
        self.y_vel = math.sin(self.angle * (2 * math.pi / 360)) * self.speed

    def bullet_movement(self, collidable):
        # Runs the function to check if the bullet has collided
        self.isCollided(collidable)
        # Bullet movement changed by velocity
        self.x += self.x_vel
        self.y += self.y_vel

        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
        # Bullet destroyed once on screen too long
        if pygame.time.get_ticks() - self.spawn_time > self.bullet_lifetime:
            self.kill()

    def isCollided(self, collidable):
        # Gets group for the collided object
        collision_list = pygame.sprite.spritecollide(self, collidable, False)
        for collided_object in collision_list:
            # Checks if Collided object is an Enemy
            if isinstance(collided_object, Enemy):
                collided_object.health -= randint(10, 20)
                if collided_object.health <= 0:
                    dropitem = randint(1,5)
                    if dropitem == 5:
                        ammunition_group.add(Ammunition(collided_object.rect.x, collided_object.rect.y))
                    collided_object.kill()
                    collidable.remove(collided_object)
                    Player.score += 50
            self.kill()

    def update(self, collidable = pygame.sprite.Group()):
        self.bullet_movement(collidable)


class Wall(pygame.sprite.Sprite):

    def __init__(self, x, y, width=128, height=128):
        super().__init__()
        self.image = pygame.image.load('images/Wall.png').convert_alpha()
        self.image = pygame.transform.rotozoom(self.image, 0, 2)

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

class Ammunition(pygame.sprite.Sprite):
    def __init__(self, x, y, width=128, height=128):
        super().__init__()
        self.image = pygame.image.load('Images/ammo-pistol 32px.png').convert_alpha()
        self.image = pygame.transform.rotozoom(self.image, 0, 2)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def shift_world(self, shift_x, shift_y):
        self.rect.x += shift_x
        self.rect.y += shift_y

    def draw(self, window):
        window.blit(self.image, (self.rect.x, self.rect.y))

class Fake_Wall(pygame.sprite.Sprite):

    def __init__(self, x, y, width=128, height=128):
        super().__init__()
        self.image = pygame.image.load('images/Wall.png').convert_alpha()
        self.image = pygame.transform.rotozoom(self.image, 0, 2)

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

class Door(pygame.sprite.Sprite):

    def __init__(self, x, y, width=128, height=128):
        super().__init__()
        self.image = pygame.image.load('images/silverdoor.jpg').convert_alpha()
        self.image = pygame.transform.rotozoom(self.image, 0, 0.5)

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

class Key(pygame.sprite.Sprite):

    def __init__(self, x, y, width=128, height=128):
        super().__init__()
        self.image = pygame.image.load('images/key_big.png').convert_alpha()
        self.image = pygame.transform.rotozoom(self.image, 0, 2)

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

class Treasure(pygame.sprite.Sprite):

    def __init__(self, x, y, width=128, height=128):
        super().__init__()
        self.image = pygame.image.load('images/GoldTrophy.png').convert_alpha()
        self.image = pygame.transform.rotozoom(self.image, 0, 2)

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
    # Makes global variables for entities
    global all_sprites_group, current_level, running, player, player_group, enemies_group
    global bullet_group, walls_group, ammunition_group, fake_wall_group, door_group, key_group, treasure_group

    global player
    player = Player()
    player_group = pygame.sprite.Group()
    player_group.add(player)

    enemies_group = pygame.sprite.Group()

    bullet_group = pygame.sprite.Group()

    current_level = 0
    # running = True

    # Creates empty groups
    walls_group = pygame.sprite.Group()
    enemies_group = pygame.sprite.Group()
    ammunition_group = pygame.sprite.Group()
    fake_wall_group = pygame.sprite.Group()
    door_group = pygame.sprite.Group()
    key_group = pygame.sprite.Group()
    treasure_group = pygame.sprite.Group()

def run_viewbox(player_x, player_y):
    # Divides the screen into four sections
    left_viewbox = window_width/2 - window_width/8
    right_viewbox = window_width/2 - window_width/16
    top_viewbox = window_height/2 - window_height/8
    bottom_viewbox = window_height/2 - window_height/16
    dx, dy = 0, 0
    # Checks which section the player is in
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
    # Shifts all entities
    if (dx != 0 or dy != 0):
        for wall in walls_group:
            wall.shift_world(dx, dy)
        for enemy in enemies_group:
            enemy.shift_world(dx, dy)
        for ammunition in ammunition_group:
            ammunition.shift_world(dx, dy)
        for fake_wall in fake_wall_group:
            fake_wall.shift_world(dx, dy)
        for door in door_group:
            door.shift_world(dx, dy)
        for key in key_group:
            key.shift_world(dx, dy)
        for treasure in treasure_group:
            treasure.shift_world(dx, dy)

def setup_maze(current_level):
    # Repeats for the height of the map [50]
    for y in range(len(levels[current_level])):
        # Repeats for the width of the map [50]
        for x in range(len(levels[current_level][y])):
            # Checks the current character in the list
            character = levels[current_level][y][x]
            # Changes the position of the character in the list to an in game coordinate
            pos_x = (x * 128)
            pos_y = (y * 128)

            if character == "X":
                # Update wall coordinates
                walls_group.add(Wall(pos_x, pos_y))
            elif character == "P":
                player.set_position(pos_x, pos_y)
            elif character == "E":
                enemies_group.add(Enemy(pos_x, pos_y))
                logging.warning(len(enemies_group))
            elif character == "A":
                ammunition_group.add(Ammunition(pos_x, pos_y))
            elif character == "O":
                fake_wall_group.add(Fake_Wall(pos_x, pos_y))
            elif character == "D":
                door_group.add(Door(pos_x, pos_y))
            elif character == "K":
                key_group.add(Key(pos_x, pos_y))
            elif character == "T":
                treasure_group.add(Treasure(pos_x, pos_y))




def main():
    loading = True
    isGameOver = False
    counter = 300
    create_instances()
    setup_maze(current_level)
    pygame.mixer.music.play(-1)

    running = True

    while running:

        bullet_group.update(walls_group)
        bullet_group.update(enemies_group)
        player_group.update(walls_group, counter)
        enemies_group.update()
        walls_group.update()

        run_viewbox(player.rect.x, player.rect.y)
        window.fill((0, 0, 0))

        for wall in walls_group:
            if (wall.rect.x < window_width) and (wall.rect.y < window_height):
                wall.draw(window)
        ammunition_group.draw(window)
        key_group.draw(window)
        treasure_group.draw(window)
        door_group.draw(window)
        player_group.draw(window)
        enemies_group.draw(window)
        bullet_group.draw(window)
        fake_wall_group.draw(window)

        time_surface = font.render("Time: " + str(counter), True, (255,255,255))
        window.blit(time_surface, (20,20))


        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.USEREVENT:
                if counter > 0 and player.health != 0:
                    if player.exit == 0:
                        counter -= 1

        if keys[pygame.K_v]:
            Player.score = 0
            Player.key = 0
            Player.exit = 0
            main()

        # enemiesRemaining = len(enemies_group)
        # enemiesRemaining_surface = font.render("Enemies Remaining: " + str(enemiesRemaining), True, (255, 0, 0))
        # window.blit(enemiesRemaining_surface, (20,20))
        ammo_surface = font.render("Ammo " + str(player.ammo) + "/" + str(player.rounds * 8), True, (255,255,255))
        window.blit(ammo_surface, (2200,1250))
        score_surface = font.render("Score: " + str(player.score), True, (0, 255, 0))
        window.blit(score_surface, (20,80))

        if player.exit > 0:
            pygame.mixer.music.stop()
            window.fill((0, 0, 0))
            window.blit(win_text_surface, (winScreen_x, winScreen_y))
            window.blit(restartwin_text_surface, (winScreen_x - 50, winScreen_y + 100))
            window.blit(score_surface, (20, 80))
            window.blit(time_surface, (20, 20))
        if player.health == 0:
            pygame.mixer.music.stop()
            window.fill((0, 0, 0))
            window.blit(gameover_text_surface, (winScreen_x, winScreen_y))
            window.blit(restart_text_surface, (winScreen_x - 80, winScreen_y + 100))
            window.blit(score_surface, (20, 80))
            window.blit(time_surface, (20, 20))
        if counter < 1:
            pygame.mixer.music.stop()
            window.fill((0, 0, 0))
            window.blit(timesup_text_surface, (winScreen_x + 100, winScreen_y))
            window.blit(restart_text_surface, (winScreen_x - 50, winScreen_y + 100))
            window.blit(score_surface, (20, 80))
            window.blit(time_surface, (20, 20))


        # pygame.draw.rect(window, 'red', player.hitbox_rect, width=2)
        # pygame.draw.rect(window, 'yellow', player.rect, width=2)

        pygame.display.update()
        clock.tick(60)

main()
