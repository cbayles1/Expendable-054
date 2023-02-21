import pygame as pg
import random
from settings import *
from other import *
vec = pg.math.Vector2

class Static(pg.sprite.Sprite):
    def __init__(self, game, x,y, groups, img):
        pg.sprite.Sprite.__init__(self, groups)
        self.image = img
        self.game = game
        self.rect = self.image.get_rect()
        self.pos = vec(x * TILESIZE, y * TILESIZE)
        self.rect.topleft = self.pos
class Obstacle(Static):
    def __init__(self, game, x,y, groups, img):
        super().__init__(game, x,y, groups, img)
class Wall(Obstacle):
    def __init__(self, game, x,y):
        self.groups = game.all_sprites, game.statics, game.obstacles, game.walls
        if y % 6 == 0: self.image = game.wall2Img
        elif y % 2 == 0: self.image = game.wall1Img
        else: self.image = game.wall0Img
        super().__init__(game, x,y, self.groups, self.image)
class Floor(Obstacle):
    def __init__(self, game, x, y, img=None):
        self.groups = game.all_sprites, game.statics, game.obstacles, game.floors
        if img == None: self.image = game.floor0Img
        else: self.image = img
        super().__init__(game, x,y, self.groups, self.image)
class PowerUp(Static):
    def __init__(self, game, x, y, type):
        self.groups = game.all_sprites, game.statics, game.powerUps
        self.last_hover = pg.time.get_ticks()
        self.state = 0
        if type == 8: 
            self.type = "grapple"
            self.image = game.grappleImg
        elif type == 9: 
            self.type = "life"
            self.image = game.lifeImg
        elif type == 10: 
            self.type = "minigun"
            self.image = game.minigunImg
        elif type == 11: 
            self.type = "stealth"
            self.image = game.stealthImg
        self.image.set_colorkey(YELLOW)
        super().__init__(game, x,y, self.groups, self.image)
        if type == 8 and game.levelNum == 1: 
            self.rect.x -= 0.5 * TILESIZE
            self.rect.y += 0.5 * TILESIZE
        self.rect.y -= 7

    def update(self):
        now = pg.time.get_ticks()
        if now > self.last_hover + 500:
            self.last_hover = now
            if self.state == 0: 
                self.rect.y += 7
                self.state = 1
            elif self.state == 1:
                self.rect.y -= 7
                self.state = 0

class Sensor(Static):
    def __init__(self, game, x,y, groups, img):
        super().__init__(game, x,y, groups, img)
class Door(Sensor):
    def __init__(self, game, x,y, midLevel=False):
        self.groups = game.all_sprites, game.statics, game.sensors, game.doors
        if x == 0: self.image = game.doorFirstImg
        else: 
            self.image = game.doorFinalImg
        self.midLevel = midLevel
        super().__init__(game, x,y, self.groups, self.image)
class Window(Sensor):
    def __init__(self, game, x,y):
        self.groups = game.all_sprites, game.statics, game.sensors, game.windows
        self.image = game.windowImg
        self.image.set_colorkey(YELLOW)
        self.broken = False
        self.breakAnimateIndex = 0
        self.breaking = False
        super().__init__(game, x,y, self.groups, self.image)

    def update(self):
        if self.breaking: 
            self.image, self.breakAnimateIndex = animateSprite(self.breakAnimateIndex, [self.game.windowCrackedImg, self.game.windowGoneImg], 0.1)
            if self.breakAnimateIndex > 1:
                self.breaking = False
        self.image.set_colorkey(YELLOW)
class Elevator(Sensor):
    def __init__(self, game, x,y, door):
        self.groups = game.all_sprites, game.statics, game.sensors, game.elevators
        self.image = game.elevator0Img
        super().__init__(game, x,y, self.groups, self.image)
        self.rect.bottom -= 32
        self.door = door
        self.elevateForAnimation = 0
        self.animateIndex = 0
    
    def update(self):
        if self.elevateForAnimation == 1: 
            self.image, self.animateIndex = animateSprite(self.animateIndex, [
                self.game.elevator0Img, self.game.elevator1Img, self.game.elevator2Img, 
                self.game.elevator3Img, self.game.elevator4Img, self.game.elevator4Img], 
                delayTime=0.5, suspend=True)
        elif self.elevateForAnimation == 2:
            self.image, self.animateIndex = animateSprite(self.animateIndex, [
                self.game.elevator4Img, self.game.elevator4Img, self.game.elevator3Img, 
                self.game.elevator2Img, self.game.elevator1Img, self.game.elevator0Img],
                delayTime=0.5, suspend=True)
class FallFloor(Sensor):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.statics, game.sensors, game.fallFloors
        self.image = game.fallFloorImg
        super().__init__(game, x,y, self.groups, self.image)
        self.acc = vec(0,0)
        self.vel = vec(0,0)
        self.acc.y = 0
        self.smushAnimateIndex = 0
        self.smushing = False
    
    def update(self):
        if self.acc.y == 0: return
        elif self.acc.y == GRAVITY:
            self.vel.y += self.acc.y
            self.pos.y += self.vel.y + 0.5 * self.acc.y
            self.rect.topleft = self.pos
class LaserEnd(Static):
    def __init__(self, game, x,y, img, xPixelDiff, yPixelDiff):
        self.groups = game.all_sprites, game.statics, game.obstacles, game.laserEnds
        super().__init__(game, x,y, self.groups, img)
        self.rect = self.image.get_rect()
        self.rect.topleft = vec(x * TILESIZE + xPixelDiff * 4, y * TILESIZE + yPixelDiff * 4)
class LaserBeam(Sensor):
    def __init__(self, game, x,y, img, xPixelDiff, yPixelDiff):
        self.groups = game.all_sprites, game.statics, game.sensors, game.laserBeams
        super().__init__(game, x,y, self.groups, img)
        self.rect = self.image.get_rect()
        self.rect.topleft = vec(x * TILESIZE + xPixelDiff * 4, y * TILESIZE + yPixelDiff * 4)
        self.state = 1
        self.last_switch = 0

    def update(self):
        now = pg.time.get_ticks()
        if self.state == 0:
            self.image.set_alpha(0)
            if now - self.last_switch > LASER_DELAY:
                self.last_switch = now
                self.state = 1
        elif self.state == 1:
            self.image.set_alpha(255)
            if now - self.last_switch > LASER_DELAY:
                self.last_switch = now
                self.state = 0
class CollDecor(Obstacle):
    def __init__(self, game, x,y, tile):
        self.groups = game.all_sprites, game.statics, game.obstacles, game.decor
        xPixelDiff = 0
        yPixelDiff = 0
        self.source = "decor"
        self.destroy = False
        if tile == 28:
            self.image = game.darkTableImg 
        elif tile == 29: 
            self.image = game.televisionImg
            xPixelDiff = 6
            yPixelDiff = 0
            self.destroy = True
        elif tile == 30: self.image = game.brightTableImg
        elif tile == 31: self.image = game.stoolUpImg
        elif tile == 32: 
            self.image = game.stoolDownImg
            yPixelDiff = 4
        elif tile == 33: 
            self.image = game.testTubesImg
            self.destroy = True
            yPixelDiff = 6
        if self.destroy and game.treePowers: 
            yPixelDiff = 2
            self.image = game.treeImg
        super().__init__(game, x,y, self.groups, self.image)
        #self.rect = self.image.get_rect()
        if self.destroy: 
            prepForDamage(self)
            self.lives = 1
        self.rect.topleft = vec(x * TILESIZE + xPixelDiff * 4, y * TILESIZE + yPixelDiff * 4)
    def update(self):
        if self.game.freezeUpdate == "decor": return
        if self.game.treePowers and self.destroy: self.image = self.game.treeImg
        if self.destroy and self.damageFlag: damageEffects(self, self.game, 5)
class GhostDecor(Static):
    def __init__(self, game, x,y, tile):
        self.groups = game.all_sprites, game.statics, game.decor
        xPixelDiff = 0
        yPixelDiff = 0
        self.source = "decor"
        self.destroy = False
        if tile == 34: 
            self.image = game.flaskImg
            self.destroy = True
            yPixelDiff = 1
            xPixelDiff = 6
        elif tile == 35: 
            self.image = game.desktopImg
            yPixelDiff = 5
        elif tile == 36: 
            self.image = game.darkChairImg
            yPixelDiff = 2
        elif tile == 37: self.image = game.fireExtinguisherImg
        elif tile == 38: 
            yPixelDiff = -2
            self.image = game.treeImg
        elif tile == 39:
            self.image = game.crateImg
            yPixelDiff = -5.5
            self.destroy = True
        if game.valentine: self.image = game.lifeImg
        super().__init__(game, x,y, self.groups, self.image)
        self.rect = self.image.get_rect()
        self.vel = vec(0,0)
        self.pos = vec(x * TILESIZE, y * TILESIZE)
        if self.destroy:
            self.lives = 1
            prepForDamage(self)
        self.rect.topleft = vec(x * TILESIZE + xPixelDiff * 4, y * TILESIZE + yPixelDiff * 4)
    def update(self):
        if self.game.freezeUpdate == "decor": return
        if self.game.valentine: self.image = self.game.lifeImg
        if self.destroy and self.damageFlag: damageEffects(self, self.game, 5)
class DepthStatic(Static):
    def __init__(self, game, x,y, image, coll=False, fallFloor=False):
        self.image = image
        if coll: self.groups = game.all_sprites, game.statics, game.obstacles, game.depthStatics
        elif fallFloor: self.groups = game.all_sprites, game.statics, game.depthStatics, game.fallFloorDepthStatics
        else: self.groups = game.all_sprites, game.statics, game.depthStatics
        super().__init__(game, x,y, self.groups, self.image)
        if coll: self.rect.x += 28
class Acid(Static):
    def __init__(self, game, x, y, top=False):
        self.groups = game.all_sprites, game.statics, game.sensors, game.acids
        self.top = top
        self.animateIndex = 0
        if top: self.image = random.choice([game.acidTop0Img, game.acidTop1Img])
        else: self.image = random.choice([game.acidPit0Img, game.acidPit1Img])
        super().__init__(game, x, y, self.groups, self.image)

    def update(self):
        if self.top: 
            self.animateIndex += 0.15
            if self.animateIndex >= 1:
                if self.image == self.game.acidTop0Img:
                    self.image = self.game.acidTop1Img
                    self.animateIndex = 0
                else:
                    self.image = self.game.acidTop0Img
                    self.animateIndex = 0
                self.image.set_colorkey(YELLOW)
class Clone(Static):
    def __init__(self, game, x,y):
        self.groups = game.all_sprites, game.statics, game.clones
        self.image = game.cloneImg
        super().__init__(game,x,y, self.groups, self.image)

class Avatar(pg.sprite.Sprite):
    def __init__(self, game, x, y):
        self.groups = game.all_sprites, game.kinetics
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.height = TILESIZE / 1.6
        self.image = game.avatarIdle0Img
        self.rect = self.image.get_rect()
        self.pos = vec(x * TILESIZE, y * TILESIZE)
        self.vel = vec(0,0)
        self.acc = vec(0,GRAVITY)
        self.rect.topleft = self.pos
        self.jumping = False
        self.lives = 3
        self.para = False
        self.last_shot = 0
        self.last_stealth = 0
        self.grapplehookCount = 0
        self.orientation = 1 
        self.paraTorn = False
        self.nearLadder = False
        self.last_injury = 0
        self.invulnerable = False
        self.tryElevator = False
        self.nearElevator = False
        self.elevatingIndex = 0
        self.inventory = []
        self.lastMinigunInit = 0
        self.stealth = False
        self.crouching = False
        self.shootingForAnimation = False
        self.jumpAnimateIndex = 0
        self.idleAnimateIndex = 0
        self.runAnimateIndex = 0
        self.paraAnimateIndex = 0
        self.crouchAnimateIndex = 0
        self.shootAnimateIndex = 0
        self.dyingAnimateIndex = 0
        self.wakka = False
        self.source = "avatar"
        prepForDamage(self)

    def update(self):
        if self.game.freezeUpdate == "avatar": return
        if self.orientation < 0: 
            self.image, self.runAnimateIndex = animateSprite(self.runAnimateIndex, [self.game.avatarLeftRun0Img, self.game.avatarLeftRun1Img, self.game.avatarLeftRun2Img, self.game.avatarLeftRun3Img])
        elif self.orientation > 0:
            self.image, self.runAnimateIndex = animateSprite(self.runAnimateIndex, [self.game.avatarRightRun0Img, self.game.avatarRightRun1Img, self.game.avatarRightRun2Img, self.game.avatarRightRun3Img])
        else: 
            self.image = self.game.avatarIdle0Img
        self.image.set_colorkey(YELLOW)
        if 1 > self.vel.x > -1: 
            if self.orientation < 0: self.image, self.idleAnimateIndex = animateSprite(self.idleAnimateIndex, [pg.transform.flip(self.game.avatarIdle0Img, True, False), pg.transform.flip(self.game.avatarIdle0Img, True, False), pg.transform.flip(self.game.avatarIdle1Img, True, False)])
            elif self.orientation > 0: self.image, self.idleAnimateIndex = animateSprite(self.idleAnimateIndex, [self.game.avatarIdle0Img, self.game.avatarIdle0Img, self.game.avatarIdle1Img])
        if self.shootingForAnimation: 
            if 1 > self.vel.x > -1:
                if self.orientation < 0: self.image = self.game.avatarLeftShoot0Img
                elif self.orientation > 0: self.image = self.game.avatarRightShoot0Img
            else:
                if self.orientation < 0: self.image, self.idleAnimateIndex = animateSprite(self.idleAnimateIndex, [self.game.avatarLeftShoot1Img, self.game.avatarLeftShoot2Img, self.game.avatarLeftShoot3Img, self.game.avatarLeftShoot4Img])
                elif self.orientation > 0: self.image, self.idleAnimateIndex = animateSprite(self.idleAnimateIndex, [self.game.avatarRightShoot1Img, self.game.avatarRightShoot2Img, self.game.avatarRightShoot3Img, self.game.avatarRightShoot4Img])
            now = pg.time.get_ticks()
            if now - self.last_shot > AVAT_BULLET_DELAY / 1.5:
                self.shootingForAnimation = False
                self.image = self.game.avatarIdle0Img
            self.image.set_colorkey(YELLOW)
        self.rect = pg.Rect((self.pos.x, self.pos.y, TILESIZE, self.height))
        self.acc.x += self.vel.x * -self.game.friction
        self.vel += self.acc
        if self.crouching: self.pos.x += (self.vel.x + 0.5 * self.acc.x) / 2
        else: self.pos.x += self.vel.x + 0.5 * self.acc.x
        self.pos.y += self.vel.y + 0.5 * self.acc.y
        self.rect.x = self.pos.x
        self.collide_with_obstacles('x')
        self.rect.y = self.pos.y
        self.collide_with_obstacles('y')
        if self.rect.right <= 0 or self.rect.left >= self.game.map.pixelWidth or self.rect.bottom <= 0 or self.rect.top >= self.game.map.pixelHeight:
            def restartSign():
                drawMenuBox(self.game, WIDTH / 3.25, HEIGHT / 3, WIDTH / 2.5, HEIGHT / 4, NAVY, GREY)
                drawText(self.game, "RESTARTING", 64, WHITE, WIDTH / 2, HEIGHT / 2.5)
                for event in pg.event.get(): pass
                pg.display.flip()
            wait(2000, restartSign)
            self.game.restart()
        if self.crouching and self.height != TILESIZE:
            self.rect.y += 1
            hits = pg.sprite.spritecollide(self, self.game.obstacles, False)
            self.rect.y -= 1
            if hits:
                if self.orientation == 1: self.image = self.game.avatarRightCrouchImg
                else: self.image = self.game.avatarLeftCrouchImg
                self.image.set_colorkey(YELLOW)
                self.rect = self.image.get_rect()
                self.rect.y = self.pos.y + 3 * 6 + 12
                self.rect.x = self.pos.x
                self.vel.x = 0
        if self.lives <= 0:
            self.game.game_over()
            return
        if self.lives > 3: self.lives = 3
        if not self.para:
            self.height = TILESIZE * 2
            self.acc.y = GRAVITY
        if self.para:
            self.height = TILESIZE * 3 - 10
            self.acc.y = 0
            self.vel.y = GRAVITY * 4
            self.rect.y = self.pos.y
        if self.game.currentStageType == 1 and self.paraTorn == False:
            self.para = True
        if self.game.currentStageType == 0:
            self.para = False
        if self.jumping or self.vel.y > GRAVITY:
            if self.para: 
                if self.vel.x < 0: self.image, self.paraAnimateIndex = animateSprite(self.paraAnimateIndex, [self.game.avatarLeftPara0Img, self.game.avatarLeftPara1Img, self.game.avatarLeftPara2Img, self.game.avatarLeftPara3Img])
                else: self.image, self.paraAnimateIndex = animateSprite(self.paraAnimateIndex, [self.game.avatarRightPara0Img, self.game.avatarRightPara1Img, self.game.avatarRightPara2Img, self.game.avatarRightPara3Img])
            else: 
                if self.vel.x < 0: self.image, self.jumpAnimateIndex = animateSprite(self.jumpAnimateIndex, [self.game.avatarLeftJump0Img, self.game.avatarLeftJump1Img, self.game.avatarLeftJump2Img, self.game.avatarLeftJump3Img])
                else: self.image, self.jumpAnimateIndex = animateSprite(self.jumpAnimateIndex, [self.game.avatarRightJump0Img, self.game.avatarRightJump1Img, self.game.avatarRightJump2Img, self.game.avatarRightJump3Img])
        if self.stealth:
            now = pg.time.get_ticks()
            if now - self.last_stealth > POWERUP_TIMEOUT:
                self.stealth = False
                self.inventory.remove("stealth")
                self.last_stealth = 0
        if self.grapplehookCount < 0: 
            self.grapplehookCount = 0
            if "grapple" in self.inventory: self.inventory.remove("grapple")
        if self.grapplehookCount > 3: self.grapplehookCount = 3
        if self.wakka: 
            if self.orientation < 0: self.image, self.runAnimateIndex = animateSprite(self.runAnimateIndex, [self.game.pacLeft0Img, self.game.pacLeft1Img])
            else: self.image, self.runAnimateIndex = animateSprite(self.runAnimateIndex, [self.game.pacRight0Img, self.game.pacRight1Img], delayTime=0.05)
            self.image.set_colorkey(BLACK)
            for bullet in self.game.bullets:
                bullet.image = self.game.cherryImg
                bullet.image.set_colorkey(YELLOW)
        else: self.image.set_colorkey(YELLOW)
        if self.stealth: self.image.set_alpha(122)
        else: self.image.set_alpha(255)
        if self.damageFlag: damageEffects(self, self.game)

    def collide_with_obstacles(self, direction):
        obstacleHits = pg.sprite.spritecollide(self, self.game.obstacles, False)
        if obstacleHits:
            rect = obstacleHits[0].rect
            if direction == 'x':
                if self.vel.x > 0:
                    self.pos.x = (rect.left - self.rect.width)
                if self.vel.x < 0:
                    self.pos.x = rect.right
                self.rect.x = self.pos.x
            elif direction == 'y':
                if self.vel.y > 0:
                    self.pos.y = (rect.top - self.rect.height)
                    if self.vel.y > GRAVITY * 54 and self.game.currentStageType == 1:
                        self.lives -= 3
                    if self.para:
                        self.paraTorn = True
                        self.para = False
                if self.vel.y < 0:
                    self.pos.y = rect.bottom
                self.vel.y = 0
                self.rect.y = self.pos.y
                self.jumping = False

    def jump(self):
        self.rect.y += 1
        hits = pg.sprite.spritecollide(self, self.game.obstacles, False)
        self.rect.y -= 1
        if hits and not self.jumping and not self.para:
            self.jumping = True
            self.acc.y = -AVATAR_JUMP
            self.game.effectsChannel.play(self.game.jumpSound)

    def jumpCut(self):
        if self.jumping and self.vel.y < -2 * AVATAR_JUMP:
            self.vel.y = -2 * AVATAR_JUMP

    def fireBullet(self):
        now = pg.time.get_ticks()
        if self.game.grappleLine or self.para: return
        if self.crouching and not self.game.bond: return
        if self.vel.x < 0: spawn = self.rect.left
        else: spawn = self.rect.right
        if now - self.last_shot > AVAT_MINIGUN_DELAY and "minigun" in self.inventory and now < POWERUP_TIMEOUT * 1.5 + self.lastMinigunInit:
            self.last_shot = now
            Bullet(self.game, vec(spawn, self.rect.top + TILESIZE / 2), vec(self.orientation * self.game.bulletSpeed, 0), "avatar", img=self.game.bloodBulletImg)
        elif now - self.last_shot > AVAT_BULLET_DELAY:
            if "minigun" in self.inventory: self.inventory.remove("minigun")
            self.last_shot = now
            Bullet(self.game, vec(spawn, self.rect.top + TILESIZE / 11 * 5), vec(self.orientation * self.game.bulletSpeed, 0), "avatar")
        self.shootingForAnimation = True

    def injury(self, damage):
        self.invulnerable = True
        now = pg.time.get_ticks()
        if now - self.last_injury > INVULNERABLE_TIME:
            self.last_injury = now
            self.invulnerable = False
        if not self.invulnerable:
            self.game.effectsChannel.play(self.game.damageSound)
            self.damageFlag = True

    def grappleCollCheck(self):
        self.rect.y += 1
        hits1 = pg.sprite.spritecollide(self, self.game.obstacles, False)
        self.rect.y -= 2
        hits2 = pg.sprite.spritecollide(self, self.game.obstacles, False)
        self.rect.y += 1        
        if hits1 and not hits2: 
            return True
        else: return False

    def pac(self):
        self.colorkey = BLACK
        self.wakka = True
class Baddie(pg.sprite.Sprite):
    def __init__(self, game, groups, x, y, orientation, lives, vel, bulletDelay, imgPair, source):
        pg.sprite.Sprite.__init__(self, groups)
        self.image = imgPair[0][0]
        self.image.set_colorkey(YELLOW)
        self.game = game
        self.rect = self.image.get_rect()
        self.pos = vec(x * TILESIZE, y * TILESIZE - 32)
        self.rect.topleft = self.pos
        self.vel = vec(vel,0)
        self.acc = vec(0, GRAVITY)
        self.last_shot = 0
        self.bulletDelay = bulletDelay
        self.animationIndex = 0
        self.imgPair = imgPair
        self.lives = lives
        self.source = source
        self.orientation = orientation
        self.bulletPos = vec(self.rect.centerx, self.rect.centery - 16)
        prepForDamage(self)
    
    def update(self):
        if self.game.freezeUpdate == self.source: return
        self.vel += self.acc
        self.pos.x += self.vel.x + 0.5 * self.acc.x
        self.pos.y += self.vel.y + 0.5 * self.acc.y
        self.rect.x = self.pos.x
        xColl = self.collide_with_obstacles('x')
        self.rect.y = self.pos.y
        yColl = self.collide_with_obstacles('y')

        self.rect.x += TILESIZE * self.orientation
        self.rect.y += TILESIZE
        obstacleHits = pg.sprite.spritecollide(self, self.game.obstacles, False)
        self.rect.x -= TILESIZE * self.orientation
        self.rect.y -= TILESIZE

        self.rect.x += TILESIZE * self.orientation
        laserHits = pg.sprite.spritecollide(self, self.game.laserBeams, False)
        self.rect.x -= TILESIZE * self.orientation
        self.bulletPos = vec(self.rect.centerx, self.rect.centery - 16)

        onScreen = rectOnScreen(self.rect, self.game.camera)

        if not (obstacleHits or laserHits or self.source == "sniperBadd"):
            self.vel.x *= -1
            self.orientation *= -1
        if self.vel.x > 0: 
            self.orientation = 1
            if onScreen: 
                self.image, self.animationIndex = animateSprite(self.animationIndex, self.imgPair[0])
        elif self.vel.x < 0: 
            self.orientation = -1
            if onScreen: 
                self.image, self.animationIndex = animateSprite(self.animationIndex, self.imgPair[1])

        if self.lives <= 0 and not self.source == "doc": self.kill()
        if not self.source == "doc": self.fireBullet()
        if onScreen:
            self.image.set_colorkey(YELLOW)
            self.image.set_alpha(255)
        if self.damageFlag: damageEffects(self, self.game)

    def fireBullet(self):
        if (self.rect.bottom <= self.game.avatar.rect.bottom + TILESIZE and self.rect.top + TILESIZE * 5 >= self.game.avatar.rect.top) and not self.game.avatar.stealth:
            now = pg.time.get_ticks()
            if now - self.last_shot > self.bulletDelay:
                self.last_shot = now
                Bullet(self.game, self.bulletPos, vec(self.orientation * self.game.bulletSpeed, 0), source=self.source)

    def collide_with_obstacles(self, direction):
        obstacleHits = pg.sprite.spritecollide(self, self.game.obstacles, False)
        if obstacleHits:
            if direction == 'x':
                if self.vel.x > 0:
                    self.pos.x = (obstacleHits[0].rect.left - self.rect.width)
                if self.vel.x < 0:
                    self.pos.x = obstacleHits[0].rect.right
                self.vel.x *= -1
                self.rect.x = self.pos.x
            if direction == 'y':
                if self.vel.y > 0:
                    self.pos.y = obstacleHits[0].rect.top - 1
                if self.vel.y < 0:
                    self.pos.y = obstacleHits[0].rect.bottom + self.rect.height + 1
                self.vel.y = 0
                self.rect.bottom = self.pos.y
class BigBadd(Baddie):
    def __init__(self, game, x, y, orientation):
        self.groups = game.all_sprites, game.kinetics, game.baddies, game.bigBadds
        imgsRight = [game.bigBaddRight0Img, game.bigBaddRight1Img, game.bigBaddRight2Img]
        imgsLeft = [game.bigBaddLeft0Img, game.bigBaddLeft1Img, game.bigBaddLeft2Img]
        super().__init__(game, self.groups, x, y, orientation, 2, BIG_BADD_SPEED, BIG_BADD_BULLET_DELAY, (imgsRight, imgsLeft), "bigBadd")
        
    def update(self):
        super().update()
        if self.vel.y == 0 and self.vel.x == 0: self.vel.x = random.choice([BIG_BADD_SPEED, -BIG_BADD_SPEED])
        if self.game.camera.apply(self.rect, isRect=True).right < 0 or self.game.camera.apply(self.rect, isRect=True).left > WIDTH:
            if self.game.avatar.rect.bottom <= self.rect.bottom and self.rect.top - TILESIZE * 3 <= self.game.avatar.rect.top:
                if self.game.avatar.rect.right < self.rect.left: 
                    self.vel.x = -BIG_BADD_SPEED
                if self.game.avatar.rect.left < self.rect.right: 
                    self.vel.x = BIG_BADD_SPEED
class QuickBadd(Baddie):
    def __init__(self, game, x, y, orientation):
        self.groups = game.all_sprites, game.kinetics, game.baddies, game.quickBadds
        imgsRight = [game.quickBaddRight0Img, game.quickBaddRight1Img, game.quickBaddRight2Img]
        imgsLeft = [game.quickBaddLeft0Img, game.quickBaddLeft1Img, game.quickBaddLeft2Img]
        super().__init__(game, self.groups, x, y, orientation, 1, QUICK_BADD_SPEED, QUICK_BADD_BULLET_DELAY, (imgsRight, imgsLeft), "quickBadd")

    def update(self):
        super().update()
        if self.vel.y == 0 and self.vel.x == 0: self.vel.x = random.choice([QUICK_BADD_SPEED, -QUICK_BADD_SPEED])
        if self.game.camera.apply(self.rect, isRect=True).right < 0 or self.game.camera.apply(self.rect, isRect=True).left > WIDTH:
            if self.game.avatar.rect.bottom <= self.rect.bottom and self.rect.top - TILESIZE * 3 <= self.game.avatar.rect.top:
                if self.game.avatar.rect.right < self.rect.left: 
                    self.vel.x = -QUICK_BADD_SPEED
                if self.game.avatar.rect.left < self.rect.right: 
                    self.vel.x = QUICK_BADD_SPEED
class SniperBadd(Baddie):
    def __init__(self, game, x,y, orientation):
        self.groups = game.all_sprites, game.kinetics, game.baddies, game.sniperBadds
        super().__init__(game, self.groups, x, y, orientation, 1, 0, SNIPER_BADD_BULLET_DELAY, ([game.sniperBaddRight0Img], [game.sniperBaddLeft0Img]), "sniperBadd")
        self.shootingForAnimation = False
        if orientation < 0: self.pos.x += 4

    def update(self):
        super().update()
        if self.shootingForAnimation:
            if self.orientation > 0: self.image = self.game.sniperBaddRight1Img
            else: self.image = self.game.sniperBaddLeft1Img
            now = pg.time.get_ticks()
            if now - self.last_shot > SNIPER_BADD_BULLET_DELAY / 4:
                self.shootingForAnimation = False
                if self.orientation > 0: self.image = self.game.sniperBaddRight0Img
                else: self.image = self.game.sniperBaddLeft0Img
            self.image.set_colorkey(YELLOW)

    def fireBullet(self):
        if (self.rect.top >= self.game.avatar.rect.bottom - TILESIZE) and not self.game.avatar.stealth: 
            now = pg.time.get_ticks()
            if now - self.last_shot > SNIPER_BADD_BULLET_DELAY:
                self.last_shot = now
                self.shootingForAnimation = True
                originX = self.rect.centerx
                originY = self.rect.centery
                if self.orientation > 0: 
                    originY -= 64
                    originX += 36
                elif self.orientation < 0: 
                    originY -= 56
                    originX -= 36
                bullet = Bullet(self.game, vec(originX, originY), vec(self.orientation * self.game.bulletSpeed / 2, -self.game.bulletSpeed / 2), source="sniperBadd")
                if self.orientation < 0: bullet.image = pg.transform.rotate(bullet.image, -45)
                elif self.orientation > 0: bullet.image = pg.transform.rotate(bullet.image, 45)
class Doc(Baddie):
    def __init__(self, game, x,y):
        self.groups = game.all_sprites, game.statics, game.baddies
        super().__init__(game, self.groups, x, y, -1, 7, 0, 0, ([game.docLeftImg], [game.docLeftImg]), "doc")
        self.speeches = ["*cough* Why'd you do that?!", "Can't you see I'm not a threat?", "I tried to destroy the other clones..", "..with a neurotoxin, but I was too late.", "*cough* The PTDA's coming!", "Get out of here before you..", "..end up like me! Take this!"]
        self.speechIndex = -1
        self.image = self.game.docLeftImg
        self.freddy = False
        self.last_freddy = 0

    def update(self):
        super().update()
        if self.freddy:
            now = pg.time.get_ticks()
            if now > self.last_freddy + 2000: 
                self.game.avatar.jump()
                self.freddy = False

    def flipSpeechBox(self, ogBg):
        if self.speechIndex >= 0:
            if self.speechIndex == 6: PowerUp(self.game, 34, 58, 8)
            if self.speechIndex < len(self.speeches):
                bg = pg.Surface((ogBg.get_width(), ogBg.get_height()))
                bg.blit(ogBg, (0,0))
                new = pg.transform.flip(self.game.avatarIdle0Img, True, False)
                new = pg.transform.scale(new, (int((new.get_width() / 3) * 4), int((new.get_height() / 3) * 4)))
                if self.speechIndex == 1: 
                    self.image.blit(new, (44,140), area=pg.Rect(4,0,28,24))
                    self.freddy = True
                    self.last_freddy = pg.time.get_ticks()
                drawTextWithBox(self.game, self.speeches[self.speechIndex], 36, 24 * TILESIZE, 56 * TILESIZE, screen=bg)
                return bg
            else: return ogBg
        else: return ogBg
class Bullet(pg.sprite.Sprite):
    def __init__(self, game, pos, direction, source, img=None):
        self.groups = game.all_sprites, game.bullets, game.kinetics
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        if img != None: self.image = img
        else: self.image = game.bulletImg
        self.image.set_colorkey(YELLOW)
        self.rect = self.image.get_rect()
        self.direction = direction
        self.pos = vec(pos.x, pos.y)
        self.rect.x = self.pos.x
        self.rect.y = self.pos.y
        self.vel = direction * self.game.bulletSpeed
        if direction.x < 0: self.image = pg.transform.flip(self.image, True, False)
        self.source = source
        if rectOnScreen(self.rect, game.camera): game.effectsChannel.play(self.game.gunSound)

    def update(self):
        self.rect.topleft += self.vel
        if not rectOnScreen(self.rect, self.game.camera): self.kill()
class Grapplehook(pg.sprite.Sprite):
    def __init__(self, game, pos):
        self.groups = game.all_sprites, game.grapplehook, game.kinetics
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.image = self.game.grapplehookImg
        self.image.set_colorkey(YELLOW)
        self.rect = self.image.get_rect()
        self.pos = vec(pos.x, pos.y)
        self.rect.topleft = self.pos
        self.vel = vec(0, GRAPPLEHOOK_SPEED)
        self.game.effectsChannel.play(self.game.grappleSound)

    def update(self):
        self.rect.topleft -= self.vel
        self.game.grappleLine = True
        if self.rect.bottom < 0:
            self.kill()
            self.game.grappleLine = False