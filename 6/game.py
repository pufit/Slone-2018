import pygame
import time
import websocket
import sys
import os
import json
from pygame.locals import *
from _thread import start_new_thread


sys.path.append(os.getcwd() + '\\WSServer\\')


WIN_FIELD_WIDTH = 400
WIN_FIELD_HEIGHT = 400
WIN_ADDITIONAL_WIDTH = 200
DISPLAY = (WIN_FIELD_WIDTH + WIN_ADDITIONAL_WIDTH, WIN_FIELD_HEIGHT)
BACKGROUND_COLOR = (13, 18, 33)
TICK = 0.10
FIELD_WIDTH = 20
FIELD_HEIGHT = 20
LIFE_HEIGHT = 80
SYNC_TIME = 1


def coord_to_coord(x, y, k):
    return x * WIN_FIELD_WIDTH // FIELD_WIDTH + k, y * WIN_FIELD_HEIGHT // FIELD_HEIGHT + k


class Field(pygame.sprite.Sprite):
    def __init__(self, screen):
        pygame.sprite.Sprite.__init__(self)
        self.screen = screen

        self.dots_color = (173, 192, 219)

        self.players = {}
        self.bullets = []

    def add_player(self, player):
        self.players[player.n] = player

    def draw_dots(self):
        for i in range(FIELD_WIDTH):
            for j in range(FIELD_HEIGHT):
                pygame.draw.circle(self.screen, self.dots_color,
                                   (WIN_FIELD_WIDTH//FIELD_WIDTH//2 + i*WIN_FIELD_WIDTH//FIELD_WIDTH,
                                    WIN_FIELD_HEIGHT//FIELD_HEIGHT//2 + j*WIN_FIELD_HEIGHT//FIELD_HEIGHT), 0, 0)

    def player_shoot(self, player):
        self.bullets.append(Bullet(player.x, player.y, player.direction))

    def action(self, n, act):
        player = self.players[n]
        if act == 'LEFT':
            player.speed_x = -1
            player.direction = 2
        elif act == 'RIGHT':
            player.speed_x = 1
            player.direction = 0
        elif act == 'UP':
            player.speed_y = -1
            player.direction = 1
        elif act == 'DOWN':
            player.speed_y = 1
            player.direction = -1
        elif act == 'SHOOT':
            player.shooting = True
        else:
            player.speed_x = 0
            player.speed_y = 0
            player.shooting = False

    def update(self):
        for player in self.players.values():
            if player.shooting:
                self.player_shoot(player)
            player.update()
            player.draw(self.screen)
        for bullet in self.bullets:
            bullet.update()
            bullet.draw(self.screen)
            for player in self.players.values():
                if (player.x == bullet.x) and (player.y == bullet.y):
                    player.life.damage()
        for player in self.players.values():
            player.life.draw(self.screen)
            player.speed_x = 0
            player.speed_y = 0
            player.shooting = False


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)

        self.width = WIN_FIELD_WIDTH // FIELD_WIDTH - 8
        self.height = WIN_FIELD_HEIGHT // FIELD_HEIGHT - 8

        self.image = pygame.image.load('src/sprites/bullet.png')
        self.image = pygame.transform.scale(self.image, (self.width, self.height))

        rect_x, rect_y = coord_to_coord(x, y, 3)
        self.rect = pygame.Rect(rect_x, rect_y, self.width, self.height)

        self.x, self.y = x, y
        self.direction = direction
        self.speed_x, self.speed_y = 0, 0
        if self.direction == 2:
            self.speed_x = -1
        elif self.direction == 1:
            self.speed_y = -1
        elif self.direction == 0:
            self.speed_x = 1
        elif self.direction == -1:
            self.speed_y = 1

    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        if self.x >= FIELD_WIDTH:
            self.x = 0
        if self.x < 0:
            self.x = FIELD_WIDTH - 1
        if self.y >= FIELD_HEIGHT:
            self.y = 0
        if self.y < 0:
            self.y = FIELD_HEIGHT - 1
        self.rect.x, self.rect.y = coord_to_coord(self.x, self.y, 2)

    def draw(self, screen):
        image = pygame.transform.rotate(self.image, 90 * self.direction)
        self.rect = image.get_rect(center=self.rect.center)

        screen.blit(image, (self.rect.x, self.rect.y))


class Life(pygame.sprite.Sprite):
    def __init__(self, life, n):
        pygame.sprite.Sprite.__init__(self)
        self.max_life = life
        self.life = life

        self.width = WIN_ADDITIONAL_WIDTH // 2
        self.height = LIFE_HEIGHT

        self.rect = Rect(WIN_FIELD_WIDTH + self.width*int(n - 1), 0, self.width, self.height)

        # потом исправлю
        self.image = pygame.Surface((self.rect.width, self.rect.height))
        if int(n) == 1:
            self.image.fill((255, 0, 0))
        else:
            self.image.fill((0, 0, 255))

        self.n = n

    def damage(self):
        self.life -= 1
        if self.life == 0:
            print('Player %s loose' % self.n)
            exit()
        self.rect.width = (self.width * self.life) // self.max_life
        self.image = pygame.Surface((self.rect.width, self.rect.height))
        if int(self.n) == 1:
            self.image.fill((255, 0, 0))
        else:
            self.image.fill((0, 0, 255))

    def draw(self, screen):
        screen.blit(self.image, (self.rect.x, self.rect.y))


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y, n):
        pygame.sprite.Sprite.__init__(self)

        self.x, self.y = x, y

        self.width = WIN_FIELD_WIDTH // FIELD_WIDTH - 2
        self.height = WIN_FIELD_HEIGHT // FIELD_HEIGHT - 2

        self.image = pygame.image.load('src/sprites/player%s.png' % n)
        self.image = pygame.transform.scale(self.image, (self.width, self.height))

        rect_x, rect_y = coord_to_coord(x, y, 2)
        self.rect = pygame.Rect(rect_x, rect_y, self.width, self.height)

        self.direction = 0
        self.speed_x, self.speed_y = 0, 0

        self.n = n

        self.life = Life(10, n)
        self.shooting = False

    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        if self.x >= FIELD_WIDTH:
            self.x = 0
        if self.x < 0:
            self.x = FIELD_WIDTH - 1
        if self.y >= FIELD_HEIGHT:
            self.y = 0
        if self.y < 0:
            self.y = FIELD_HEIGHT - 1
        self.rect.x, self.rect.y = coord_to_coord(self.x, self.y, 2)

    def draw(self, screen):
        image = pygame.transform.rotate(self.image, 90*self.direction)
        self.rect = image.get_rect(center=self.rect.center)

        screen.blit(image, (self.rect.x, self.rect.y))


def ws_client(field, me):
    while True:
        recv = json.loads(ws.recv())
        if recv['type'] == 'action':
            if recv['data']['player_id'] != me.n:
                field.action(recv['data']['player_id'], recv['data']['action_type'])
        if recv['type'] == 'sync' and me.n != 1:
            data = recv['data']
            for i in range(len(field.players)):
                player = field.players[i+1]
                player.x = data['players'][i][0]
                player.y = data['players'][i][1]
                player.direction = data['players'][i][2]
                player.life.life = data['players'][i][3]
            for i in range(len(field.bullets)):
                bullet = field.bullets[i]
                bullet.x = data['bullets'][i][0]
                bullet.y = data['bullets'][i][1]
                bullet.direction = data['bullets'][i][2]


def main():
    pygame.init()
    screen = pygame.display.set_mode(DISPLAY)
    pygame.display.set_caption("Arrows")
    bg = pygame.Surface((WIN_FIELD_WIDTH + WIN_ADDITIONAL_WIDTH, WIN_FIELD_HEIGHT))
    bg.fill(BACKGROUND_COLOR)

    main_loop = True

    field = Field(screen)

    if serv:
        me = Player(5, 10, 1)
        field.add_player(me)
        while True:
            recv = json.loads(ws.recv())
            if recv['type'] == 'player_connected':
                field.add_player(Player(15, 10, 2))
                break
    else:
        field.add_player(Player(5, 10, 1))
        me = Player(15, 10, 2)  # со всем id разбирусь позже. Пока сделаем онли для двоих
        field.add_player(me)

    start_new_thread(ws_client, (field, me))

    next_check_point = 3 + time.time()
    while main_loop:
        for event in pygame.event.get():
            if event.type == QUIT:
                main_loop = False
            if event.type == KEYDOWN:
                if event.key == K_LEFT:
                    ws.send(json.dumps({'type': 'do_action', 'data': {'action_type': 'LEFT'}}))
                    field.action(me.n, 'LEFT')
                if event.key == K_RIGHT:
                    ws.send(json.dumps({'type': 'do_action', 'data': {'action_type': 'RIGHT'}}))
                    field.action(me.n, 'RIGHT')
                if event.key == K_UP:
                    ws.send(json.dumps({'type': 'do_action', 'data': {'action_type': 'UP'}}))
                    field.action(me.n, 'UP')
                if event.key == K_DOWN:
                    ws.send(json.dumps({'type': 'do_action', 'data': {'action_type': 'DOWN'}}))
                    field.action(me.n, 'DOWN')
                if event.key == K_SPACE:
                    ws.send(json.dumps({'type': 'do_action', 'data': {'action_type': 'SHOOT'}}))
                    field.action(me.n, 'SHOOT')
        screen.blit(bg, (0, 0))
        field.draw_dots()

        field.update()
        pygame.display.update()

        if (time.time() > next_check_point) and (me.n == 1):
            resp = {
                'type': 'get_sync',
                'data': {
                    'bullets': [[bullet.x, bullet.y, bullet.direction] for bullet in field.bullets],
                    'players': [[player.x, player.y, player.direction,
                                 player.life.life] for player in field.players.values()],
                }
            }
            ws.send(json.dumps(resp))

            next_check_point = time.time() + SYNC_TIME

        time.sleep(TICK)


if __name__ == '__main__':
    from WSServer import server
    if input('Server or client? s/c\n') == 's':
        server.run()
        serv = True
        ip = 'ws://localhost:8000'
    else:
        serv = False
        ip = input('Address: ')
        ip = 'ws://' + ip

    ws = websocket.WebSocket()
    ws.connect(ip)
    main()
