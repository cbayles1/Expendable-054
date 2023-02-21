import pygame as pg
from settings import *
from os import path
import time
import io, base64

class Map:
    def __init__(self, game, lev):
        self.game = game
        self.data = lev
        self.tileWidth = len(self.data[0])      #MAP WIDTH IN TILES
        self.tileHeight = len(self.data)      #MAP HEIGHT IN TILES
        self.pixelWidth = self.tileWidth * TILESIZE      #MAP WIDTH IN PIXELS
        self.pixelHeight = self.tileHeight * TILESIZE      #MAP HEIGHT IN PIXELS

class Spritesheet:
    def __init__(self, game, filename):
        self.game = game
        self.spritesheet = pg.image.load(io.BytesIO(base64.b64decode(filename))).convert()
    def getImage(self, x, y, w, h, diffWidth=TILESIZE, diffHeight=TILESIZE):
        prospectWidth = diffWidth
        prospectHeight = diffHeight
        image = pg.Surface((w,h))
        image.blit(self.spritesheet, (0,0), (x,y,w,h))
        image = pg.transform.scale(image, (prospectWidth, prospectHeight))
        return image

class Camera:
    def __init__(self, game, w,h):
        self.camera = pg.Rect((0,0,w,h))
        self.game = game
        self.width = w
        self.height = h

    def apply(self, entity, isRect=False):        #APPLIES CAMERA OFFSET TO SPRITE WHEN BLITTING TO SCREEN
        if not isRect: return entity.rect.move(self.camera.topleft)
        if isRect: return entity.move(self.camera.topleft)

    def update(self, target, updateX=True, updateY=True):       #MOVES CAMERA TO TARGET SPRITE
        if updateX:
            x = -target.rect.x + int(WIDTH / 2)
            x = min(0, x)
            x = max(-(self.width - WIDTH), x)
            self.camera.x = x
        if updateY:
            y = -target.rect.y + int(WIDTH / 3)
            y = min(0, y)
            y = max(-(self.height - HEIGHT), y)
            self.camera.y = y        

def drawText(self, msg, size, color, x, y, foonti=FONT_1, screen=None):
    font = pg.font.Font(io.BytesIO(base64.b64decode(foonti)), size)
    text_surface = font.render(msg, False, color)
    text_rect = text_surface.get_rect()
    text_rect.midtop = (x,y)
    if screen == None: screen = self.screen
    screen.blit(text_surface, text_rect)
    return text_rect

def drawTextWithBox(self, msg, size, x, y, textColor=WHITE, boxColor=NAVY, screen=None):
    joe = pg.Surface((WIDTH, HEIGHT))
    rect = drawText(self, msg, size, textColor, x, y, FONT_1, joe)
    bob = pg.Surface((rect.w + 20, rect.h + 20))
    bob.fill(boxColor)
    bob.set_alpha(167)
    if screen == None: screen = self.background
    screen.blit(bob, (rect.x - 10, rect.y - 10))
    drawText(self, msg, size, textColor, x, y, FONT_1, screen)

def fadeIn(self, width, height, color=BLACK, speed=1.025):
    cover = pg.Surface((width, height))
    cover.fill(color)
    alpha = 255                      #threshold
    while alpha >= 16:
        cover.set_alpha(alpha)
        self.draw(noUpdate=True)
        self.screen.blit(cover, (0,0))
        pg.display.update()
        alpha = alpha ** (1/speed)     #fadeSpeed

def fadeOut(self, width, height, color=BLACK):
    cover = pg.Surface((width, height))
    cover.fill(color)
    alpha = 16                       #threshold
    while alpha <= 255:
        cover.set_alpha(alpha)
        self.draw(noUpdate=True)
        self.screen.blit(cover, (0,0))
        pg.display.update()
        alpha = alpha ** 1.025       #fadeSpeed

def fadeFull(self, width, height, color, sleepTime):
    fadeOut(self, width, height, color)
    time.sleep(1)
    fadeIn(self, width, height, color)

def scrollMenu(game, spots, index, speed=0.025):
    spot = spots[int(index)]
    keys = pg.key.get_pressed()
    if keys[pg.K_DOWN] or keys[pg.K_s]: index += speed
    elif keys[pg.K_UP] or keys[pg.K_w]: index -= speed
    if pg.joystick.get_count() > 0:
        axes = game.joysticks[0].get_numaxes()
        axis = game.joysticks[0].get_axis(1)
        if axis > 0.5: index += speed
        if axis < -0.5: index -= speed
    if index >= len(spots): index = 0
    elif index < 0: index = len(spots) - 1
    spot = spots[int(index)]
    return index

def setupControllers(self):
    self.joysticks = []
    for i in range(0, pg.joystick.get_count()):
        self.joysticks.append(pg.joystick.Joystick(i))
        self.joysticks[-1].init()
        print("Detected joystick: '" + self.joysticks[-1].get_name() + "'")

def drawMenuBox(self, x, y, width, height, boxColor, borderColor, borderSize=6):
    pg.draw.rect(self.screen, borderColor, (x - borderSize, y - borderSize, width + borderSize * 2, height + borderSize * 2))
    pg.draw.rect(self.screen, boxColor, (x, y, width, height))

def animateSprite(index, imageArray, delayTime=DEFAULT_ANIMATION_DELAY, suspend=False, joe=False):
    arrLen = len(imageArray)
    index += delayTime
    if joe: print(index)
    if index >= arrLen: 
        if suspend: index = arrLen - 1
        else: index = 0
    return imageArray[int(index)], index

def prepForDamage(target):
    target.damageAnimationIndex = 0
    target.damageFlag = False

def damageEffects(target, game, speed=(20/3), loseLives=True):
    if target.damageFlag and not game.moribund and not game.victorious:
        if target.damageAnimationIndex < 3 and not game.haste:
            target.damageAnimationIndex += speed * 0.025
            if 1 <= target.damageAnimationIndex < 2: target.image.set_alpha(64)
            if 2 <= target.damageAnimationIndex < 3: target.image.set_alpha(122)
            else: target.image.set_alpha(32)
            target.image.set_colorkey(YELLOW)
            if target.damageAnimationIndex >= 3:
                target.damageAnimationIndex = 0
                target.damageFlag = False
                if loseLives: 
                    target.lives -= 1
                    if target.lives <= 0 and target.source != "avatar": target.kill()

def erase(surf, sourceRect, destPos):
    surf.blit(surf, destPos, sourceRect)
    return surf

def eraseLight(background, lightIndex, storyIndex):
    if lightIndex == 0: x = 54
    elif lightIndex == 1: x = 132
    elif lightIndex == 2: x = 212
    elif lightIndex == 3: x = 291
    elif lightIndex == 4: x = 371
    elif lightIndex == 5: x = 450
    x *= 4
    y = 48 + 6 * 48 * storyIndex
    erase(background, pg.Rect(172,48,24,32), (x,y))

def wait(time, function_one=None):
    now = pg.time.get_ticks()
    last_wait = pg.time.get_ticks()
    while now < time + last_wait: 
        if function_one == None: 
            for event in pg.event.get(): pass
        else: 
            function_one()
        now = pg.time.get_ticks()

def rectOnScreen(rect, camera):
    if camera == None: r = rect
    else: r = camera.apply(rect, True)
    if r.left <= WIDTH and r.right >= 0 and r.top <= HEIGHT and r.bottom >= 0: return True
    else: return False