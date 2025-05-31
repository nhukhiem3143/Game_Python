import asyncio
import math
import pygame
import random
import platform
import sys
import os

# Hàm để lấy đường dẫn tài nguyên đúng khi đóng gói bằng PyInstaller
def resource_path(relative_path):
    """Lấy đường dẫn tuyệt đối đến file tài nguyên, hoạt động cả khi đóng gói và không đóng gói."""
    try:
        # sys._MEIPASS được PyInstaller thiết lập khi đóng gói
        base_path = sys._MEIPASS
    except AttributeError:
        # Nếu không đóng gói, dùng thư mục hiện tại
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Cấu hình game
FPS = 60
WIDTH = 800
HEIGHT = 600

# Khởi tạo Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Astrocrash")
clock = pygame.time.Clock()

# Màu sắc
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GRAY = (100, 100, 100)
GREEN = (0, 255, 0)
YELLOW = (255, 255, 0)
BLUE = (0, 0, 255)
ORANGE = (255, 165, 0)

# Tải phông chữ
font = pygame.font.SysFont("Arial", 36)
large_font = pygame.font.SysFont("Arial", 72)

# Tải âm thanh và nhạc nền
boom_sound = None
shoot_sound = None
intro_music = None
background_music = None

try:
    boom_sound = pygame.mixer.Sound(resource_path("boom.wav"))
except FileNotFoundError as e:
    print(f"Warning: {e} - Boom sound will be disabled.")

try:
    shoot_sound = pygame.mixer.Sound(resource_path("shoot.wav"))
except FileNotFoundError as e:
    print(f"Warning: {e} - Shoot sound will be disabled.")

try:
    intro_music = pygame.mixer.Sound(resource_path("intro.mp3"))
except FileNotFoundError as e:
    print(f"Warning: {e} - Intro music will be disabled.")

try:
    background_music = pygame.mixer.Sound(resource_path("background.mp3"))
    pygame.mixer.music.load(resource_path("background.mp3"))
except FileNotFoundError as e:
    print(f"Warning: {e} - Background music will be disabled.")

# Biến quản lý âm thanh
intro_enabled = True
background_enabled = True
sound_enabled = True
paused = False  # Trạng thái tạm dừng
menu_open = False  # Trạng thái menu trong trận

# Tạo nền gradient
def create_gradient(start_color, end_color, width, height):
    gradient = pygame.Surface((width, height))
    for y in range(height):
        t = y / height
        r = int(start_color[0] * (1 - t) + end_color[0] * t)
        g = int(start_color[1] * (1 - t) + end_color[1] * t)
        b = int(start_color[2] * (1 - t) + end_color[2] * t)
        pygame.draw.line(gradient, (r, g, b), (0, y), (width, y))
    return gradient

menu_background = create_gradient((0, 0, 50), (0, 0, 150), WIDTH, HEIGHT)
game_background = create_gradient((10, 10, 30), (50, 50, 100), WIDTH, HEIGHT)

# Các lớp game
class Ship:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT - 50
        self.speed = 7
        self.base_speed = 7
        self.health = 150
        self.shoot_speed = 0.1
        self.base_shoot_speed = 0.1
        self.bullet_level = 1
        self.powerup_timer = {"speed": 0, "shoot": 0}
        try:
            self.image = pygame.image.load(resource_path("ship.png"))
            self.image = pygame.transform.scale(self.image, (70, 70))
        except FileNotFoundError as e:
            print(f"Error: {e} - Using default rectangle for ship.")
            self.image = pygame.Surface((70, 70))
            self.image.fill(WHITE)
        self.rect = self.image.get_rect(center=(self.x, self.y))

    def move(self, dx, dy):
        self.x += dx * self.speed
        self.y += dy * self.speed
        self.x = max(0, min(WIDTH, self.x))
        self.y = max(0, min(HEIGHT, self.y))
        self.rect.center = (self.x, self.y)

    def update_powerups(self):
        if self.powerup_timer["speed"] > 0:
            self.powerup_timer["speed"] -= 1 / FPS
            if self.powerup_timer["speed"] <= 0:
                self.shoot_speed = self.base_shoot_speed
        if self.powerup_timer["shoot"] > 0:
            self.powerup_timer["shoot"] -= 1 / FPS
            if self.powerup_timer["shoot"] <= 0:
                self.shoot_speed = self.base_shoot_speed

class Asteroid:
    def __init__(self, size="small", speed=1):
        self.size = size
        self.x = random.randint(0, WIDTH)
        self.y = 0
        self.speed = speed
        self.damage = 10 if self.size == "small" else 30
        self.health = 20 if self.size == "small" else 50
        size_val = 44 if self.size == "small" else 50
        try:
            self.image = pygame.image.load(resource_path("alien_2.png" if self.size == "small" else "alien_1.png"))
            self.image = pygame.transform.scale(self.image, (size_val, size_val))
        except FileNotFoundError as e:
            print(f"Error: {e} - Using default rectangle for asteroid.")
            self.image = pygame.Surface((size_val, size_val))
            self.image.fill(GRAY)
        self.rect = self.image.get_rect(center=(self.x, self.y))

    def move(self):
        self.y += self.speed
        if self.y > HEIGHT:
            self.x = random.randint(0, WIDTH)
            self.y = 0
        self.rect.center = (self.x, self.y)

class Missile:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 10
        self.image = pygame.Surface((5, 5), pygame.SRCALPHA)
        pygame.draw.circle(self.image, WHITE, (2, 2), 2)
        self.rect = self.image.get_rect(center=(self.x, self.y))

    def move(self):
        self.y -= self.speed
        self.rect.center = (self.x, self.y)
        return 0 <= self.y <= HEIGHT

class PowerUp:
    def __init__(self, x, y, type):
        self.x = x
        self.y = y
        self.type = type
        self.speed = 2
        filename = {"hp_small": "hp_item.png", "hp_large": "hp_item.png", "speed": "speed_item.png",
                    "shoot": "speed_item.png", "bullet": "bullet_item.png"}[type]
        try:
            self.image = pygame.image.load(resource_path(filename))
            self.image = pygame.transform.scale(self.image, (15, 15))
        except FileNotFoundError as e:
            print(f"Error: {e} - Using default rectangle for powerup.")
            self.image = pygame.Surface((15, 15))
            self.image.fill(YELLOW)
        self.rect = self.image.get_rect(center=(self.x, self.y))

    def move(self):
        self.y += self.speed
        self.rect.center = (self.x, self.y)
        return 0 <= self.y <= HEIGHT

class Explosion:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.life = 10
        self.image = pygame.Surface((20, 20), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=(self.x, self.y))

    def update(self):
        self.life -= 1
        pygame.draw.circle(self.image, RED, (10, 10), 10 - (10 - self.life))
        self.rect.center = (self.x, self.y)
        return self.life > 0

# Thanh kéo âm lượng
class Slider:
    def __init__(self, x, y, width, height, min_val, max_val, initial_val):
        self.rect = pygame.Rect(x, y, width, height)
        self.min_val = min_val
        self.max_val = max_val
        self.value = initial_val
        self.dragging = False

    def draw(self, screen):
        pygame.draw.rect(screen, GRAY, self.rect)
        handle_pos = self.rect.x + (self.value - self.min_val) / (self.max_val - self.min_val) * self.rect.width
        handle_rect = pygame.Rect(handle_pos - 5, self.rect.y - 5, 10, self.rect.height + 10)
        pygame.draw.rect(screen, WHITE, handle_rect)

    def update(self):
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        if click[0] == 1 and self.rect.collidepoint(mouse):
            self.dragging = True
        if click[0] == 0:
            self.dragging = False
        if self.dragging:
            self.value = self.min_val + (mouse[0] - self.rect.x) / self.rect.width * (self.max_val - self.min_val)
            self.value = max(self.min_val, min(self.max_val, self.value))

# Thiết lập game
ship = Ship()
asteroids = []
missiles = []
powerups = []
explosions = []
score = 0
high_score = 0
state = "MENU"
last_shot = 0
difficulty = 1
spawn_timer = 0
menu_open = False
intro_slider = Slider(150, HEIGHT // 2 + 60, 80, 10, 0, 1, 0.5)
background_slider = Slider(150, HEIGHT // 2 + 120, 80, 10, 0, 1, 0.5)
sound_slider = Slider(150, HEIGHT // 2 + 180, 80, 10, 0, 1, 0.5)

def draw_button(text, x, y, width, height, color, hover_color, action=None):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    button_rect = pygame.Rect(x, y, width, height)

    if button_rect.collidepoint(mouse):
        pygame.draw.rect(screen, hover_color, button_rect)
        pygame.draw.rect(screen, WHITE, button_rect, 2)
    else:
        pygame.draw.rect(screen, color, button_rect)
        pygame.draw.rect(screen, GRAY, button_rect, 2)

    text_surf = font.render(text, True, BLACK)
    text_rect = text_surf.get_rect(center=button_rect.center)
    screen.blit(text_surf, text_rect)

    if button_rect.collidepoint(mouse) and click[0] == 1 and action:
        action()

def draw_toggle_button(text, x, y, width, height, enabled, action=None):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    button_rect = pygame.Rect(x, y, width, height)

    color = GREEN if enabled else GRAY
    pygame.draw.rect(screen, color, button_rect)
    pygame.draw.rect(screen, WHITE, button_rect, 2)

    text_surf = font.render(text, True, BLACK)
    text_rect = text_surf.get_rect(center=button_rect.center)
    screen.blit(text_surf, text_rect)

    if button_rect.collidepoint(mouse) and click[0] == 1 and action:
        action()
        return True
    return False

def draw_menu_button():
    if state == "PLAYING":
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        button_rect = pygame.Rect(WIDTH - 40, 10, 30, 30)

        pygame.draw.rect(screen, ORANGE, button_rect)
        pygame.draw.line(screen, BLACK, (WIDTH - 35, 15), (WIDTH - 15, 15), 2)
        pygame.draw.line(screen, BLACK, (WIDTH - 35, 20), (WIDTH - 15, 20), 2)
        pygame.draw.line(screen, BLACK, (WIDTH - 35, 25), (WIDTH - 15, 25), 2)

        # Di chuyển khai báo global lên trước khi sử dụng menu_open
        global menu_open
        if button_rect.collidepoint(mouse) and click[0] == 1:
            menu_open = not menu_open

def draw_menu_options():
    global menu_open  # Di chuyển lên đầu hàm
    if menu_open and state == "PLAYING":
        panel_width, panel_height = 200, 150
        panel_x, panel_y = WIDTH // 2 - panel_width // 2, HEIGHT // 2 - panel_height // 2
        pygame.draw.rect(screen, GRAY, (panel_x, panel_y, panel_width, panel_height))
        pygame.draw.rect(screen, WHITE, (panel_x, panel_y, panel_width, panel_height), 2)

        x_button_rect = pygame.Rect(panel_x + panel_width - 30, panel_y + 10, 20, 20)
        pygame.draw.rect(screen, RED, x_button_rect)
        pygame.draw.line(screen, WHITE, (x_button_rect.left + 5, x_button_rect.top + 5), (x_button_rect.right - 5, x_button_rect.bottom - 5), 2)
        pygame.draw.line(screen, WHITE, (x_button_rect.right - 5, x_button_rect.top + 5), (x_button_rect.left + 5, x_button_rect.bottom - 5), 2)
        mouse = pygame.mouse.get_pos()
        click = pygame.mouse.get_pressed()
        if x_button_rect.collidepoint(mouse) and click[0] == 1:
            menu_open = False

        pause_button_rect = pygame.Rect(panel_x + 40, panel_y + 40, 120, 40)
        pause_text = "||" if paused else ">"
        pygame.draw.rect(screen, YELLOW, pause_button_rect)
        pygame.draw.rect(screen, BLACK, pause_button_rect, 2)
        pause_surf = font.render(pause_text, True, BLACK)
        pause_rect = pause_surf.get_rect(center=pause_button_rect.center)
        screen.blit(pause_surf, pause_rect)
        if pause_button_rect.collidepoint(mouse) and click[0] == 1:
            toggle_pause()

        back_button_rect = pygame.Rect(panel_x + 40, panel_y + 90, 120, 40)
        draw_button("Back to Menu", back_button_rect.x, back_button_rect.y, 120, 40, GREEN, (0, 200, 0), go_to_menu)

def toggle_pause():
    global paused
    paused = not paused

def start_game():
    global state, score, asteroids, missiles, powerups, explosions, ship, difficulty, spawn_timer, paused, menu_open
    state = "PLAYING"
    score = 0
    difficulty = 1
    spawn_timer = 0
    paused = False
    menu_open = False
    ship = Ship()
    asteroids = [Asteroid("small", difficulty) for _ in range(3)]
    missiles = []
    powerups = []
    explosions = []
    if intro_music:
        intro_music.stop()
    if background_enabled and background_music:
        pygame.mixer.music.set_volume(background_slider.value)
        pygame.mixer.music.play(-1)

def go_to_menu():
    global state, paused, menu_open, background_slider, intro_slider
    state = "MENU"
    paused = False
    menu_open = False
    if background_music:
        pygame.mixer.music.stop()
    if background_enabled and background_music:
        pygame.mixer.music.set_volume(background_slider.value)
        pygame.mixer.music.play(-1)
    if intro_enabled and intro_music and state == "MENU":
        intro_music.set_volume(intro_slider.value)
        intro_music.play(-1)

def toggle_intro_music():
    global intro_enabled, intro_slider
    intro_enabled = not intro_enabled
    if intro_enabled and intro_music and state == "MENU":
        intro_music.set_volume(intro_slider.value)
        intro_music.play(-1)
    elif intro_music:
        intro_music.stop()

def toggle_background_music():
    global background_enabled, background_slider
    background_enabled = not background_enabled
    if background_enabled and background_music and state == "PLAYING":
        pygame.mixer.music.set_volume(background_slider.value)
        pygame.mixer.music.play(-1)
    elif background_music:
        pygame.mixer.music.stop()

def toggle_sound_effects():
    global sound_enabled
    sound_enabled = not sound_enabled

async def main():
    global score, asteroids, missiles, powerups, explosions, state, last_shot, high_score, difficulty, spawn_timer, menu_open
    running = True
    if intro_enabled and intro_music:
        intro_music.set_volume(intro_slider.value)
        intro_music.play(-1)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if state == "MENU":
            screen.blit(menu_background, (0, 0))
            title_text = large_font.render("Astrocrash", True, WHITE)
            title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 4))
            screen.blit(title_text, title_rect)

            draw_button("Play", WIDTH // 2 - 50, HEIGHT // 2, 100, 40, GREEN, (0, 200, 0), start_game)

            draw_toggle_button(f"Intro: {'ON' if intro_enabled else 'OFF'}", 50, HEIGHT // 2 + 60, 100, 40, intro_enabled, toggle_intro_music)
            draw_toggle_button(f"Music: {'ON' if background_enabled else 'OFF'}", 50, HEIGHT // 2 + 120, 100, 40, background_enabled, toggle_background_music)
            draw_toggle_button(f"Sound: {'ON' if sound_enabled else 'OFF'}", 50, HEIGHT // 2 + 180, 100, 40, sound_enabled, toggle_sound_effects)
            
            intro_slider.draw(screen)
            background_slider.draw(screen)
            sound_slider.draw(screen)
            intro_slider.update()
            background_slider.update()
            sound_slider.update()
            if intro_enabled and intro_music:
                intro_music.set_volume(intro_slider.value)
            if background_music:
                pygame.mixer.music.set_volume(background_slider.value)

            high_score_text = font.render(f"High Score: {high_score}", True, YELLOW)
            screen.blit(high_score_text, (WIDTH - high_score_text.get_width() - 10, 10))

        elif state == "PLAYING":
            if not paused:
                screen.blit(game_background, (0, 0))
                dx, dy = 0, 0
                keys = pygame.key.get_pressed()
                if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                    dx -= 1
                if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                    dx += 1
                if keys[pygame.K_UP] or keys[pygame.K_w]:
                    dy -= 1
                if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                    dy += 1
                if dx != 0 or dy != 0:
                    ship.move(dx, dy)

                current_time = pygame.time.get_ticks() / 1000
                if keys[pygame.K_SPACE] and current_time - last_shot >= ship.shoot_speed:
                    last_shot = current_time
                    if ship.bullet_level == 1:
                        missiles.append(Missile(ship.x, ship.y))
                    elif ship.bullet_level == 2:
                        missiles.append(Missile(ship.x - 10, ship.y))
                        missiles.append(Missile(ship.x + 10, ship.y))
                    else:
                        missiles.append(Missile(ship.x - 10, ship.y))
                        missiles.append(Missile(ship.x, ship.y))
                        missiles.append(Missile(ship.x + 10, ship.y))
                    if sound_enabled and shoot_sound:
                        shoot_sound.set_volume(sound_slider.value)
                        shoot_sound.play()

                ship.update_powerups()
                ship.rect.clamp_ip(screen.get_rect())
                for asteroid in asteroids[:]:
                    asteroid.move()
                    if ship.rect.colliderect(asteroid.rect):
                        ship.health -= asteroid.damage
                        asteroids.remove(asteroid)
                        if ship.health <= 0:
                            state = "LOSS"
                            high_score = max(high_score, score)
                            if background_music:
                                pygame.mixer.music.stop()

                missiles = [m for m in missiles if m.move()]
                for missile in missiles[:]:
                    for asteroid in asteroids[:]:
                        if missile.rect.colliderect(asteroid.rect):
                            asteroid.health -= 10
                            missiles.remove(missile)
                            if asteroid.health <= 0:
                                if random.random() < 0.2:
                                    types = ["hp_small", "hp_large", "speed", "shoot", "bullet"]
                                    powerups.append(PowerUp(asteroid.x, asteroid.y, random.choice(types)))
                                asteroids.remove(asteroid)
                                explosions.append(Explosion(asteroid.x, asteroid.y))
                                if sound_enabled and boom_sound:
                                    boom_sound.set_volume(sound_slider.value)
                                    boom_sound.play()
                                score += 10
                            break

                powerups = [p for p in powerups if p.move()]
                for powerup in powerups[:]:
                    if ship.rect.colliderect(powerup.rect):
                        if powerup.type == "hp_small":
                            ship.health = min(150, ship.health + 20)
                        elif powerup.type == "hp_large":
                            ship.health = min(150, ship.health + 50)
                        elif powerup.type == "speed":
                            ship.shoot_speed = ship.base_shoot_speed / 2
                            ship.powerup_timer["speed"] = 10
                        elif powerup.type == "shoot":
                            ship.shoot_speed = ship.base_shoot_speed / 2
                            ship.powerup_timer["shoot"] = 10
                        elif powerup.type == "bullet":
                            ship.bullet_level = min(3, ship.bullet_level + 1)
                        powerups.remove(powerup)

                explosions = [e for e in explosions if e.update()]

                difficulty = 1 + score / 100
                spawn_timer += 1 / FPS
                if spawn_timer > 2 / difficulty and len(asteroids) < 10:
                    spawn_timer = 0
                    size = "small" if random.random() < 0.7 else "large"
                    asteroids.append(Asteroid(size, difficulty))

                if score >= 1000:
                    state = "WIN"
                    high_score = max(high_score, score)
                    if background_music:
                        pygame.mixer.music.stop()

                screen.blit(game_background, (0, 0))
                screen.blit(ship.image, ship.rect)
                for asteroid in asteroids:
                    screen.blit(asteroid.image, asteroid.rect)
                    health_width = (20 if asteroid.size == "small" else 40) * (asteroid.health / (20 if asteroid.size == "small" else 50))
                    pygame.draw.rect(screen, RED, (asteroid.x - 10, asteroid.y - 20, 20 if asteroid.size == "small" else 40, 5))
                    pygame.draw.rect(screen, GREEN, (asteroid.x - 10, asteroid.y - 20, health_width, 5))
                for missile in missiles:
                    screen.blit(missile.image, missile.rect)
                for powerup in powerups:
                    screen.blit(powerup.image, powerup.rect)
                for explosion in explosions:
                    screen.blit(explosion.image, explosion.rect)

                health_color = GREEN if ship.health > 75 else YELLOW if ship.health > 30 else RED
                pygame.draw.rect(screen, RED, (10, 10, 240, 20))
                pygame.draw.rect(screen, health_color, (10, 10, ship.health * 240 / 150, 20))
                pygame.draw.rect(screen, WHITE, (10, 10, 240, 20), 2)
                health_text = font.render(f"Health: {ship.health}", True, WHITE)
                screen.blit(health_text, (10, 35))
                score_text = font.render(f"Score: {score}", True, YELLOW)
                screen.blit(score_text, (10, 60))

                high_score_text = font.render(f"High Score: {high_score}", True, YELLOW)
                screen.blit(high_score_text, (WIDTH - high_score_text.get_width() - 10, 10))

            draw_menu_button()
            draw_menu_options()

        elif state == "WIN":
            screen.blit(menu_background, (0, 0))
            win_text = large_font.render("Win!", True, GREEN)
            screen.blit(win_text, (WIDTH // 2 - win_text.get_width() // 2, HEIGHT // 4))
            draw_button("Play Again", WIDTH // 2 - 60, HEIGHT // 2, 120, 40, GREEN, (0, 200, 0), start_game)
            draw_button("Main Menu", WIDTH // 2 - 60, HEIGHT // 2 + 60, 120, 40, GREEN, (0, 200, 0), go_to_menu)

        elif state == "LOSS":
            screen.blit(menu_background, (0, 0))
            loss_text = large_font.render("Loss!", True, RED)
            screen.blit(loss_text, (WIDTH // 2 - loss_text.get_width() // 2, HEIGHT // 4))
            draw_button("Play Again", WIDTH // 2 - 60, HEIGHT // 2, 120, 40, GREEN, (0, 200, 0), start_game)
            draw_button("Main Menu", WIDTH // 2 - 60, HEIGHT // 2 + 60, 120, 40, GREEN, (0, 200, 0), go_to_menu)

        pygame.display.flip()
        clock.tick(FPS)
        await asyncio.sleep(1.0 / FPS)

    pygame.quit()

if platform.system() == "Emscripten":
    asyncio.ensure_future(main())
else:
    if __name__ == "__main__":
        asyncio.run(main())