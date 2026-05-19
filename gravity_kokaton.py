"""
重力アクションゲーム（フラッピーバード風）のベースコード
"""

import pygame as pg
import sys
import random


# 画面サイズの設定
WIDTH = 800
HEIGHT = 600

class Player(pg.sprite.Sprite):
    """
    主人公キャラクター（こうかとん）に関するクラス
    """
    def __init__(self) -> None:
        super().__init__()
        # ※実際の画像ファイルがある場合は以下のコメントアウトを外して差し替える
        self.image = pg.image.load("ex5/fig/3.png")
        self.image = pg.transform.flip(self.image, True, False)
        
        self.rect = self.image.get_rect()
        self.rect.center = (150, HEIGHT // 2)
        self.vy = 0.0 # Y方向の落下速度

    def update(self) -> None:
        """
        重力による落下処理
        """
        self.vy += 0.5 
        self.rect.y += int(self.vy)

    def jump(self) -> None:
        """
        スペースキー押下によるジャンプ処理
        """
        self.vy = -8.0 

class Score():
    """
    スコアに関するクラス
    """
    def __init__(self):
        self.font = pg.font.Font(None,50)
        self.color = (255 , 255, 255)
        self.value = 0.0
        self.image = self.font.render(f"Score: {int(self.value)}", 0, self.color)
        self.rect = self.image.get_rect()
        self.rect.center = (100, 50)

    def update(self, screen: pg.Surface):
        self.value += 100 / 60
        self.image = self.font.render(f"Score: {int(self.value)}", 0, self.color)
        screen.blit(self.image, self.rect)

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
    
    def activate(self, score: Score) -> None:
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
    
    def activate(self, score: Score) -> None:
        #コインの効果:スコアを1000増加
        score.value += 1000

class Obstacle(pg.sprite.Sprite):
    """
    障害物に関するクラス
    """
    def __init__(self, x: int, y: int, width: int, height: int) -> None:
        super().__init__()
        self.image = pg.Surface((width, height))
        self.image.fill((0, 255, 0)) # 緑色のダミー四角形
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def update(self) -> None:
        """
        左方向へのスクロール処理
        """
        self.rect.x -= 5 
        if self.rect.right < 0:
            self.kill() # 画面外に出たらグループから削除


def main():
    pg.init()
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    pg.display.set_caption("飛べ！重力こうかとん")
    clock = pg.time.Clock()

    # Sprite Groupの初期化
    all_sprites = pg.sprite.Group()
    obstacles = pg.sprite.Group()
    items = pg.sprite.Group()

    # 主人公の生成
    player = Player()
    all_sprites.add(player)

    #スコアインスタンスの生成
    score = Score()

    # 障害物生成用のカスタムイベント
    SPAWN_OBSTACLE = pg.USEREVENT + 1
    pg.time.set_timer(SPAWN_OBSTACLE, 1500) 

    running = True
    while running:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                running = False
            
            # スペースキー入力時のジャンプ処理
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    player.jump()
            
            # 障害物とコインのランダム生成
            if event.type == SPAWN_OBSTACLE:
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

        all_sprites.update()

        #こうかとんとアイテムの当たり判定
        hit_items = pg.sprite.spritecollide(player, items, True)
        for item in hit_items:
            item.activate(score) #獲得したアイテムの効果を発動

        # こうかとんと障害物の当たり判定、および画面上下端の判定
        if pg.sprite.spritecollide(player, obstacles, False) \
           or player.rect.top < 0 or player.rect.bottom > HEIGHT:
            # 共通基本機能では、衝突時にそのままループを抜けて終了する
            running = False

        # 背景と全Spriteの描画
        screen.fill((135, 206, 235))
        all_sprites.draw(screen)

        score.update(screen)
        
        pg.display.flip()
        clock.tick(60)

    pg.quit()
    sys.exit()

if __name__ == "__main__":
    main()