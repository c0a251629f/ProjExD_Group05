import pygame
import sys
import random


# 画面サイズ
WIDTH = 800
HEIGHT = 600


class Player(pygame.sprite.Sprite):
    """
    主人公キャラクター（こうかとん）
    """
    def __init__(self) -> None:
        super().__init__()

        self.image = pygame.image.load("fig/3.png")
        self.image = pygame.transform.flip(self.image, True, False)

        self.rect = self.image.get_rect()
        self.rect.center = (150, HEIGHT // 2)

        self.vy = 0.0

    def update(self) -> None:
        """
        重力処理
        """
        self.vy += 0.5
        self.rect.y += int(self.vy)

    def jump(self) -> None:
        """
        ジャンプ
        """
        self.vy = -8.0


class Obstacle(pygame.sprite.Sprite):
    """
    障害物
    """
    def __init__(self, x: int, y: int, width: int, height: int) -> None:
        super().__init__()

        self.image = pygame.Surface((width, height))
        self.image.fill((0, 255, 0))

        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def update(self) -> None:
        """
        左へ移動
        """
        self.rect.x -= 5

        if self.rect.right < 0:
            self.kill()


class Enemy(pygame.sprite.Sprite):
    """
    右から飛んでくる敵
    """
    def __init__(self) -> None:
        super().__init__()

        # 敵画像
        self.image = pygame.image.load("fig/6.png")
        # 視認性向上のため拡大
        self.image = pygame.transform.rotozoom(self.image, 0, 0.6)

        self.rect = self.image.get_rect()

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
    screen: pygame.Surface,
    text: str,
    size: int,
    x: int,
    y: int,
    color: tuple = (0, 0, 0)
) -> None:
    """
    テキスト描画
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

    # グループ
    all_sprites = pygame.sprite.Group()
    obstacles = pygame.sprite.Group()
    enemies = pygame.sprite.Group()

    # プレイヤー生成
    player = Player()
    all_sprites.add(player)

    # 障害物イベント
    SPAWN_OBSTACLE = pygame.USEREVENT + 1
    pygame.time.set_timer(SPAWN_OBSTACLE, 1500)

    # スコアイベント
    ADD_SCORE = pygame.USEREVENT + 2
    pygame.time.set_timer(ADD_SCORE, 1000)

    # 敵生成イベント
    SPAWN_ENEMY = pygame.USEREVENT + 3
    pygame.time.set_timer(SPAWN_ENEMY, 2000)

    state = "countdown"

    score = 0

    countdown_start_time = pygame.time.get_ticks()
    restart_button_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 150, 200, 60)

    running = True

    while running:

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            # ジャンプ
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and state == "playing":
                    player.jump()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if state == "gameover" and restart_button_rect.collidepoint(event.pos):
                    obstacles.empty()
                    enemies.empty()
                    all_sprites.empty()
                    player.rect.center = (150, HEIGHT // 2)
                    player.vy = 0.0
                    all_sprites.add(player)
                    score = 0
                    state = "countdown"
                    countdown_start_time = pygame.time.get_ticks()

            # 障害物生成
            if event.type == SPAWN_OBSTACLE and state == "playing":

                gap_y = random.randint(150, HEIGHT - 150)
                gap_size = 150

                top_obs = Obstacle(
                    WIDTH,
                    0,
                    50,
                    gap_y - gap_size // 2
                )

                bottom_obs = Obstacle(
                    WIDTH,
                    gap_y + gap_size // 2,
                    50,
                    HEIGHT - (gap_y + gap_size // 2)
                )

                obstacles.add(top_obs, bottom_obs)
                all_sprites.add(top_obs, bottom_obs)

            # 敵生成
            if event.type == SPAWN_ENEMY and state == "playing":

                enemy = Enemy()

                enemies.add(enemy)
                all_sprites.add(enemy)

            # スコア加算
            if event.type == ADD_SCORE and state == "playing":
                score += 100

        # 背景
        screen.fill((135, 206, 235))

        # カウントダウン
        if state == "countdown":

            all_sprites.draw(screen)

            now = pygame.time.get_ticks()
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

            # 当たり判定
            if (
                pygame.sprite.spritecollide(player, obstacles, False)
                or pygame.sprite.spritecollide(player, enemies, False)
                or player.rect.top < 0
                or player.rect.bottom > HEIGHT
            ):
                state = "gameover"

            # 描画
            all_sprites.draw(screen)

            draw_text(
                screen,
                f"SCORE: {score}",
                50,
                WIDTH // 2,
                50,
                (0, 0, 0)
            )

        # ゲームオーバー
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

            draw_text(
                screen,
                f"TOTAL SCORE: {score}",
                80,
                WIDTH // 2,
                HEIGHT // 2 + 50,
                (255, 255, 255)
            )
            pygame.draw.rect(screen, (30, 144, 255), restart_button_rect)
            draw_text(
                screen,
                "RESTART",
                40,
                restart_button_rect.centerx,
                restart_button_rect.centery,
                (255, 255, 255)
            )

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()