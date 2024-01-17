import pygame
from pygame.locals import *
import pymunk
import random
import os
import time  # 追加
import sys


# Pygameの初期化
pygame.init()


# 画面サイズ
screen_width, screen_height = 500, 700 #500, 700 #720, 960


# キャラクターサイズ
character_width, character_height = 120, 200


# 壁の厚さ
wall_thickness = 5


# ゲームウィンドウの作成
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Catch the Food Game")


# Pymunkの初期化
space = pymunk.Space()
space.gravity = 0, -1000  # 重力の設定


# キャラクターの作成
class Character(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.crying = False  # 追加
        self.image_left = pygame.image.load("ずんだもん左.png").convert_alpha()
        self.image_right = pygame.image.load("ずんだもん右.png").convert_alpha()
        self.smile_image_left = pygame.image.load("ずんだもん左笑顔.png").convert_alpha()
        self.smile_image_right = pygame.image.load("ずんだもん右笑顔.png").convert_alpha()
        self.crying_image_left = pygame.image.load("ずんだもん左泣き顔.png").convert_alpha()
        self.crying_image_right = pygame.image.load("ずんだもん右泣き顔.png").convert_alpha()
        self.image_left = pygame.transform.scale(self.image_left, (character_width, character_height))
        self.image_right = pygame.transform.scale(self.image_right, (character_width, character_height))
        self.smile_image_left = pygame.transform.scale(self.smile_image_left, (character_width, character_height))
        self.smile_image_right = pygame.transform.scale(self.smile_image_right, (character_width, character_height))
        self.crying_image_left = pygame.transform.scale(self.crying_image_left, (character_width, character_height))
        self.crying_image_right = pygame.transform.scale(self.crying_image_right, (character_width, character_height))
        self.image = self.image_left
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 10
        self.catching = False  # 追加
        self.catch_start_time = 0  # 追加
        self.catching_duration = 0.5  # キャッチ中の表示時間
        self.crying_duration = 0.5  # 追加
        self.last_catch_time = 0  # 最後にキャッチした時間
        self.last_direction = "left"  # 最後に進んでいた方向


        # 初期画像の保存
        self.initial_image_left = pygame.transform.scale(self.image_left, (character_width, character_height))
        self.initial_image_right = pygame.transform.scale(self.image_right, (character_width, character_height))
        self.image = self.initial_image_left  # 初期画像をセット


        # 初期位置の保存
        self.initial_position = (self.rect.centerx, self.rect.centery)


    def update(self, keys):


        # 笑顔表示が終わったら通常表示
        if keys[K_LEFT]:
            self.rect.x -= self.speed
            self.image = self.image_left
        elif keys[K_RIGHT]:
            self.rect.x += self.speed
            self.image = self.image_right


        if self.catching:
            # キャッチ中は適用する画像を切り替え
            elapsed_time_since_catch = time.time() - self.last_catch_time
            if elapsed_time_since_catch < self.catching_duration:
                if self.last_direction == "left":
                    self.image = self.smile_image_left
                elif self.last_direction == "right":
                    self.image = self.smile_image_right
            else:
                self.catching = False
                if self.last_direction == "left":
                    self.image = self.image_left
                elif self.last_direction == "right":
                    self.image = self.image_right


        # 新たに追加
        if self.crying:
            elapsed_time_since_cry = time.time() - self.last_cry_time
            if elapsed_time_since_cry < self.crying_duration:
                if self.last_direction == "left":
                    self.image = self.crying_image_left
                elif self.last_direction == "right":
                    self.image = self.crying_image_right
            else:
                self.crying = False
                if not self.catching:  # キャッチ中は表示を変更しない
                    if self.last_direction == "left":
                        self.image = self.image_left
                    elif self.last_direction == "right":
                        self.image = self.image_right


        if self.rect.left < wall_thickness:
            self.rect.left = wall_thickness
        elif self.rect.right > screen_width - wall_thickness:
            self.rect.right = screen_width - wall_thickness


    def catch_food(self):
        # 食べ物をキャッチしたときに呼び出され、キャッチ中の状態を設定
        self.catching = True
        self.last_catch_time = time.time()
        self.last_direction = "left" if self.image == self.image_left else "right"


    def restart(self):
        # リスタート時に呼び出すメソッド
        self.image = self.initial_image_left  # 初期画像に戻す
        self.rect.center = self.initial_position  # 初期位置に戻す


# 背景の初期設定
current_background = pygame.image.load("春の街中（日中）.jpg").convert()
current_background = pygame.transform.scale(current_background, (screen_width, screen_height))


# 音楽の読み込みと再生
pygame.mixer.music.load("ちょっと楽しい.mp3")
pygame.mixer.music.play(-1)


# 効果音の読み込み
catch_sound = pygame.mixer.Sound("キャッチした時の音.mp3")


# 壁の作成
def create_walls():
    walls = [pymunk.Segment(space.static_body, (0, 0), (0, screen_height), wall_thickness),
             pymunk.Segment(space.static_body, (screen_width, 0), (screen_width, screen_height), wall_thickness)]
    for wall in walls:
        wall.friction = 1.0
        space.add(wall)


create_walls()


# キャラクターのグループ
all_sprites = pygame.sprite.Group()
character = Character(screen_width // 2, screen_height - character_height // 2)
all_sprites.add(character)


# 食べ物の作成
class Food(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()


        # ランダムに食べ物または障害物を選択
        items = ["ずんだ餅.png", "zunda_mochi.png", "obstacle.png"]
        self.item_path = os.path.join(random.choices(items, weights=[0.02, 0.005, 0.005])[0])


        if "obstacle.png" in self.item_path:
            self.image = pygame.image.load(self.item_path).convert_alpha()
            self.image = pygame.transform.scale(self.image, (60, 60))
            self.score = 0  # 障害物の場合は得点を加算しない
        else:
            self.image = pygame.image.load(self.item_path).convert_alpha()
            if "zunda_mochi.png" in self.item_path:
                self.image = pygame.transform.scale(self.image, (60, 60))
                self.score = 3
            else:
                self.image = pygame.transform.scale(self.image, (30, 30))
                self.score = 1


        self.rect = self.image.get_rect()
        self.rect.topleft = (random.randint(wall_thickness, screen_width - wall_thickness), 0)
        self.speed = 10


    def update(self):
        self.rect.y += self.speed
        if self.rect.top > screen_height:
            self.rect.topleft = (random.randint(wall_thickness, screen_width - wall_thickness), 0)


# 食べ物のグループ
food_group = pygame.sprite.Group()


# 得点
score = 0


# ゲームが始まっているかどうかのフラグ
game_started = True


# ゲーム開始からの経過時間
elapsed_time = 0


# 背景変更のタイミング（1分経過）
background_change_time_spring = 60  # seconds
background_change_time_summer = 120  # seconds
background_change_time_autumn = 180  # seconds
background_change_time_winter = 240  # seconds


# ゲームオーバー画面の表示とリスタート処理
def game_over_screen():
    global score, elapsed_time  # グローバル変数としてscoreとelapsed_timeを宣言


    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEBUTTONDOWN:
                if restart_button_rect.collidepoint(event.pos):
                    # リスタートボタンがクリックされたら初期化して新しいゲームを始める
                    score = 0  # scoreをグローバル変数として更新
                    character.restart()  # キャラクターのリスタート処理
                    obstacle_catch_count = 0
                    character.crying = False
                    character.catching = False
                    game_over = False
                    all_sprites.empty()
                    food_group.empty()
                    create_walls()
                    all_sprites.add(character)
                    current_background = pygame.image.load("春の街中（日中）.jpg").convert()
                    current_background = pygame.transform.scale(current_background, (screen_width, screen_height))
                    elapsed_time = 0    # ゲーム開始からの経過時間
                    return


        # ゲームオーバーの文字を表示
        font = pygame.font.Font(None, 74)
        game_over_text = font.render("Game Over", True, (255, 0, 0))
        score_font = pygame.font.Font(None, 48)
        score_text = score_font.render(f"Score: {score}", True, (0, 0, 0))
        screen.blit(game_over_text, (screen_width // 2 - 150, screen_height // 2 - 50))
        screen.blit(score_text, (screen_width // 2 - 100, screen_height // 2 + 50))


        # リスタートボタンの描画
        restart_button_rect = pygame.Rect(screen_width // 2 - 100, screen_height // 2 + 120, 200, 50)
        pygame.draw.rect(screen, (0, 128, 255), restart_button_rect)
        restart_font = pygame.font.Font(None, 36)
        restart_text = restart_font.render("Restart", True, (255, 255, 255))
        restart_text_rect = restart_text.get_rect(center=restart_button_rect.center)
        screen.blit(restart_text, restart_text_rect)


        pygame.display.flip()


# メインループ
running = True
clock = pygame.time.Clock()
obstacle_catch_count = 0  # 障害物のキャッチ回数をカウントする変数
game_over_start_time = 0  # ゲームオーバー画面表示開始時刻


while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False


    keys = pygame.key.get_pressed()


    # 画面の更新
    screen.blit(current_background, (0, 0))


    # キャラクターの更新と描画
    character.update(keys)
    all_sprites.draw(screen)


    # 食べ物の更新と描画
    food_group.update()
    food_group.draw(screen)


    game_over = False  # ゲームオーバーフラグ


    # 衝突判定
    collisions = pygame.sprite.spritecollide(character, food_group, True)
    if collisions:
        # 食べ物をキャッチしたときの処理
        if collisions[0].score > 0:  # 得点がある場合のみ得点を加算
            score += sum(food.score for food in collisions)
            catch_sound.play()
            character.catch_food()  # キャラクターの状態を変更
        elif "obstacle.png" in collisions[0].item_path:
            # 障害物をキャッチしたときの処理（不正解音を再生）
            pygame.mixer.Sound("ブブー、不正解.mp3").play()
            character.catch_food()  # キャラクターの状態を変更
            character.crying = True  # 新たに追加
            character.last_cry_time = time.time()  # 新たに追加
            obstacle_catch_count += 1  # 障害物のキャッチ回数を増加
            if obstacle_catch_count >= 5:
                game_over = True  # ゲームオーバーフラグを有効にする


    # ゲームオーバー画面
    if game_over:
        game_over_screen()  # ゲームオーバー画面を表示してリスタート処理を待つ
        # ゲームオーバー後の初期化処理（得点などのリセット）
        score = 0
        character.rect.x = screen_width // 2
        character.rect.y = screen_height - character_height // 2
        game_over = False  # ゲームオーバーフラグを無効にする
        # キャラクターの初期位置に戻す
        character.rect.center = character.initial_position
        # 変数をリセットします
        score = 0
        obstacle_catch_count = 0
        game_started = True


    # 得点表示
    font = pygame.font.Font(None, 36)
    score_text = font.render(f"Score: {score}", True, (0, 0, 0))
    screen.blit(score_text, (10, 10))


    # 食べ物の下に障害物の画像表示
    obstacle_image = pygame.image.load("obstacle.png").convert_alpha()
    obstacle_image = pygame.transform.scale(obstacle_image, (30, 30))
    screen.blit(obstacle_image, (10, 60))


    # 障害物のキャッチ回数表示
    obstacle_catch_count_text = font.render(f": {obstacle_catch_count}", True, (255, 0, 0))
    screen.blit(obstacle_catch_count_text, (50, 60))
    # 物理演算の更新
    space.step(1 / 60.0)


    # 一定確率で新しい食べ物を追加
    if random.random() < 0.02:  # "ずんだ餅.png"の出現率
        food = Food()
        food_group.add(food)


    # 経過時間の更新
    elapsed_time += clock.tick(60) / 1000


    # 得点に基づいて食べ物の速度を変更
    if score >= 150:
        food_speed = 30
    elif score >= 100:
        food_speed = 25
    elif score >= 50:
        food_speed = 20
    else:
        food_speed = 15  # デフォルトの速度


    for food in food_group.sprites():
        food.speed = food_speed


    # 背景変更
    if 0 <= elapsed_time < background_change_time_spring:
        current_background = pygame.image.load("春の街中（日中）.jpg").convert()
    elif background_change_time_spring <= elapsed_time < background_change_time_summer:
        current_background = pygame.image.load("夏の街中（日中）.jpg").convert()
    elif background_change_time_summer <= elapsed_time < background_change_time_autumn:
        current_background = pygame.image.load("秋の街中（日中）.jpg").convert()
    elif background_change_time_autumn <= elapsed_time < background_change_time_winter:
        current_background = pygame.image.load("冬の街中（晴れ・日中）.jpg").convert()


    current_background = pygame.transform.scale(current_background, (screen_width, screen_height))
    elapsed_time %= background_change_time_winter  # タイマーのリセット


    pygame.display.flip()


# 終了処理
pygame.quit()



