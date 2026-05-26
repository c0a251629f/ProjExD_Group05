import pygame
import sys
import random

# 画面サイズの設定
WIDTH = 800
HEIGHT = 600


class Player(pygame.sprite.Sprite):
    """
    主人公キャラクター（こうかとん）に関するクラス
    """
    def __init__(self) -> None:
        super().__init__()
        # ※実際の画像ファイルがある場合は以下のコメントアウトを外して差し替える
        self.image = pygame.image.load("ex5/fig/3.png")
        self.image = pygame.transform.flip(self.image, True, False)
        
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
    スコア管理に関するクラス
    """
    def __init__(self):
        self.font = pygame.font.Font(None, 50)
        self.color = (255, 255, 255) # 白色
        self.bonus_color = (255, 215, 0) # 金色（3倍時用）
        self.value = 0
        self.image = self.font.render(f"Score: {int(self.value)}", 0, self.color)
        self.rect = self.image.get_rect()
        self.rect.center = (100,50)
        
        # 3倍アイテム用の状態管理
        self.multiplier = 1
        self.multiplier_timer = 0 # フレーム数で時間を管理 (60フレーム = 1秒)
    
    def update(self, screen: pygame.Surface):
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


class Obstacle(pygame.sprite.Sprite):
    """
    障害物に関するクラス
    """
    def __init__(self, x: int, y: int, width: int, height: int) -> None:
        super().__init__()
        self.image = pygame.Surface((width, height))
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
            
            
def draw_text(screen: pygame.Surface, text: str, size: int, x: int, y: int, color: tuple = (0, 0, 0)) -> None:
    """
    画面にテキストを描画するヘルパー関数
    """
    font = pygame.font.SysFont(None, size)
    surface = font.render(text, True, color)
    rect = surface.get_rect()
    rect.center = (x, y)
    screen.blit(surface, rect)


class Item(pygame.sprite.Sprite):
    """
    スコア3倍アイテムに関するクラス
    """
    def __init__(self, x: int, y: int) -> None:
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill((255, 0, 0))  # スコア3倍は赤色のダミー四角形
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self) -> None:
        """
        左方向へのスクロール処理
        """
        self.rect.x -= 5 
        if self.rect.right < 0:
            self.kill()


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("飛べ！重力こうかとん")
    clock = pygame.time.Clock()

    # Sprite Groupの初期化
    all_sprites = pygame.sprite.Group()
    obstacles = pygame.sprite.Group()
    items = pygame.sprite.Group() # アイテム用のグループ

    # 主人公の生成
    player = Player()
    all_sprites.add(player)

    # 障害物生成用のカスタムイベント
    SPAWN_OBSTACLE = pygame.USEREVENT + 1
    pygame.time.set_timer(SPAWN_OBSTACLE, 1500)
    # ADD_SCORE = pygame.USEREVENT + 2
    # pygame.time.set_timer(ADD_SCORE, 1000)

    # アイテム生成用のカスタムイベント（2秒ごとに抽選）
    SPAWN_ITEM = pygame.USEREVENT + 3
    pygame.time.set_timer(SPAWN_ITEM, 2000)

    # スコアインスタンスの生成
    score = Score()

    state = "countdown"   
    countdown_start_time = pygame.time.get_ticks()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # スペースキー入力時のジャンプ処理
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and state == "playing":
                    player.jump()
            
            # 障害物のランダム生成
            if event.type == SPAWN_OBSTACLE and state == "playing":
                gap_y = random.randint(150, HEIGHT - 150)
                gap_size = 150
                
                top_obs = Obstacle(WIDTH, 0, 50, gap_y - gap_size // 2)
                bottom_obs = Obstacle(WIDTH, gap_y + gap_size // 2, 50, HEIGHT - (gap_y + gap_size // 2))
                
                obstacles.add(top_obs, bottom_obs)
                all_sprites.add(top_obs, bottom_obs)

            # アイテムのランダム生成
            if event.type == SPAWN_ITEM:
            # 40%の確率で3倍アイテムを生成
                if random.random() < 0.4:
                    item_y = random.randint(100, HEIGHT - 100)
                    item = Item(WIDTH, item_y)
                    items.add(item)
                    all_sprites.add(item)

        # 背景と全Spriteの描画
        screen.fill((135, 206, 235)) # ※背景画像がある場合は blit に変更
        
        if state == "countdown":
            all_sprites.draw(screen)
            
            now = pygame.time.get_ticks()
            elapsed = now - countdown_start_time
            
            if elapsed < 1000:
                draw_text(screen, "3", 150, WIDTH // 2, HEIGHT // 2, (255, 50, 50))
            elif elapsed < 2000:
                draw_text(screen, "2", 150, WIDTH // 2, HEIGHT // 2, (255, 150, 50))
            elif elapsed < 3000:
                draw_text(screen, "1", 150, WIDTH // 2, HEIGHT // 2, (255, 200, 50))
            elif elapsed < 4000:
                draw_text(screen, "GO!", 150, WIDTH // 2, HEIGHT // 2, (50, 255, 50))
            else:
                state = "playing"    
        
        elif state == "playing":
            all_sprites.update()

            # こうかとんとアイテムの当たり判定（接触時にアイテムを消滅させる）
            hit_items = pygame.sprite.spritecollide(player, items, True)
            for item in hit_items:
                score.activate_multiplier(3, 10) # 10秒間スコア3倍を発動

            # こうかとんと障害物の当たり判定、および画面上下端の判定
            if pygame.sprite.spritecollide(player, obstacles, False) or player.rect.top < 0 or player.rect.bottom > HEIGHT:
                state = "gameover"
        
            all_sprites.draw(screen)
            score.update(screen)
               
        elif state == "gameover":
            all_sprites.draw(screen)
            draw_text(screen, "GAME OVER", 120, WIDTH // 2, HEIGHT // 2 - 50, (255, 0, 0))
            draw_text(screen, f"TOTAL SCORE: {int(score.value)}", 80, WIDTH // 2, HEIGHT // 2 + 50, (255, 255, 255))
        
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()