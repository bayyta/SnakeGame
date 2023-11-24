import os
import sys
import pygame as pg
import random as rand
import math
from enum import Enum

# MODIFIABLE variables
scale =         2.0
tilesHori =     28          # max 32
tilesVert =     28          # max 32
startSpeed =    5.0         # tiles per second
score =         0
appleSpeed =    1.0

# read only variables
speed =         startSpeed
tileSize =      16 * scale
width =         512 * scale
height =        512 * scale
xOffset =       (width - tileSize * tilesHori) / 2
yOffset =       (height - tileSize * tilesVert) / 2

# game variables
class GameState(Enum):
    menu =      1
    play =      2
    gameover =  3
state = GameState.menu
font = None

class SnakePiece:
    def __init__(self, pos, dir, image, head):
        global tileSize
        global xOffset
        global yOffset
        self.pos = pos
        self.dir = dir
        self.image = pg.transform.scale(image, (int(tileSize), int(tileSize)))
        self.head = head
        self.rot = 0
        if (dir == [True, False]): self.rot = 270
        elif (dir == [-True, False]): self.rot = 90
        elif (dir == [False, True]): self.rot = 180
        else: self.rot = 0
        self.turns = [] # stores coordinates and directions for every turn
        self.rect = image.get_rect()
        self.rect.x = self.pos[0] * tileSize + xOffset
        self.rect.y = self.pos[1] * tileSize + yOffset
        self.rect.width = tileSize
        self.rect.height = tileSize
            
    def updatePos(self, vel):
        global tileSize
        global xOffset
        global yOffset
        bool = True
        if (self.turns):
            if (self.pos == self.turns[0][0]):
                if (self.head):
                    self.rotateHead()
                    if (self.dir[0] * self.turns[0][1][0] == -1 or self.dir[1] * self.turns[0][1][1] == -1): # snake turning 180 degrees
                        bool = False
                self.dir = self.turns[0][1]
                del self.turns[0]
        self.pos[0] += self.dir[0] * vel
        self.pos[1] += self.dir[1] * vel
        self.rect.x = self.pos[0] * tileSize + xOffset
        self.rect.y = self.pos[1] * tileSize + yOffset
        return bool

    def rotateHead(self):
        if (len(self.turns) > 0):
            _dir = self.turns[-1][1]
            if (_dir == [True, False]): self.rot = 270
            elif (_dir == [-True, False]): self.rot = 90
            elif (_dir == [False, True]): self.rot = 180
            else: self.rot = 0

    def render(self, screen):
        if (self.head): screen.blit(pg.transform.rotate(self.image, self.rot), self.rect)
        else: screen.blit(self.image, self.rect)

class Apple:
    def __init__(self, image, pieces):
        global tileSize
        global xOffset
        global yOffset
        self.pos = self.randomizeSpawn(pieces)
        self.image = pg.transform.scale(image, (int(tileSize), int(tileSize)))
        self.rect = image.get_rect()
        self.rect.x = self.pos[0] * tileSize + xOffset
        self.rect.y = self.pos[1] * tileSize + yOffset
        self.rect.width = tileSize
        self.rect.height = tileSize

    def randomizeSpawn(self, pieces):
        global tilesHori
        global tilesVert
        emptyTiles = []
        for y in range(tilesVert):
            for x in range(tilesHori):
                emptyTiles.append([x, y])
        for piece in pieces:
            if (piece.pos in emptyTiles): emptyTiles.remove(piece.pos)
        return emptyTiles[rand.randrange(0, len(emptyTiles))]

    def render(self, screen):
        screen.blit(self.image, self.rect)

# static class?
class Text:
    def renderFromCenter(screen, text, xOff, yOff, color, _font = None, antialias = 0):
        if _font == None:
            _font = font
        surface = _font.render(text, antialias, color)
        rect = surface.get_rect()
        rect.x = width / 2 - rect.width / 2 + xOff
        rect.y = height / 2 - (rect.height / 2) + yOff
        screen.blit(surface, rect)

class Menu:
    def __init__(self):
        self.menuitems = ["-PLAY", "OPTIONS", "EXIT"]
        self.selected = 0
        self.gap = 40 * scale
        self.options = Options()

    def render(self, screen):
        if not self.options.running:
            for i in range(len(self.menuitems)):
                yOff = self.gap * (i - ((len(self.menuitems) - 1) / 2)) # vertical offset for text
                Text.renderFromCenter(screen, self.menuitems[i], 1 * scale, yOff + 3 * scale, (0, 0, 0))
                Text.renderFromCenter(screen, self.menuitems[i], 0, yOff, (255, 255, 255))
        else:
            self.options.render(screen)

    def keyDown(self, key):
        global state
        if not self.options.running:
            if key == pg.K_UP: self.selected -= 1
            elif key == pg.K_DOWN: self.selected += 1
            elif key == pg.K_RETURN:
                if self.selected == 0: state = GameState.play
                elif self.selected == 1: self.options.running = True
                elif self.selected == 2: sys.exit()
                return
            if self.selected < 0: self.selected = len(self.menuitems) - 1
            elif self.selected > len(self.menuitems) - 1: self.selected = 0
            if self.selected == 0: self.menuitems[0] = "-PLAY"
            else: self.menuitems[0] = "PLAY"
            if self.selected == 1: self.menuitems[1] = "-OPTIONS"
            else: self.menuitems[1] = "OPTIONS"
            if self.selected == 2: self.menuitems[2] = "-EXIT"
            else: self.menuitems[2] = "EXIT"
        else:
            self.options.keyDown(key)

class Options:
    def __init__(self):
        self.difficulties = [appleSpeed, appleSpeed * 2, appleSpeed * 20]
        self.diffText = ["EASY", "MEDIUM", "HARD"]
        self.diffSelected = 0
        self.scaleMin = 0.5
        self.scaleMax = 3.0
        self.selected = 0
        self.scale = scale
        self.menuitems = ["-DIFFICULTY: EASY", "HORIZONTAL TILES: " + str(tilesHori), "VERTICAL TILES: " + str(tilesVert), "SCALE: " + str(self.scale)]
        self.gap = 40 * scale
        self.running = False

    def render(self, screen):
        for i in range(len(self.menuitems)):
            yOff = self.gap * (i - ((len(self.menuitems) - 1) / 2)) # vertical offset for text
            Text.renderFromCenter(screen, self.menuitems[i], 1 * scale, yOff + 3 * scale, (0, 0, 0))
            Text.renderFromCenter(screen, self.menuitems[i], 0, yOff, (255, 255, 255))

    def keyDown(self, key):
        global state
        global appleSpeed
        if key == pg.K_UP: self.selected -= 1
        elif key == pg.K_DOWN: self.selected += 1
        elif key == pg.K_ESCAPE:
            self.running = False
            return
        if self.selected < 0: self.selected = len(self.menuitems) - 1
        elif self.selected > len(self.menuitems) - 1: self.selected = 0
        if self.selected == 0: 
            if key == pg.K_LEFT:
                self.diffSelected -= 1
            elif key == pg.K_RIGHT:
                self.diffSelected += 1
            if self.diffSelected > len(self.diffText) - 1: self.diffSelected = 0
            elif self.diffSelected < 0: self.diffSelected = len(self.diffText) - 1
            appleSpeed = self.difficulties[self.diffSelected]
            self.menuitems[0] = "-DIFFICULTY: " + self.diffText[self.diffSelected]
        else: self.menuitems[0] = "DIFFICULTY: " + self.diffText[self.diffSelected]
        if self.selected == 1: self.menuitems[1] = "-HORIZONTAL TILES: " + str(tilesHori)
        else: self.menuitems[1] = "HORIZONTAL TILES: " + str(tilesHori)
        if self.selected == 2: self.menuitems[2] = "-VERTICAL TILES: " + str(tilesVert)
        else: self.menuitems[2] = "VERTICAL TILES: " + str(tilesVert)
        if self.selected == 3: 
            if key == pg.K_LEFT:
                self.scale -= 0.5
                if self.scale < self.scaleMin:
                    self.scale = self.scaleMin
            elif key == pg.K_RIGHT:
                self.scale += 0.5
                if self.scale > self.scaleMax:
                    self.scale = self.scaleMax
            self.menuitems[3] = "-SCALE: " + str(self.scale)
        else: self.menuitems[3] = "SCALE: " + str(self.scale)

class GameOver:
    def __init__(self):
        self.fontbig = pg.font.Font("fonts/pixeled/Pixeled.ttf", int(28 * scale))
        self.menuitems = ["-PLAY AGAIN", "MENU"]
        self.selected = 0
        self.gap = 40 * scale
        self.newState = None

    def render(self, screen):
        Text.renderFromCenter(screen, str(score), 1 * scale, 3 * scale - self.gap * 1.5, (0, 0, 0), self.fontbig)
        Text.renderFromCenter(screen, str(score), 0, -self.gap * 1.5, (255, 255, 255), self.fontbig)
        for i in range(len(self.menuitems)):
            Text.renderFromCenter(screen, self.menuitems[i], 1 * scale, self.gap * i + 3 * scale, (0, 0, 0))
            Text.renderFromCenter(screen, self.menuitems[i], 0, self.gap * i, (255, 255, 255))

    def shouldRestart(self):
        return self.newState

    def keyDown(self, key):
        if key == pg.K_UP: self.selected -= 1
        elif key == pg.K_DOWN: self.selected += 1
        elif key == pg.K_RETURN:
            if self.selected == 0: self.newState = GameState.play
            elif self.selected == 1: 
                self.newState = GameState.menu
            return
        if self.selected < 0: self.selected = len(self.menuitems) - 1
        elif self.selected > len(self.menuitems) - 1: self.selected = 0
        if self.selected == 0: self.menuitems[0] = "-PLAY AGAIN"
        else: self.menuitems[0] = "PLAY AGAIN"
        if self.selected == 1: self.menuitems[1] = "-MENU"
        else: self.menuitems[1] = "MENU"

class Level:
    def __init__(self):
        global tileSize
        global tilesHori
        global tilesVert
        global xOffset
        global yOffset
        self.time = 0.0
        self.headImage = pg.image.load("res/head.png")
        self.bodyImage = pg.image.load("res/body.png")
        self.appleImage = pg.image.load("res/apple.png")
        self.pieces = [SnakePiece([int(tilesHori / 2), int(tilesVert / 2)], [True, False], self.headImage, True)] # start in center moving right
        self.apples = [Apple(self.appleImage, self.pieces)]
        self.colors = []
        self.rects = []
        self.menu = Menu()
        self.gameOver = GameOver()

        # set tile colors
        for i in range(tilesHori * tilesVert):
            self.colors.append(rand.randint(0, 5))

        # set tile positions and sizes
        for y in range(tilesVert):
            for x in range(tilesHori):
                self.rects.append([x * tileSize + xOffset, y * tileSize + yOffset, tileSize - 1, tileSize - 1])
                
    def update(self, dt):
        global state
        global speed
        global score
        global tilesHori
        global tilesVert
        # switch current state
        if (state == GameState.menu):
            pass
        elif (state == GameState.play):
            # snake update
            self.time += (dt / 1000.0) * speed
            if (self.time >= 1.0):              
                # update position
                for piece in self.pieces:
                    if not piece.updatePos(math.floor(self.time)):
                        state = GameState.gameover
                        return
                self.time -= math.floor(self.time)
                # check for collisions
                bool = False
                # apple collision
                for i in range(len(self.apples)):
                    if (self.collide(self.pieces[0].pos, self.apples[i].pos)):
                        # collision
                        del self.apples[i]
                        self.apples.append(Apple(self.appleImage, self.pieces)) # add new apple
                        self.appendPiece(self.pieces[-1].pos, self.pieces[-1].dir, self.pieces[-1].turns) # add new snake piece
                        bool = True
                        speed += appleSpeed
                        score += 1
                        break
                # if apple was eaten, don't check for snake collision
                if not bool:
                    for i in range(1, len(self.pieces)):
                        if (self.collide(self.pieces[0].pos, self.pieces[i].pos)):
                            # collision
                            state = GameState.gameover
                            return
                # check if out of bounds
                if (self.pieces[0].pos[0] < 0 or self.pieces[0].pos[0] >= tilesHori): state = GameState.gameover
                elif (self.pieces[0].pos[1] < 0 or self.pieces[0].pos[1] >= tilesVert): state = GameState.gameover
        elif (state == GameState.gameover):
            if self.gameOver.shouldRestart() != None:
                self.restart()
                state = self.gameOver.shouldRestart()
                self.gameOver.newState = None

    def restart(self):
        global speed
        global score
        global state
        score = 0
        speed = startSpeed
        self.pieces.clear()
        self.apples.clear()
        self.pieces = [SnakePiece([int(tilesHori / 2), int(tilesVert / 2)], [True, False], self.headImage, True)] # start in center moving right
        self.apples = [Apple(self.appleImage, self.pieces)]

    def appendPiece(self, pos, dir, turns):
        sp = SnakePiece(pos[:], dir[:], self.bodyImage, False)
        sp.turns = turns[:]
        if (dir == [True, False]): sp.pos[0] -= 1
        elif (dir == [-True, False]): sp.pos[0] += 1
        elif (dir == [False, True]): sp.pos[1] -= 1
        else: sp.pos[1] += 1
        sp.updatePos(0)
        self.pieces.append(sp)

    def render(self, screen):
        global tilesHori
        global tilesVert
        global state
        # draw background
        for y in range(tilesVert):
            for x in range(tilesHori):
                screen.fill((30 - self.colors[x + y * tilesHori], 31 - self.colors[x + y * tilesHori], 33 - self.colors[x + y * tilesHori]), self.rects[x + y * tilesHori])

        # draw apples
        for apple in self.apples:
            apple.render(screen)

        # draw snake
        for piece in self.pieces:
            piece.render(screen)

        if state == GameState.menu:
            self.menu.render(screen)
        elif state == GameState.gameover:
            self.gameOver.render(screen)     

    def collide(self, pos1, pos2):
        return pos1 == pos2

    def keyDown(self, key):
        global state
        if (state == GameState.play):
            if (len(self.pieces[0].turns) > 0):
                for piece in self.pieces:
                    del piece.turns[-1]
            if key == pg.K_UP:
                for piece in self.pieces:
                    piece.turns.append([self.pieces[0].pos[:], [0, -1]]) # make copy of 'pos' instead of reference by adding '[:]'
            elif key == pg.K_RIGHT:
                for piece in self.pieces:
                    piece.turns.append([self.pieces[0].pos[:], [1, 0]])
            elif key == pg.K_DOWN:
                for piece in self.pieces:
                    piece.turns.append([self.pieces[0].pos[:], [0, 1]])
            elif key == pg.K_LEFT:
                for piece in self.pieces:
                    piece.turns.append([self.pieces[0].pos[:], [-1, 0]])
            elif key == pg.K_ESCAPE:
                state = GameState.menu
        elif (state == GameState.menu):
            self.menu.keyDown(key)
        elif state == GameState.gameover:
            self.gameOver.keyDown(key)

class Game:
    def __init__(self):
        global width
        global height
        self.color = (16, 16, 16)
        self.screen = pg.display.set_mode([int(width), int(height)])
        pg.display.set_caption("Snake")
        self.level = Level()

    def update(self, dt):
        self.level.update(dt)

    def render(self):
        self.screen.fill(self.color)
        self.level.render(self.screen)
        pg.display.flip()

    def keyDown(self, key):
        self.level.keyDown(key)

class Main:
    def run(self):
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        pg.init()
        self.initGlobals()
        game = Game()
        clock = pg.time.Clock()
        time = 0.0
        while 1:
            for event in pg.event.get():
                if event.type == pg.QUIT: sys.exit()
                if event.type == pg.KEYDOWN: game.keyDown(event.key)
            clock.tick(10000)
            time += clock.get_time()
            if (time >= 1000): # one second elapsed
                time -= 1000
                print(math.floor(clock.get_fps()))
            game.update(clock.get_time())
            game.render()

    def initGlobals(self):
        global font
        font = pg.font.Font("fonts/pixeled/Pixeled.ttf", int(16 * scale))

if (__name__ == "__main__"):
    Main().run()
