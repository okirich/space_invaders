from pygame import *
from random import randint
import pygame

class GameSprite(sprite.Sprite):
    def __init__(self,sp_image,sp_speed,sp_x,sp_y):
        super().__init__()
        self.image = transform.scale(image.load(sp_image),(65,65))
        self.speed = sp_speed

        self.rect = self.image.get_rect()
        self.rect.x = sp_x
        self.rect.y = sp_y
    
    def reset(self):
        window.blit(self.image,(self.rect.x,self.rect.y))

class Player(GameSprite):

    to_reload = 5 #количество выстрелов до перезарядки
    fired = 0 #колличество произведенных выстрелов
    start_reload_time = 0 #время начала перезарядки
    reload_time = 3000 #время требуемое на перезарядку в [мс]
    ready_to_fire = True
    
    def update(self):
        keys = key.get_pressed()
        if keys[K_LEFT] and self.rect.x > 5:
            self.rect.x -= self.speed
        if keys[K_RIGHT] and self.rect.x < win_w - 80:
            self.rect.x += self.speed
    
    def fire(self):
        if self.ready_to_fire:
            self.fired += 1
            bullet = Bullet(img_bullet,-15,self.rect.centerx,self.rect.top)
            bullet_group.add(bullet)
            if self.fired == self.to_reload:
                self.ready_to_fire = False
                self.start_reload_time = pygame.time.get_ticks()
        else:
            self.reload()        

    def reload(self):
        if self.start_reload_time + self.reload_time <= pygame.time.get_ticks():
            self.fired = 0
            self.ready_to_fire = True

class Enemy(GameSprite):
    def update(self):
        self.rect.y += self.speed
        if self.rect.y > win_h:
            self.rect.x = randint(80,win_w - 80)
            self.rect.y = 0
            global lost 
            lost += 1

class Asteroid(GameSprite):
    def update(self):
        self.rect.y += self.speed
        if self.rect.y > win_h:
            self.rect.x = randint(80,win_w - 80)
            self.rect.y = 0

class Bullet(GameSprite):
    def update(self):
        self.rect.y += self.speed
        if self.rect.y < 0:
            self.kill()

class Bonus(GameSprite):
    def update(self):
        self.rect.y += self.speed
        if self.rect.y > win_h:
            self.rect.x = randint(80,win_w - 80)
            self.rect.y = 0
            global lost 
            lost += 1

win_w = 1200
win_h = 800
### картинки
img_back = 'galaxy.jpg'     #фоновая картинка
img_player = 'rocket.png'   #картинка игрока
img_enemy = 'ufo.png'       #картинка противника
img_bullet = 'bullet.png'   #картинка снаряда
img_asteroid = 'asteroid.png' #картинка астероида
img_bonus = 'bonus.png' #картинка бонуса жизни
img_bonus_2 = 'super_speed.png' #картинка бонуса скорости
### шрифты
font.init()
font1 = font.SysFont('Arial',80)
font2 = font.SysFont('Arial',36)
win = font1.render('YOU WIN!',True,(255,255,255))
lose = font1.render('YOU LOSE!',True,(180,0,0))
### объект фона
window = display.set_mode((win_w,win_h))
display.set_caption('Space Invaders')
background = transform.scale(image.load(img_back),(win_w,win_h))
### объекты игры
ship_speed = 7 #скорость корабля по умолчанию
ship = Player(img_player,ship_speed,win_w/2-25,win_h-100)
bullet_group = sprite.Group()
enemy_group = sprite.Group()
asteroid_group = sprite.Group()

bonus_group_1 = sprite.GroupSingle()
bonus_lives = Bonus(img_bonus,5,randint(80,win_w-80),-40)
bonus_group_1.add(bonus_lives)

bonus_group_2 = sprite.GroupSingle()
bonus_superspeed = Bonus(img_bonus_2,5,randint(80,win_w-80),-40)
bonus_group_2.add(bonus_superspeed)


for _ in range(5):
    en = Enemy(img_enemy,randint(1,5),randint(80,win_w-80),-40)
    enemy_group.add(en)
for _ in range(3):
    ast = Asteroid(img_asteroid,randint(1,5),randint(80,win_w-80),-40)
    asteroid_group.add(ast)

### фоновая музыка
mixer.init()
mixer.music.load('space.ogg')
mixer.music.play()
### звуковые эффекты
fire_sound = mixer.Sound('fire.ogg')
### переменные для игры
finish = False
run = True
score = 0 #сбито врагов
lost = 0 #пропущено врагов
max_lost = 3 #проиграл если пропустил столько(без учета бонусов)
round = 30000 #время раунда в мс

while run:
    for e in event.get():
        if e.type == QUIT:
            run = False
        elif e.type == KEYDOWN:
            if e.key == K_SPACE:
                ship.fire()
                fire_sound.play()
            
                
    #основные действия игрового цикла
    if not finish:
        window.blit(background,(0,0))
        cntr = font2.render('Счет:' + str(score),True,(255,255,255))
        lost_ = font2.render('Пропущено:' + str(lost),True,(255,255,255))
        window.blit(cntr,(10,20))
        window.blit(lost_,(10,50))
        ship.update()
        ship.reset()
        bonus_group_1.update()
        bonus_group_1.draw(window)
        bonus_group_2.update()
        bonus_group_2.draw(window)
        enemy_group.update()
        enemy_group.draw(window)
        bullet_group.update()
        bullet_group.draw(window)
        asteroid_group.update()
        asteroid_group.draw(window)

        c_time = pygame.time.get_ticks()
        #набор очков и обработка попаданий

        collides_b_e = sprite.groupcollide(enemy_group,bullet_group,True,True)
        collides_b_a = sprite.groupcollide(asteroid_group,bullet_group,False,True)
        for c in collides_b_e:
            score += 1
            en = Enemy(img_enemy,randint(1,5),randint(80,win_w-80),-40)
            enemy_group.add(en)

        if sprite.spritecollide(ship,enemy_group,False) or lost >= max_lost \
            or sprite.spritecollide(ship,asteroid_group,False):
            finish = True
            window.blit(lose,(win_w/2 - 150,win_h/2 - 50))
        
        if sprite.spritecollide(ship,bonus_group_1,True):
            max_lost += 3
        
        if sprite.spritecollide(ship,bonus_group_2,True):
            ship_speed *= 2
            ship = Player(img_player,ship_speed,win_w/2-25,win_h-100)

        if c_time > round: 
            finish = True
            window.blit(win,(win_w/2 - 150,win_h/2 - 50)) 

        display.update()

    time.delay(50)
