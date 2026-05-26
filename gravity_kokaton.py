"""
重力アクションゲーム（フラッピーバード風）のベースコード
"""
import os
import pygame as pg
import sys
import random

os.chdir(os.path.dirname(os.path.abspath(__file__)))

# 画面サイズ
WIDTH = 800
HEIGHT = 600


class Player(pg.sprite.Sprite):
    """
    主人公キャラクター（こうかとん）
    """
    def __init__(self) -> None:
        super().__init__()
        # ※実際の画像ファイルがある場合は以下のコメントアウトを外して差し替える
        self.image = pg.image.load("fig/3.png")
        self.image = pg.transform.flip(self.image, True, False)
        
        self.rect = self.image.get_rect()
        self.rect.center = (150, HEIGHT // 2)

        self.vy = 0.0
        # マスクを作成してピクセル単位当たり判定に対応
        self.mask = pg.mask.from_surface(self.image)

        #透明化状態
        self.transparent = False
        self.transparent_timer = 0

    def update(self) -> None:
        """
        重力処理
        """
        self.vy += 0.5
        self.rect.y += int(self.vy)

     #透明化タイマー
        if self.transparent:
            self.transparent_timer -= 1

            if self.transparent_timer <= 0:
                self.transparent = False
                self.image.set_alpha(255)


    def jump(self) -> None:
        """
        ジャンプ
        """
        self.vy = -8.0

    def activate_transparent(self):
        self.transparent = True
        self.transparent_timer = 300
        self.image.set_alpha(128)
        
class Score():
    """
    スコア管理に関するクラス
    """
    def __init__(self):
        self.font = pg.font.Font(None, 50)
        self.color = (255, 255, 255) # 白色
        self.bonus_color = (255, 215, 0) # 金色（3倍時用）
        self.value = 0.0
        self.image = self.font.render(f"Score: {int(self.value)}", 0, self.color)
        self.rect = self.image.get_rect()
        self.rect.center = (100,50)
        
        # 3倍アイテム用の状態管理
        self.multiplier = 1
        self.multiplier_timer = 0 # フレーム数で時間を管理 (60フレーム = 1秒)
    
    def update(self, screen: pg.Surface):
        # 3倍タイマーのカウントダウン
        if self.multiplier_timer > 0:
            self.multiplier_timer -= 1
            if self.multiplier_timer == 0:
                self.multiplier = 1 # 効果終了

        # 通常のスコア加算（3倍時は加算量も3倍）
        self.value += (100 / 60) * self.multiplier
        
        # 描画テキストの準備
        current_color = self.bonus_color if self.multiplier > 1 else self.color
        score_text = f"Score: {int(self.value)}"
        
        # 3倍時は残り秒数を表示
        if self.multiplier > 1:
            seconds_left = (self.multiplier_timer // 60) + 1
            score_text += f" (x3! {seconds_left}s)"

        # 元のコードと同じ引数「0」を維持し、文字色のみcurrent_colorに連動
        self.image = self.font.render(score_text, 0, current_color)
        # 元のコードと全く同じcenter位置の設定を維持
        self.rect = self.image.get_rect()
        self.rect.center = (100,50)
        # 元のコードと全く同じblit処理を維持
        screen.blit(self.image, self.rect)

    def activate_multiplier(self, multiplier: int, duration_sec: int):
        """倍率アイテム発動"""
        self.multiplier = multiplier
        self.multiplier_timer = duration_sec * 60 # 60fps想定

class Item(pg.sprite.Sprite):
    """
    アイテムに関する親クラス
    他のアイテム実装時もこのクラスを継承する
    """
    def __init__(self, x:int, y: int, color: tuple) -> None:
        super().__init__()
        self.image = pg.Surface((30,30),pg.SRCALPHA)
        pg.draw.circle(self.image, color, (15,15), 15)
        self.rect = self.image.get_rect()
        self.rect.center = (x,y)
    
    def update(self) -> None:
        """
        共通仕様:障害物と同じスピードで左へスクロール
        """
        self.rect.x -= 5
        if self.rect.right < 0:
            self.kill()
    
    def activate(self, player, score: Score) -> None:
        """
        アイテムを拾った時の効果(子クラスごとに処理を上書き)
        """
        pass
class CoinItem(Item):
    """
    獲得時スコアが1000増加するアイテム
    """
    def __init__(self, x:int, y:int) -> None:
        super().__init__(x,y,(255,215,0))
    
    def activate(self, player, score: Score) -> None:
        #コインの効果:スコアを1000増加
        score.value += 1000

class sanbai(Item):
    """
    スコア3倍アイテムに関するクラス
    """
    def __init__(self, x:int, y:int) -> None:
        super().__init__(x, y,(255,0,0))
        self.image = pg.Surface((30, 30))
        self.image.fill((255, 0, 0))  # スコア3倍は赤色のダミー四角形
        self.rect = self.image.get_rect(center = (x,y))
    
    def activate(self, player, score: Score):
        score.activate_multiplier(3,10)

        
class Obstacle(pg.sprite.Sprite):
    """
    障害物
    """
    def __init__(self, x: int, y: int, width: int, height: int) -> None:
        super().__init__()
        self.image = pg.Surface((width, height))
        self.image.fill((0, 255, 0)) # 緑色のダミー四角形
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        # マスク（ピクセル単位当たり判定用）
        self.mask = pg.mask.from_surface(self.image)

    def update(self) -> None:
        """
        左へ移動
        """
        self.rect.x -= 5

        if self.rect.right < 0:
            self.kill() # 画面外に出たらグループから削除
            
            
#def draw_text(screen: pg.Surface, text: str, size: int, x: int, y: int, color: tuple = (0, 0, 0)) -> None:
            #self.kill()


class Enemy(pg.sprite.Sprite):
    """
    右から飛んでくる敵
    """
    #font = pg.font.SysFont(None, size)
    def __init__(self) -> None:
        super().__init__()

        # 敵画像
        self.image = pg.image.load("fig/6.png")
        # 視認性向上のため拡大
        self.image = pg.transform.rotozoom(self.image, 0, 0.6)

        self.rect = self.image.get_rect()
        # マスク（ピクセル単位当たり判定用）
        self.mask = pg.mask.from_surface(self.image)

        # 右端から出現
        self.rect.x = WIDTH

        # ランダムな高さ
        self.rect.y = random.randint(50, HEIGHT - 50)

        # 左向き速度
        self.vx = 8

    def update(self) -> None:
        """
        左へ移動
        """
        self.rect.x -= self.vx

        # 画面外に出たら削除
        if self.rect.right < 0:
            self.kill()


def draw_text(
    screen: pg.Surface,
    text: str,
    size: int,
    x: int,
    y: int,
    color: tuple = (0, 0, 0)
) -> None:
    """
    テキスト描画
    """
    font = pg.font.SysFont(None, size)

    surface = font.render(text, True, color)

    rect = surface.get_rect()
    rect.center = (x, y)

    screen.blit(surface, rect)


class TransparentItem(Item):
    def __init__(self, x:int, y:int) -> None:
        super().__init__(x,y,(0,0,255))

    def activate(self, player, score):
        player.activate_transparent()
        



def main():
    pg.init()
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    pg.display.set_caption("飛べ！重力こうかとん")
    clock = pg.time.Clock()

    # Sprite Groupの初期化
    all_sprites = pg.sprite.Group()
    obstacles = pg.sprite.Group()
    items = pg.sprite.Group()

    clock = pg.time.Clock()

    # グループ
    all_sprites = pg.sprite.Group()
    obstacles = pg.sprite.Group()
    enemies = pg.sprite.Group()

    # プレイヤー生成
    player = Player()
    all_sprites.add(player)

    # 障害物生成用のカスタムイベント
    SPAWN_OBSTACLE = pg.USEREVENT + 1
    pg.time.set_timer(SPAWN_OBSTACLE, 1500)


    # スコアインスタンスの生成
    score = Score()

    state = "countdown"   
    countdown_start_time = pg.time.get_ticks()

    #アイテム生成イベント
    SPAWN_ITEM = pg.USEREVENT +2
    pg.time.set_timer(SPAWN_ITEM, 5000)
    # 障害物イベント
    SPAWN_OBSTACLE = pg.USEREVENT + 1
    pg.time.set_timer(SPAWN_OBSTACLE, 1500)

    # スコアイベント
    #ADD_SCORE = pg.USEREVENT + 2
    #pg.time.set_timer(ADD_SCORE, 1000)

    # 敵生成イベント
    SPAWN_ENEMY = pg.USEREVENT + 3
    pg.time.set_timer(SPAWN_ENEMY, 2000)

    countdown_start_time = pg.time.get_ticks()
    restart_button_rect = pg.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 150, 200, 60)

    running = True

    while running:

        for event in pg.event.get():

            if event.type == pg.QUIT:
                running = False

            # ジャンプ
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE and state == "playing":
                    player.jump()

            if event.type == pg.MOUSEBUTTONDOWN:
                if state == "gameover" and restart_button_rect.collidepoint(event.pos):
                    obstacles.empty()
                    enemies.empty()
                    all_sprites.empty()
                    player.rect.center = (150, HEIGHT // 2)
                    player.vy = 0.0
                    all_sprites.add(player)
                    # スコアオブジェクトをリセット
                    if isinstance(score, Score):
                        score.value = 0
                        score.multiplier = 1
                        score.multiplier_timer = 0
                    else:
                        score = Score()
                    state = "countdown"
                    countdown_start_time = pg.time.get_ticks()

            # 障害物生成
            if event.type == SPAWN_OBSTACLE and state == "playing":

                gap_y = random.randint(150, HEIGHT - 150)
                gap_size = 150
                
                #障害物の生成
                top_obs = Obstacle(WIDTH, 0, 50, gap_y - gap_size // 2)
                bottom_obs = Obstacle(WIDTH, gap_y + gap_size // 2, 50, HEIGHT - (gap_y + gap_size // 2))
                obstacles.add(top_obs, bottom_obs)
                all_sprites.add(top_obs, bottom_obs)
            
            #20%の確率で障害物の隙間にコインを生成
                if random.random() < 0.20:
                    coin = CoinItem(WIDTH + 25, gap_y)
                    items.add(coin)
                    all_sprites.add(coin)

            # アイテムのランダム生成
            if event.type == SPAWN_ITEM:
                item_y = random.randint(100,HEIGHT -100)
                r = random.random()

                if r < 0.4:
                    item = sanbai(WIDTH, item_y)
                else:
                    item = TransparentItem(WIDTH, item_y)

                items.add(item)
                all_sprites.add(item)
            # # 40%の確率で3倍アイテムを生成


        


                # top_obs = Obstacle(
                #     WIDTH,
                #     0,
                #     50,
                #     gap_y - gap_size // 2
                # )

                # bottom_obs = Obstacle(
                #     WIDTH,
                #     gap_y + gap_size // 2,
                #     50,
                #     HEIGHT - (gap_y + gap_size // 2)
                # )

                # obstacles.add(top_obs, bottom_obs)
                # all_sprites.add(top_obs, bottom_obs)

            # 敵生成
            if event.type == SPAWN_ENEMY and state == "playing":

                enemy = Enemy()

                enemies.add(enemy)
                all_sprites.add(enemy)

            # スコア加算
            #if event.type == ADD_SCORE and state == "playing":
                #score += 100

        # 背景
        screen.fill((135, 206, 235))

        # カウントダウン
        if state == "countdown":

            all_sprites.draw(screen)
            

            now = pg.time.get_ticks()
            elapsed = now - countdown_start_time

            if elapsed < 1000:
                draw_text(
                    screen,
                    "3",
                    150,
                    WIDTH // 2,
                    HEIGHT // 2,
                    (255, 50, 50)
                )

            elif elapsed < 2000:
                draw_text(
                    screen,
                    "2",
                    150,
                    WIDTH // 2,
                    HEIGHT // 2,
                    (255, 150, 50)
                )

            elif elapsed < 3000:
                draw_text(
                    screen,
                    "1",
                    150,
                    WIDTH // 2,
                    HEIGHT // 2,
                    (255, 200, 50)
                )

            elif elapsed < 4000:
                draw_text(
                    screen,
                    "GO!",
                    150,
                    WIDTH // 2,
                    HEIGHT // 2,
                    (50, 255, 50)
                )

            else:
                state = "playing"

        # プレイ中
        elif state == "playing":

            all_sprites.update()

            # こうかとんとアイテムの当たり判定（接触時にアイテムを消滅させる）
            hit_items = pg.sprite.spritecollide(player, items, True)
            for item in hit_items:
                item.activate(player, score) #獲得したアイテムの効果を発動

            # こうかとんと障害物の当たり判定、および画面上下端の判定
            if not player.transparent:
                # マスクを使ったピクセル単位の当たり判定に変更
                hit_obstacle = pg.sprite.spritecollide(player, obstacles, False, pg.sprite.collide_mask)
                hit_enemy = pg.sprite.spritecollide(player, enemies, False, pg.sprite.collide_mask)
                if hit_obstacle or hit_enemy or player.rect.top < 0 or player.rect.bottom > HEIGHT:
                    print("Collision detected: ", "obstacle" if hit_obstacle else "enemy" if hit_enemy else "boundary")
                    state = "gameover"
        
            all_sprites.draw(screen)
            score.update(screen)
               
        elif state == "gameover":

            all_sprites.draw(screen)

            draw_text(
                screen,
                "GAME OVER",
                120,
                WIDTH // 2,
                HEIGHT // 2 - 50,
                (255, 0, 0)
            )

            draw_text(screen,f"TOTAL SCORE: {int(score.value)}",80,WIDTH // 2,HEIGHT // 2 + 50, (255, 255, 255))
            pg.draw.rect(screen, (30, 144, 255), restart_button_rect)
            draw_text(screen,"RESTART",40,restart_button_rect.centerx,restart_button_rect.centery,(255, 255, 255))
            

        pg.display.flip()
        clock.tick(60)

    pg.quit()
    sys.exit()


if __name__ == "__main__":
    main()