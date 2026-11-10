import math
import os
import sys
import random
import time
import pygame
import mysql.connector

# Initialize pygame
pygame.init()

# MySQL Database Connection (credentials come from environment variables)
conn = mysql.connector.connect(
    host=os.getenv("DB_HOST", "localhost"),
    user=os.environ["DB_USER"],
    password=os.environ["DB_PASSWORD"],
    database=os.getenv("DB_NAME", "aim_trainer_db"),
)
cursor = conn.cursor()

# Screen settings
WIDTH, HEIGHT = 800, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Aim Trainer")

TARGET_EVENT = pygame.USEREVENT
TARGET_PADDING = 30
BG_COLOR = (0, 25, 40)
LIVES = 3
TOP_BAR_HEIGHT = 50
MAX_NAME_LENGTH = 20


def select_difficulty(win):
    font = pygame.font.SysFont("comicsans", 36)
    options = ["Easy", "Medium", "Hard"]
    selected = 1  # Default: Medium

    while True:
        win.fill(BG_COLOR)
        title = font.render("Select Difficulty:", True, "white")
        win.blit(title, (WIDTH // 2 - title.get_width() // 2, HEIGHT // 4))

        for i, option in enumerate(options):
            color = "yellow" if i == selected else "white"
            text = font.render(option, True, color)
            win.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 + i * 50))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and selected > 0:
                    selected -= 1
                elif event.key == pygame.K_DOWN and selected < len(options) - 1:
                    selected += 1
                elif event.key == pygame.K_RETURN:
                    return options[selected]


def get_player_name(win):
    name = ""
    font = pygame.font.SysFont("comicsans", 36)
    while True:
        win.fill(BG_COLOR)
        text = font.render("Enter Your Name: " + name, True, "white")
        win.blit(text, (WIDTH // 4, HEIGHT // 2))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and name.strip():
                    return name.strip()
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                elif event.unicode.isprintable() and len(name) < MAX_NAME_LENGTH:
                    name += event.unicode


player_name = get_player_name(WIN)


class Target:
    MAX_SIZE = 30
    GROWTH_RATE = 0.2
    COLOR = "red"
    SECOND_COLOR = "white"

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = 0
        self.grow = True

    def update(self):
        if self.size + self.GROWTH_RATE >= self.MAX_SIZE:
            self.grow = False
        if self.grow:
            self.size += self.GROWTH_RATE
        else:
            self.size -= self.GROWTH_RATE

    def draw(self, win):
        pygame.draw.circle(win, self.COLOR, (self.x, self.y), self.size)
        pygame.draw.circle(win, self.SECOND_COLOR, (self.x, self.y), self.size * 0.8)
        pygame.draw.circle(win, self.COLOR, (self.x, self.y), self.size * 0.6)
        pygame.draw.circle(win, self.SECOND_COLOR, (self.x, self.y), self.size * 0.4)

    def collide(self, x, y):
        dis = math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)
        return dis <= self.size


def save_score(name, time_elapsed, hits, accuracy):
    cursor.execute(
        "INSERT INTO aim_trainer_scores (name, time_elapsed, targets_hit, accuracy) VALUES (%s, %s, %s, %s)",
        (name, time_elapsed, hits, accuracy),
    )
    conn.commit()


def fetch_top_scores():
    # Ties on accuracy are broken by more hits, so a 1-hit run can't top the board
    cursor.execute(
        "SELECT name, time_elapsed, targets_hit, accuracy FROM aim_trainer_scores "
        "ORDER BY accuracy DESC, targets_hit DESC LIMIT 5"
    )
    return cursor.fetchall()


def delete_all_scores():
    cursor.execute("DELETE FROM aim_trainer_scores")
    conn.commit()


def end_screen(win, elapsed_time, targets_pressed, clicks, save=True):
    win.fill(BG_COLOR)

    accuracy = round(targets_pressed / clicks * 100, 1) if clicks > 0 else 0
    if save:
        save_score(player_name, elapsed_time, targets_pressed, accuracy)

    font = pygame.font.SysFont("comicsans", 28)

    labels = [
        f"Time: {elapsed_time:.2f}s",
        f"Hits: {targets_pressed}",
        f"Accuracy: {accuracy}%",
    ]

    y_offset = 60
    for text in labels:
        label = font.render(text, True, "white")
        win.blit(label, (WIDTH // 2 - label.get_width() // 2, y_offset))
        y_offset += 50

    title = font.render("Top Scores:", True, "yellow")
    win.blit(title, (WIDTH // 2 - title.get_width() // 2, y_offset + 20))

    y_offset += 60
    for idx, (name, _, hits, acc) in enumerate(fetch_top_scores()):
        score_text = f"{idx + 1}. {name} - {acc}% Accuracy ({hits} hits)"
        score_label = font.render(score_text, True, "white")
        win.blit(score_label, (WIDTH // 2 - score_label.get_width() // 2, y_offset))
        y_offset += 40

    button_font = pygame.font.SysFont("comicsans", 24, bold=True)

    play_again_rect = pygame.Rect(WIDTH // 2 - 110, HEIGHT - 120, 220, 50)
    pygame.draw.rect(win, "white", play_again_rect, border_radius=12)
    play_again_text = button_font.render("PLAY AGAIN", True, (0, 50, 150))

    delete_scores_rect = pygame.Rect(WIDTH // 2 - 110, HEIGHT - 60, 220, 50)
    pygame.draw.rect(win, "red", delete_scores_rect, border_radius=12)
    delete_scores_text = button_font.render("DELETE SCORES", True, "white")

    for rect, text in ((play_again_rect, play_again_text), (delete_scores_rect, delete_scores_text)):
        win.blit(text, (rect.x + (rect.width - text.get_width()) // 2,
                        rect.y + (rect.height - text.get_height()) // 2))

    pygame.display.update()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_again_rect.collidepoint(event.pos):
                    # ponytail: replay recurses into main(); fine unless someone replays ~1000 times in one sitting
                    main()
                elif delete_scores_rect.collidepoint(event.pos):
                    delete_all_scores()
                    end_screen(win, elapsed_time, targets_pressed, clicks, save=False)


def main():
    targets = []
    clock = pygame.time.Clock()
    targets_pressed = 0
    clicks = 0
    misses = 0

    difficulty = select_difficulty(WIN)

    # Difficulty sets spawn interval (ms) and target size
    if difficulty == "Easy":
        target_increment, Target.MAX_SIZE = 600, 40
    elif difficulty == "Medium":
        target_increment, Target.MAX_SIZE = 400, 30
    else:  # Hard
        target_increment, Target.MAX_SIZE = 250, 20

    pygame.time.set_timer(TARGET_EVENT, target_increment)
    start_time = time.time()  # start after difficulty is chosen, not before

    while True:
        clock.tick(60)
        click = False
        mouse_pos = pygame.mouse.get_pos()
        elapsed_time = time.time() - start_time

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == TARGET_EVENT:
                x = random.randint(TARGET_PADDING, WIDTH - TARGET_PADDING)
                y = random.randint(TARGET_PADDING + TOP_BAR_HEIGHT, HEIGHT - TARGET_PADDING)
                targets.append(Target(x, y))
            if event.type == pygame.MOUSEBUTTONDOWN:
                click = True
                clicks += 1

        # Iterate over a copy so removing targets doesn't skip or double-remove
        for target in targets[:]:
            target.update()
            if target.size <= 0:
                targets.remove(target)
                misses += 1
                continue
            if click and target.collide(*mouse_pos):
                targets.remove(target)
                targets_pressed += 1

        if misses >= LIVES:
            pygame.time.set_timer(TARGET_EVENT, 0)  # stop spawning behind the end screen
            end_screen(WIN, elapsed_time, targets_pressed, clicks)

        WIN.fill(BG_COLOR)
        for target in targets:
            target.draw(WIN)
        pygame.display.update()


if __name__ == "__main__":
    main()
