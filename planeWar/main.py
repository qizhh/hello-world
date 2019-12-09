import pygame
import sys
import traceback
from pygame.locals import *
from random import *

# from myplane import MyPlane
import myplane
import enemy
import bullet
import supply

pygame.init()
pygame.mixer.init()

bg_size = width, height = 480, 700
screen = pygame.display.set_mode(bg_size)
pygame.display.set_caption('飞机大战')
pygame.mixer.set_num_channels(30)

BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
WHITE = (255, 255, 255)

# background = pygame.image.load('images/background.png').convert()
background = pygame.image.load('images/avengers.png').convert()

# 载入游戏音乐
pygame.mixer.music.load("sound/avengers.ogg")
# pygame.mixer.music.load("sound/game_music.ogg")
pygame.mixer.music.set_volume(0.1)
bullet_sound = pygame.mixer.Sound("sound/bullet.wav")
bullet_sound.set_volume(0.1)
bomb_sound = pygame.mixer.Sound("sound/use_bomb.wav")
bomb_sound.set_volume(0.2)
supply_sound = pygame.mixer.Sound("sound/supply.wav")
supply_sound.set_volume(0.2)
get_bomb_sound = pygame.mixer.Sound("sound/get_bomb.wav")
get_bomb_sound.set_volume(0.2)
get_bullet_sound = pygame.mixer.Sound("sound/get_bullet.wav")
get_bullet_sound.set_volume(0.2)
upgrade_sound = pygame.mixer.Sound("sound/upgrade.wav")
upgrade_sound.set_volume(0.2)
enemy3_fly_sound = pygame.mixer.Sound("sound/enemy3_flying.wav")
enemy3_fly_sound.set_volume(0.2)
enemy1_down_sound = pygame.mixer.Sound("sound/enemy1_down.wav")
enemy1_down_sound.set_volume(0.1)
enemy2_down_sound = pygame.mixer.Sound("sound/enemy2_down.wav")
enemy2_down_sound.set_volume(0.4)
enemy3_down_sound = pygame.mixer.Sound("sound/enemy3_down.wav")
enemy3_down_sound.set_volume(0.5)
me_down_sound = pygame.mixer.Sound("sound/me_down.wav")
me_down_sound.set_volume(0.2)


def add_small_enemies(small_enemies, enemies, num):
    for i in range(num):
        small_enemy = enemy.SmallEnemy(bg_size)
        small_enemies.add(small_enemy)
        enemies.add(small_enemy)


def add_middle_enemies(middle_enemies, enemies, num):
    for i in range(num):
        middle_enemy = enemy.MiddleEnemy(bg_size)
        middle_enemies.add(middle_enemy)
        enemies.add(middle_enemy)


def add_large_enemies(large_enemies, enemies, num):
    for i in range(num):
        large_enemy = enemy.LargeEnemy(bg_size)
        large_enemies.add(large_enemy)
        enemies.add(large_enemy)

def increase_speed(target, inc):
    for each in target:
        each.speed += inc


def main():
    pygame.mixer.music.play(-1)

    # 生成我方飞机
    my_plane = myplane.MyPlane(bg_size)

    # 存放敌方飞机
    enemies = pygame.sprite.Group()

    # 生成敌方小型飞机
    small_enemies = pygame.sprite.Group()
    add_small_enemies(small_enemies, enemies, 15)

    # 生成敌方中型飞机
    middle_enemies = pygame.sprite.Group()
    add_middle_enemies(middle_enemies, enemies, 4)

    # 生成敌方大型飞机
    large_enemies = pygame.sprite.Group()
    add_large_enemies(large_enemies, enemies, 2)

    # 生成普通子弹
    bullet1 = []
    bullet1_index = 0
    BULLET1_NUM = 4
    for i in range(BULLET1_NUM):
        bullet1.append(bullet.Bullet1(my_plane.rect.midtop))
        # a = [10, 110, 210, 310, 410]
        # for i in a:
        #     bullet1.append(bullet.Bullent((i, my_plane.rect.height)))

    # 生成超级子弹
    bullet2 = []
    bullet2_index = 0
    BULLET2_NUM = 8
    for i in range(BULLET2_NUM // 2):
        bullet2.append(bullet.Bullet2(((my_plane.rect.centerx - 33), my_plane.rect.centery)))
        bullet2.append(bullet.Bullet2(((my_plane.rect.centerx + 30), my_plane.rect.centery)))

    clock = pygame.time.Clock()

    # 中弹图片索引
    small_enemy_destroy_index = 0
    middle_enemy_destroy_index = 0
    large_enemy_destroy_index = 0
    me_destroy_index = 0

    # 统计得分
    score = 0
    score_font = pygame.font.Font('font/font.ttf', 36)

    # 设置难度级别
    level = 1

    # 全屏炸弹
    bomb_image = pygame.image.load('images/bomb.png').convert_alpha()
    bomb_rect = bomb_image.get_rect()
    bomb_font = pygame.font.Font('font/font.ttf', 48)
    bomb_num = 3

    # 每30秒发放一个补给包
    bullet_supply = supply.BulletSupply(bg_size)
    bomb_supply = supply.BombSupply(bg_size)
    SUPPLY_TIME = USEREVENT
    pygame.time.set_timer(SUPPLY_TIME, 30 * 1000)

    # 超级子弹定时器
    DOUBLE_BULLET_TIME = USEREVENT + 1

    # 是否使用超级子弹
    is_double_bullet = False

    # 解除我方无敌定时器
    INVINCIBLE_TIME = USEREVENT + 2

    # 我方飞机生命数量
    life_image = pygame.image.load('images/life.png').convert_alpha()
    life_rect = life_image.get_rect()
    life_num = 3

    # 游戏结束画面
    gameover_font = pygame.font.Font('font/font.ttf', 48)
    again_image = pygame.image.load('images/again.png').convert_alpha()
    again_rect = again_image.get_rect()
    gameover_image = pygame.image.load('images/gameover.png').convert_alpha()
    gameover_rect = gameover_image.get_rect()

    # 用于阻止重复打开记录文件
    recorded = False

    # 标志是否暂停
    paused = False
    pause_nor_image = pygame.image.load('images/pause_nor.png').convert_alpha()
    pause_pressed_image = pygame.image.load('images/pause_pressed.png').convert_alpha()
    resume_nor_image = pygame.image.load('images/resume_nor.png').convert_alpha()
    resume_pressed_image = pygame.image.load('images/resume_pressed.png').convert_alpha()
    pause_rect = pause_nor_image.get_rect()
    pause_rect.left, pause_rect.top = width - pause_rect.width - 10, 10
    paused_image = pause_nor_image

    # 用于切换飞机显示图片
    switch_image1 = True

    # 用于切换飞机摧毁图片
    switch_image2 = True

    # 用于延迟
    delay = 101

    running = True

    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == MOUSEBUTTONDOWN:
                if event.button == 1 and pause_rect.collidepoint(event.pos):
                    paused = not paused
                    if paused:
                        pygame.mixer.music.pause()
                        pygame.mixer.pause()
                        pygame.time.set_timer(SUPPLY_TIME, 0)
                    else:
                        pygame.mixer.music.unpause()
                        pygame.mixer.unpause()
                        pygame.time.set_timer(SUPPLY_TIME, 30 * 1000)
                    if pause_rect.collidepoint(event.pos):
                        if paused:
                            paused_image = resume_pressed_image
                        else:
                            paused_image = pause_pressed_image
                    else:
                        if paused:
                            paused_image = resume_nor_image
                        else:
                            paused_image = pause_nor_image

            elif event.type == MOUSEMOTION:
                if pause_rect.collidepoint(event.pos):
                    if paused:
                        paused_image = resume_pressed_image
                    else:
                        paused_image = pause_pressed_image
                else:
                    if paused:
                        paused_image = resume_nor_image
                    else:
                        paused_image = pause_nor_image

            elif event.type == KEYDOWN:
                if event.key == K_SPACE:
                    if bomb_num:
                        bomb_num -= 1
                        bomb_sound.play()
                        for each in enemies:
                            if each.rect.bottom > 0:
                                each.active = False

            elif event.type == SUPPLY_TIME:
                supply_sound.play()
                if choice([True, False]):
                    bomb_supply.reset()
                else:
                    bullet_supply.reset()

            elif event.type == DOUBLE_BULLET_TIME:
                is_double_bullet = False
                pygame.time.set_timer(DOUBLE_BULLET_TIME, 0)

            elif event.type == INVINCIBLE_TIME:
                my_plane.invincible = False
                pygame.time.set_timer(INVINCIBLE_TIME, 0)

        # 根据得分增加难度
        if level == 1 and score > 50000:
            level = 2
            upgrade_sound.play()
            # 增加3架小型敌机,增加2架中型敌机,增加1架大型敌机
            add_small_enemies(small_enemies, enemies, 3)
            add_middle_enemies(middle_enemies, enemies, 2)
            add_large_enemies(large_enemies, enemies, 1)
            # 提升小型飞机的速度
            increase_speed(small_enemies, 1)
        elif level == 2 and score > 300000:
            level = 3
            upgrade_sound.play()
            # 增加5架小型敌机,增加3架中型敌机,增加2架大型敌机
            add_small_enemies(small_enemies, enemies, 5)
            add_middle_enemies(middle_enemies, enemies, 3)
            add_large_enemies(large_enemies, enemies, 2)
            # 提升小型飞机的速度
            increase_speed(small_enemies, 1)
            increase_speed(middle_enemies, 1)
        elif level == 3 and score > 600000:
            level = 4
            upgrade_sound.play()
            # 增加5架小型敌机,增加3架中型敌机,增加2架大型敌机
            add_small_enemies(small_enemies, enemies, 5)
            add_middle_enemies(middle_enemies, enemies, 3)
            add_large_enemies(large_enemies, enemies, 2)
            # 提升小型飞机的速度
            increase_speed(small_enemies, 1)
            increase_speed(middle_enemies, 1)
        elif level == 4 and score > 1000000:
            level = 5
            upgrade_sound.play()
            # 增加5架小型敌机,增加3架中型敌机,增加2架大型敌机
            add_small_enemies(small_enemies, enemies, 5)
            add_middle_enemies(middle_enemies, enemies, 3)
            add_large_enemies(large_enemies, enemies, 2)
            # 提升小型飞机的速度
            increase_speed(small_enemies, 1)
            increase_speed(middle_enemies, 1)

        # 绘制背景
        screen.blit(background, (0, 0))

        # 绘制暂停键
        screen.blit(paused_image, pause_rect)

        # 切换飞机显示图片
        if not (delay % 5):
            switch_image1 = not switch_image1

        # 切换飞机摧毁图片
        if not (delay % 3):
            switch_image2 = False
        else:
            switch_image2 = True

        if not delay:
            delay = 100
        else:
            delay -= 1

        # 不暂停时绘制物体
        if life_num and not paused:

            # 检测用户的键盘操作
            key_pressed = pygame.key.get_pressed()
            if key_pressed[K_w] or key_pressed[K_UP]:
                my_plane.moveUp()
            if key_pressed[K_s] or key_pressed[K_DOWN]:
                my_plane.moveDown()
            if key_pressed[K_a] or key_pressed[K_LEFT]:
                my_plane.moveLeft()
            if key_pressed[K_d] or key_pressed[K_RIGHT]:
                my_plane.moveRight()

            # 绘制补给并检测是否获得
            if bomb_supply.active:
                bomb_supply.move()
                screen.blit(bomb_supply.image, bomb_supply.rect)
                if pygame.sprite.collide_mask(bomb_supply, my_plane):
                    get_bomb_sound.play()
                    if bomb_num < 3:
                        bomb_num += 1
                    bomb_supply.active = False

            # 绘制超级子弹并检测是否获得
            if bullet_supply.active:
                bullet_supply.move()
                screen.blit(bullet_supply.image, bullet_supply.rect)
                if pygame.sprite.collide_mask(bullet_supply, my_plane):
                    get_bullet_sound.play()
                    is_double_bullet = True
                    pygame.time.set_timer(DOUBLE_BULLET_TIME, 18 * 1000)
                    bullet_supply.active = False

            # 检测我方飞机是否被撞
            enemies_down = pygame.sprite.spritecollide(my_plane, enemies, False, pygame.sprite.collide_mask)
            if enemies_down and not my_plane.invincible:
                my_plane.active = False
                for each in enemies_down:
                    each.active = False

            # 绘制我方飞机
            if my_plane.active:
                if switch_image1:
                    screen.blit(my_plane.image1, my_plane.rect)
                else:
                    screen.blit(my_plane.image2, my_plane.rect)
            else:
                # 毁灭
                if not switch_image2:
                    if me_destroy_index == 0:
                        me_down_sound.play()
                    screen.blit(my_plane.destroy_images[me_destroy_index], my_plane.rect)
                    me_destroy_index = (me_destroy_index + 1) % 4
                    if me_destroy_index == 0:
                        life_num -= 1
                        my_plane.reset()
                        pygame.time.set_timer(INVINCIBLE_TIME, 3 * 1000)

            # 发射子弹
            if not (delay % 10):
                bullet_sound.play()
                if is_double_bullet:
                    bullets = bullet2
                    bullets[bullet2_index].reset((my_plane.rect.centerx - 33, my_plane.rect.centery))
                    bullets[bullet2_index + 1].reset((my_plane.rect.centerx + 30, my_plane.rect.centery))
                    bullet2_index = (bullet2_index + 2) % BULLET2_NUM
                else:
                    bullets = bullet1
                    bullets[bullet1_index].reset(my_plane.rect.midtop)
                    bullet1_index = (bullet1_index + 1) % BULLET1_NUM

            # 检测子弹是否击中敌机
            for b in bullets:
                if b.active:
                    b.move()
                    screen.blit(b.image, b.rect)
                    enemy_hit = pygame.sprite.spritecollide(b, enemies, False, pygame.sprite.collide_mask)
                    if enemy_hit:
                        b.active = False
                        for e in enemy_hit:
                            if e in middle_enemies or e in large_enemies:
                                e.energy -= 1
                                if e.energy == 0:
                                    e.active = False
                                e.hit = True
                            else:
                                e.active = False

            # 绘制大型敌方飞机
            for each in large_enemies:
                if each.active:
                    each.move()
                    if each.hit:
                        screen.blit(each.image_hit, each.rect)
                        each.hit = False
                    else:
                        if switch_image1:
                            screen.blit(each.image1, each.rect)
                        if not switch_image1:
                            screen.blit(each.image2, each.rect)

                    # 绘制血槽
                    pygame.draw.line(screen, BLACK,
                                     (each.rect.left, each.rect.top - 5), (each.rect.right, each.rect.top - 5), 2)
                    # 当生命大于20%显示绿色,否则显示红色
                    energy_remain = each.energy / enemy.LargeEnemy.energy
                    if energy_remain > 0.2:
                        energy_color = GREEN
                    else:
                        energy_color = RED
                    pygame.draw.line(screen, energy_color,
                                     (each.rect.left, each.rect.top - 5),
                                     (each.rect.left + energy_remain * each.rect.width, each.rect.top - 5), 2)

                    # 即将出现在画面中,播放音效
                    if -50 < each.rect.bottom < 0:
                        enemy3_fly_sound.play()
                else:
                    # 毁灭
                    if not switch_image2:
                        if large_enemy_destroy_index == 0:
                            enemy3_down_sound.play()
                        screen.blit(each.destroy_images[large_enemy_destroy_index], each.rect)
                        large_enemy_destroy_index = (large_enemy_destroy_index + 1) % 6
                        if large_enemy_destroy_index == 0:
                            score += 10000
                            each.reset()

            # 绘制中型敌方飞机
            for each in middle_enemies:
                if each.active:
                    each.move()
                    if each.hit:
                        screen.blit(each.image_hit, each.rect)
                        each.hit = False
                    else:
                        screen.blit(each.image, each.rect)

                    # 绘制血槽
                    pygame.draw.line(screen, BLACK,
                                     (each.rect.left, each.rect.top - 5), (each.rect.right, each.rect.top - 5), 2)
                    # 当生命大于20%显示绿色,否则显示红色
                    energy_remain = each.energy / enemy.MiddleEnemy.energy
                    if energy_remain > 0.2:
                        energy_color = GREEN
                    else:
                        energy_color = RED
                    pygame.draw.line(screen, energy_color,
                                     (each.rect.left, each.rect.top - 5),
                                     (each.rect.left + energy_remain * each.rect.width, each.rect.top - 5), 2)

                else:
                    # 毁灭
                    if not switch_image2:
                        if middle_enemy_destroy_index == 0:
                            enemy2_down_sound.play()
                        screen.blit(each.destroy_images[middle_enemy_destroy_index], each.rect)
                        middle_enemy_destroy_index = (middle_enemy_destroy_index + 1) % 4
                        if middle_enemy_destroy_index == 0:
                            score += 6000
                            each.reset()

            # 绘制小型敌方飞机
            for each in small_enemies:
                if each.active:
                    each.move()
                    screen.blit(each.image, each.rect)
                else:
                    # 毁灭
                    enemy1_down_sound.play()
                    if not switch_image2:
                        if small_enemy_destroy_index == 0:
                            enemy1_down_sound.play()
                        screen.blit(each.destroy_images[small_enemy_destroy_index], each.rect)
                        small_enemy_destroy_index = (small_enemy_destroy_index + 1) % 4
                        if small_enemy_destroy_index == 0:
                            score += 1000
                            each.reset()

            # 绘制炸弹数量
            bomb_text = bomb_font.render('× %d' % bomb_num, True, WHITE)
            bomb_text_rect = bomb_text.get_rect()
            screen.blit(bomb_image, (10, height - 10 - bomb_rect.height))
            screen.blit(bomb_text, (20 + bomb_rect.width, height - 5 - bomb_text_rect.height))

            # 绘制剩余生命数量
            if life_num:
                for i in range(life_num):
                    screen.blit(life_image, (width - 10 - (i + 1) * life_rect.width, height - 10 - life_rect.height))

            # 绘制分数
            score_text = score_font.render('Score : %s' % str(score), True, WHITE)
            screen.blit(score_text, (10, 5))

        elif life_num and paused:
            # 绘制分数
            score_text = score_font.render('Score : %s' % str(score), True, WHITE)
            screen.blit(score_text, (10, 5))

        # 游戏结束
        elif life_num == 0:
            # 背景音乐停止
            pygame.mixer.music.stop()
            # 停止全部音效
            pygame.mixer.stop()
            # 停止发放补给
            pygame.time.set_timer(SUPPLY_TIME, 0)
            if not recorded:
                recorded = True
                # 读取历史最高得分
                with open('record.txt', 'r') as f:
                    record_score = int(f.read())
                # 如果玩家得分高于历史最高得分,则存档
                if score > record_score:
                    with open('record.txt', 'w') as f:
                        f.write(str(score))

            # 界面绘制
            screen.blit(background, (0, 0))
            record_score_text = score_font.render('Best : %d' % record_score, True, WHITE)
            screen.blit(record_score_text, (10, 10))

            gameover_text1 = gameover_font.render('Your Score', True, WHITE)
            gameover_text1_rect = gameover_text1.get_rect()
            gameover_text1_rect.left, gameover_text1_rect.top = (width - gameover_text1_rect.width) // 2, height // 4
            screen.blit(gameover_text1, gameover_text1_rect)

            gameover_text2 = gameover_font.render(str(score), True, WHITE)
            gameover_text2_rect = gameover_text2.get_rect()
            gameover_text2_rect.left, gameover_text2_rect.top = (width - gameover_text2_rect.width) // 2, \
                                                                gameover_text1_rect.bottom + 10
            screen.blit(gameover_text2, gameover_text2_rect)

            again_rect.left, again_rect.top = (width - again_rect.width) // 2, gameover_text2_rect.bottom + 50
            screen.blit(again_image, again_rect)

            gameover_rect.left, gameover_rect.top = (width - gameover_rect.width) // 2, again_rect.bottom + 10
            screen.blit(gameover_image, gameover_rect)

            # 检测玩家鼠标按键操作
            # 如果玩家按下左键
            if pygame.mouse.get_pressed()[0]:
                # 获取鼠标坐标
                pos = pygame.mouse.get_pos()
                # 如果点击重新开始
                if again_rect.left < pos[0] < again_rect.right and again_rect.top < pos[1] < again_rect.bottom:
                    main()
                # 如果点击游戏结束
                elif gameover_rect.left < pos[0] < gameover_rect.right and gameover_rect.top < pos[1] <gameover_rect.bottom:
                    sys.exit()

        pygame.display.flip()

        clock.tick(60)


if __name__ == '__main__':
    try:
        main()
    except SystemExit:
        pass
    except:
        traceback.print_exc()
        pygame.quit()
        input()
