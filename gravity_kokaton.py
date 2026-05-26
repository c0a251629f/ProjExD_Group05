"""
重力アクションゲーム（フラッピーバード風）のベースコード
"""

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


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("飛べ！重力こうかとん")
    clock = pygame.time.Clock()

    # Sprite Groupの初期化
    all_sprites = pygame.sprite.Group()
    obstacles = pygame.sprite.Group()

    # 主人公の生成
    player = Player()
    all_sprites.add(player)

    # 障害物生成用のカスタムイベント
    SPAWN_OBSTACLE = pygame.USEREVENT + 1
    pygame.time.set_timer(SPAWN_OBSTACLE, 1500)
    ADD_SCORE = pygame.USEREVENT + 2
    pygame.time.set_timer(ADD_SCORE, 1000)
    
    state = "countdown" 
    score = 0
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
                
            if event.type == ADD_SCORE and state == "playing":
                score += 100

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

        # こうかとんと障害物の当たり判定、および画面上下端の判定
            if pygame.sprite.spritecollide(player, obstacles, False) or player.rect.top < 0 or player.rect.bottom > HEIGHT:
            # 共通基本機能では、衝突時にそのままループを抜けて終了する
                state = "gameover"
        
            all_sprites.draw(screen)
            draw_text(screen, f"SCORE: {score}", 50, WIDTH // 2, 50, (0, 0, 0))
            
        elif state == "gameover":
            all_sprites.draw(screen)
            
            draw_text(screen, "GAME OVER", 120, WIDTH // 2, HEIGHT // 2 - 50, (255, 0, 0))
            draw_text(screen, f"TOTAL SCORE: {score}", 80, WIDTH // 2, HEIGHT // 2 + 50, (255, 255, 255))
        
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()