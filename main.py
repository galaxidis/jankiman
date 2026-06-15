import pygame
import sys
import random
import math
import asyncio
import array

# Initialisierung von Pygame
pygame.init()
pygame.mixer.init()

# Konstanten für das Retro-Gefühl
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
VIRTUAL_WIDTH = 400
VIRTUAL_HEIGHT = 300
FPS = 60

# Farbpalette (Retro Neon / CRT Stil)
COLOR_BLACK = (10, 10, 15)
COLOR_WHITE = (230, 230, 240)
COLOR_GREEN = (50, 255, 50)
COLOR_RED = (255, 50, 50)
COLOR_YELLOW = (255, 255, 50)
COLOR_CYAN = (50, 255, 255)
COLOR_MAGENTA = (255, 50, 255)
COLOR_BLUE = (50, 50, 255)
COLOR_DARK_GRAY = (40, 40, 50)

# Sound-Synthesizer für 100% Dateisicherheit ohne externe Assets
def generate_retro_sound(freq_start, freq_end, duration, wave_type="sine"):
    """Generiert einen Retro-Soundbeeffekt im Speicher, um keine externen Audio-Dateien zu benötigen."""
    try:
        sample_rate = 22050
        num_samples = int(sample_rate * duration)
        buf = array.array('h')
        
        for i in range(num_samples):
            t = i / sample_rate
            current_freq = freq_start + (freq_end - freq_start) * (t / duration)
            
            if wave_type == "sine":
                val = math.sin(2 * math.pi * current_freq * t)
            elif wave_type == "square":
                val = 1.0 if math.sin(2 * math.pi * current_freq * t) > 0 else -1.0
            elif wave_type == "noise":
                val = random.uniform(-1.0, 1.0)
            else:
                val = math.sin(2 * math.pi * current_freq * t)
                
            envelope = 1.0 - (t / duration)
            sample = int(val * envelope * 16383)
            buf.append(sample)
            
        return pygame.mixer.Sound(buffer=buf)
    except Exception:
        return None

# Soundeffekte generieren
sound_jump = generate_retro_sound(150, 600, 0.15, "sine")
sound_shoot = generate_retro_sound(800, 100, 0.2, "square")
sound_explosion = generate_retro_sound(300, 40, 0.35, "noise")
sound_coin = generate_retro_sound(600, 1200, 0.1, "sine")

def play_sound(sound):
    if sound:
        try:
            sound.play()
        except Exception:
            pass

class Player:
    def __init__(self):
        self.width = 14
        self.height = 20
        self.reset()
        
    def reset(self):
        self.x = 50
        self.y = 150
        self.vx = 0
        self.vy = 0
        self.on_ground = False
        self.score = 0
        self.lives = 3
        self.shoot_cooldown = 0
        self.direction = 1 # 1 = Rechts, -1 = Links
        self.state = "STAND" # STAND, RUN, JUMP
        self.anim_frame = 0

    def jump(self):
        if self.on_ground:
            self.vy = -7.5
            self.on_ground = False
            play_sound(sound_jump)

    def shoot(self, bullets):
        if self.shoot_cooldown == 0:
            bx = self.x + (self.width if self.direction == 1 else -8)
            by = self.y + 8
            bullets.append(Bullet(bx, by, self.direction))
            self.shoot_cooldown = 15
            play_sound(sound_shoot)

    def update(self, keys, platforms):
        move_speed = 2.5
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vx = -move_speed
            self.direction = -1
            self.state = "RUN"
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.vx = move_speed
            self.direction = 1
            self.state = "RUN"
        else:
            self.vx = 0
            if self.on_ground:
                self.state = "STAND"

        # Schwerkraft
        self.vy += 0.35
        if self.vy > 8:
            self.vy = 8

        # Bewegung X & Kollision X
        self.x += self.vx
        player_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        for platform in platforms:
            plat_rect = pygame.Rect(platform.x, platform.y, platform.width, platform.height)
            if player_rect.colliderect(plat_rect):
                if self.vx > 0:
                    self.x = platform.x - self.width
                elif self.vx < 0:
                    self.x = platform.x + platform.width

        # Bewegung Y & Kollision Y
        self.y += self.vy
        self.on_ground = False
        player_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
        for platform in platforms:
            plat_rect = pygame.Rect(platform.x, platform.y, platform.width, platform.height)
            if player_rect.colliderect(plat_rect):
                if self.vy > 0: # Fällt nach unten
                    self.y = platform.y - self.height
                    self.vy = 0
                    self.on_ground = True
                elif self.vy < 0: # Springt nach oben
                    self.y = platform.y + platform.height
                    self.vy = 0

        if not self.on_ground:
            self.state = "JUMP"
        self.anim_frame = (self.anim_frame + 1) % 30

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

        if self.y > VIRTUAL_HEIGHT:
            self.lives -= 1
            play_sound(sound_explosion)
            self.x = 50
            self.y = 100
            self.vy = 0

    def draw(self, surface):
        # NORDISCHER WIKINGER (Jankiman) in nativem Pygame gerendert!
        
        # 1. Kettenhemd / Tunic (Körper) - Stahlblau
        pygame.draw.rect(surface, (58, 102, 163), (self.x + 1, self.y + 11, 12, 7))

        # Goldener Gürtel & Schnalle
        pygame.draw.rect(surface, (255, 215, 0), (self.x + 1, self.y + 15, 12, 2))
        pygame.draw.rect(surface, (230, 230, 240), (self.x + 6, self.y + 14, 2, 4))

        # 2. Roter Wikingerbart (Bushy)
        pygame.draw.rect(surface, (255, 102, 0), (self.x + 2, self.y + 6, 10, 6))
        if self.direction == 1:
            pygame.draw.rect(surface, (255, 102, 0), (self.x + 7, self.y + 8, 7, 4))
        else:
            pygame.draw.rect(surface, (255, 102, 0), (self.x, self.y + 8, 7, 4))

        # 3. Gesicht & Augen (Skin Color)
        pygame.draw.rect(surface, (255, 219, 172), (self.x + 3, self.y + 4, 8, 4))
        eye_x = self.x + 7 if self.direction == 1 else self.x + 4
        pygame.draw.rect(surface, (230, 230, 240), (eye_x, self.y + 4, 3, 2))
        pupil_x = self.x + 9 if self.direction == 1 else self.x + 4
        pygame.draw.rect(surface, (10, 10, 15), (pupil_x, self.y + 4, 1, 2))

        # 4. Wikinger-Helm
        pygame.draw.rect(surface, (160, 160, 168), (self.x + 2, self.y, 10, 5))
        pygame.draw.rect(surface, (208, 208, 216), (self.x + 1, self.y + 3, 12, 2))

        # Helm-Hörner (Weiß mit goldenen Spitzen)
        # Linkes Horn
        pygame.draw.rect(surface, (230, 230, 240), (self.x + 1, self.y - 3, 2, 4))
        pygame.draw.rect(surface, (230, 230, 240), (self.x - 1, self.y - 4, 3, 2))
        pygame.draw.rect(surface, (255, 215, 0), (self.x - 1, self.y - 5, 1, 2))
        # Rechtes Horn
        pygame.draw.rect(surface, (230, 230, 240), (self.x + 11, self.y - 3, 2, 4))
        pygame.draw.rect(surface, (230, 230, 240), (self.x + 12, self.y - 4, 3, 2))
        pygame.draw.rect(surface, (255, 215, 0), (self.x + 14, self.y - 5, 1, 2))

        # 5. Beine & Lederstiefel
        if self.state == "RUN" and (self.anim_frame // 10) % 2 == 0:
            pygame.draw.rect(surface, (92, 64, 51), (self.x + 1, self.y + 18, 4, 3))
            pygame.draw.rect(surface, (92, 64, 51), (self.x + 9, self.y + 17, 4, 3))
        else:
            pygame.draw.rect(surface, (92, 64, 51), (self.x + 2, self.y + 18, 4, 3))
            pygame.draw.rect(surface, (92, 64, 51), (self.x + 8, self.y + 18, 4, 3))

class Bullet:
    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.vx = direction * 5.5
        self.width = 6
        self.height = 3
        self.active = True

    def update(self):
        self.x += self.vx
        if self.x < 0 or self.x > VIRTUAL_WIDTH:
            self.active = False

    def draw(self, surface):
        color = random.choice([COLOR_RED, COLOR_YELLOW, COLOR_WHITE])
        pygame.draw.rect(surface, color, (self.x, self.y, self.width, self.height))

class Enemy:
    def __init__(self, x, y, walk_range=80):
        self.start_x = x
        self.x = x
        self.y = y
        self.width = 16
        self.height = 16
        self.vx = 1
        self.walk_range = walk_range
        self.active = True
        self.pulse = 0

    def update(self, platforms):
        self.pulse = (self.pulse + 0.1) % (math.pi * 2)
        self.x += self.vx
        
        if abs(self.x - self.start_x) > self.walk_range:
            self.vx *= -1

        self.y += 2
        enemy_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        for platform in platforms:
            plat_rect = pygame.Rect(platform.x, platform.y, platform.width, platform.height)
            if enemy_rect.colliderect(plat_rect):
                self.y = platform.y - self.height
                break

    def draw(self, surface):
        offset = math.sin(self.pulse) * 2
        pygame.draw.rect(surface, COLOR_MAGENTA, (self.x, self.y + offset, self.width, self.height), 1)
        pygame.draw.rect(surface, COLOR_CYAN, (self.x + 4, self.y + 4 + offset, 8, 8))
        pygame.draw.rect(surface, COLOR_WHITE, (self.x + 3, self.y + 2 + offset, 2, 2))
        pygame.draw.rect(surface, COLOR_WHITE, (self.x + 11, self.y + 2 + offset, 2, 2))

class Coin:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 8
        self.height = 8
        self.active = True
        self.anim_offset = random.uniform(0, 10)

    def draw(self, surface, frame_counter):
        sine = math.sin((frame_counter + self.anim_offset) * 0.15)
        w = max(1, int(self.width * abs(sine)))
        offset_x = (self.width - w) // 2
        pygame.draw.ellipse(surface, COLOR_YELLOW, (self.x + offset_x, self.y, w, self.height))
        if w > 3:
            pygame.draw.line(surface, COLOR_WHITE, (self.x + offset_x + 1, self.y + 2), (self.x + offset_x + 1, self.y + 5))

class Platform:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def draw(self, surface):
        pygame.draw.rect(surface, COLOR_DARK_GRAY, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(surface, COLOR_GREEN, (self.x, self.y, self.width, 3))
        for px in range(self.x + 8, self.x + self.width, 16):
            pygame.draw.line(surface, COLOR_BLACK, (px, self.y + 3), (px, self.y + self.height))

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.vx = random.uniform(-2, 2)
        self.vy = random.uniform(-2, 2)
        self.color = color
        self.life = 30

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1

    def draw(self, surface):
        if self.life > 0:
            size = max(1, int(self.life / 10))
            pygame.draw.rect(surface, self.color, (self.x, self.y, size, size))

class Game:
    def __init__(self):
        self.state = "ATTRACT"
        self.player = Player()
        self.platforms = []
        self.enemies = []
        self.coins = []
        self.bullets = []
        self.particles = []
        self.high_score = 10000
        self.frame_counter = 0
        self.level = 1
        
        self.virtual_screen = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT))
        self.real_screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        
        self.font = pygame.font.SysFont("Courier", 12, bold=True)
        self.font_large = pygame.font.SysFont("Courier", 24, bold=True)
        
        self.load_level()

    def load_level(self):
        self.platforms.clear()
        self.enemies.clear()
        self.coins.clear()
        self.bullets.clear()
        self.particles.clear()
        
        if self.level == 1:
            self.platforms.append(Platform(0, 270, 150, 30))
            self.platforms.append(Platform(180, 270, 220, 30))
            self.platforms.append(Platform(50, 200, 100, 12))
            self.platforms.append(Platform(220, 200, 120, 12))
            self.platforms.append(Platform(120, 130, 140, 12))
            
            self.coins.append(Coin(80, 175))
            self.coins.append(Coin(100, 175))
            self.coins.append(Coin(190, 100))
            self.coins.append(Coin(210, 100))
            self.coins.append(Coin(240, 175))
            
            self.enemies.append(Enemy(60, 170, 60))
            self.enemies.append(Enemy(230, 170, 80))
            
        elif self.level == 2:
            self.platforms.append(Platform(0, 270, 100, 30))
            self.platforms.append(Platform(120, 240, 100, 12))
            self.platforms.append(Platform(260, 210, 140, 12))
            self.platforms.append(Platform(140, 140, 100, 12))
            self.platforms.append(Platform(20, 100, 90, 12))
            
            self.coins.append(Coin(150, 110))
            self.coins.append(Coin(170, 110))
            self.coins.append(Coin(50, 70))
            self.coins.append(Coin(300, 180))
            
            self.enemies.append(Enemy(130, 110, 60))
            self.enemies.append(Enemy(280, 180, 90))
            
        else:
            self.state = "VICTORY"

    def spawn_particles(self, x, y, color, count=10):
        for _ in range(count):
            self.particles.append(Particle(x, y, color))

    def update(self, keys):
        self.frame_counter += 1
        
        if self.state == "ATTRACT":
            if keys[pygame.K_RETURN] or keys[pygame.K_SPACE]:
                self.player.reset()
                self.level = 1
                self.load_level()
                self.state = "PLAYING"
                
        elif self.state == "PLAYING":
            self.player.update(keys, self.platforms)
            
            if keys[pygame.K_x] or keys[pygame.K_j] or keys[pygame.K_LCTRL]:
                self.player.shoot(self.bullets)
                
            if keys[pygame.K_UP] or keys[pygame.K_w] or keys[pygame.K_SPACE]:
                self.player.jump()

            for bullet in self.bullets[:]:
                bullet.update()
                if not bullet.active:
                    self.bullets.remove(bullet)

            for enemy in self.enemies[:]:
                if enemy.active:
                    enemy.update(self.platforms)
                    
                    player_rect = pygame.Rect(self.player.x, self.player.y, self.player.width, self.player.height)
                    enemy_rect = pygame.Rect(enemy.x, enemy.y, enemy.width, enemy.height)
                    
                    if player_rect.colliderect(enemy_rect):
                        if self.player.vy > 0 and self.player.y + self.player.height - self.player.vy <= enemy.y + 4:
                            enemy.active = False
                            self.enemies.remove(enemy)
                            self.player.vy = -5.0
                            self.player.score += 200
                            self.spawn_particles(enemy.x + 8, enemy.y + 8, COLOR_MAGENTA, 15)
                            play_sound(sound_explosion)
                        else:
                            self.player.lives -= 1
                            self.spawn_particles(self.player.x + 8, self.player.y + 8, COLOR_RED, 20)
                            play_sound(sound_explosion)
                            self.player.x = 50
                            self.player.y = 100
                            self.player.vy = 0
                            if self.player.lives <= 0:
                                self.state = "GAMEOVER"
                                if self.player.score > self.high_score:
                                    self.high_score = self.player.score

                    for bullet in self.bullets[:]:
                        b_rect = pygame.Rect(bullet.x, bullet.y, bullet.width, bullet.height)
                        if b_rect.colliderect(enemy_rect):
                            enemy.active = False
                            if enemy in self.enemies:
                                self.enemies.remove(enemy)
                            bullet.active = False
                            if bullet in self.bullets:
                                self.bullets.remove(bullet)
                            self.player.score += 150
                            self.spawn_particles(enemy.x + 8, enemy.y + 8, COLOR_CYAN, 12)
                            play_sound(sound_explosion)

            for coin in self.coins[:]:
                coin_rect = pygame.Rect(coin.x, coin.y, coin.width, coin.height)
                player_rect = pygame.Rect(self.player.x, self.player.y, self.player.width, self.player.height)
                if player_rect.colliderect(coin_rect):
                    self.coins.remove(coin)
                    self.player.score += 100
                    play_sound(sound_coin)
                    self.spawn_particles(coin.x + 4, coin.y + 4, COLOR_YELLOW, 8)
                    
            if len(self.coins) == 0 and len(self.enemies) == 0:
                self.level += 1
                self.load_level()

            for p in self.particles[:]:
                p.update()
                if p.life <= 0:
                    self.particles.remove(p)
                    
        elif self.state in ["GAMEOVER", "VICTORY"]:
            if keys[pygame.K_RETURN] or keys[pygame.K_SPACE]:
                self.state = "ATTRACT"

    def draw(self):
        self.virtual_screen.fill(COLOR_BLACK)
        
        for y in range(0, VIRTUAL_HEIGHT, 30):
            brightness = 15 + int(math.sin(self.frame_counter * 0.02 + y) * 5)
            pygame.draw.line(self.virtual_screen, (brightness, brightness, brightness + 10), (0, y), (VIRTUAL_WIDTH, y))
        for x in range(0, VIRTUAL_WIDTH, 40):
            pygame.draw.line(self.virtual_screen, (15, 15, 25), (x, 0), (x, VIRTUAL_HEIGHT))

        if self.state == "ATTRACT":
            title_text = "JANKIMAN"
            label = self.font_large.render(title_text, True, COLOR_CYAN)
            self.virtual_screen.blit(label, (VIRTUAL_WIDTH // 2 - label.get_width() // 2, 60))
            
            sub_text = "NORDIC RETRO ADVENTURE"
            label_sub = self.font.render(sub_text, True, COLOR_MAGENTA)
            self.virtual_screen.blit(label_sub, (VIRTUAL_WIDTH // 2 - label_sub.get_width() // 2, 90))
            
            if (self.frame_counter // 20) % 2 == 0:
                coin_label = self.font_large.render("INSERT COIN", True, COLOR_YELLOW)
                self.virtual_screen.blit(coin_label, (VIRTUAL_WIDTH // 2 - coin_label.get_width() // 2, 140))
                
            info_label1 = self.font.render("PFEILTASTEN / WASD : BEWEGEN", True, COLOR_WHITE)
            info_label2 = self.font.render("Z-TASTE / LCTRL     : FEUER", True, COLOR_WHITE)
            info_label3 = self.font.render("DRUECKE ENTER ZUM STARTEN", True, COLOR_GREEN)
            
            self.virtual_screen.blit(info_label1, (VIRTUAL_WIDTH // 2 - info_label1.get_width() // 2, 210))
            self.virtual_screen.blit(info_label2, (VIRTUAL_WIDTH // 2 - info_label2.get_width() // 2, 230))
            self.virtual_screen.blit(info_label3, (VIRTUAL_WIDTH // 2 - info_label3.get_width() // 2, 260))

        elif self.state == "PLAYING":
            for platform in self.platforms:
                platform.draw(self.virtual_screen)
                
            for coin in self.coins:
                coin.draw(self.virtual_screen, self.frame_counter)
                
            for enemy in self.enemies:
                enemy.draw(self.virtual_screen)
                
            for bullet in self.bullets:
                bullet.draw(self.virtual_screen)
                
            for p in self.particles:
                p.draw(self.virtual_screen)
                
            self.player.draw(self.virtual_screen)

            hud_score = f"SCORE: {self.player.score:06d}"
            hud_high = f"HI-SCORE: {self.high_score:06d}"
            hud_lives = f"LIVES: {'V' * self.player.lives}"
            hud_level = f"STAGE {self.level}"
            
            lbl_score = self.font.render(hud_score, True, COLOR_WHITE)
            lbl_high = self.font.render(hud_high, True, COLOR_RED)
            lbl_lives = self.font.render(hud_lives, True, COLOR_GREEN)
            lbl_level = self.font.render(hud_level, True, COLOR_CYAN)
            
            self.virtual_screen.blit(lbl_score, (10, 5))
            self.virtual_screen.blit(lbl_high, (VIRTUAL_WIDTH // 2 - lbl_high.get_width() // 2, 5))
            self.virtual_screen.blit(lbl_lives, (VIRTUAL_WIDTH - lbl_lives.get_width() - 10, 5))
            self.virtual_screen.blit(lbl_level, (10, VIRTUAL_HEIGHT - 20))

        elif self.state == "GAMEOVER":
            label = self.font_large.render("GAME OVER", True, COLOR_RED)
            score_lbl = self.font.render(f"DEIN RETRO SCORE: {self.player.score}", True, COLOR_WHITE)
            retry_lbl = self.font.render("DRUECKE ENTER FUER HAUPTMENUE", True, COLOR_YELLOW)
            
            self.virtual_screen.blit(label, (VIRTUAL_WIDTH // 2 - label.get_width() // 2, 100))
            self.virtual_screen.blit(score_lbl, (VIRTUAL_WIDTH // 2 - score_lbl.get_width() // 2, 140))
            self.virtual_screen.blit(retry_lbl, (VIRTUAL_WIDTH // 2 - retry_lbl.get_width() // 2, 180))

        elif self.state == "VICTORY":
            label = self.font_large.render("WINNER! CHAMPION!", True, COLOR_GREEN)
            score_lbl = self.font.render(f"ENDSTAND: {self.player.score}", True, COLOR_YELLOW)
            retry_lbl = self.font.render("DRUECKE ENTER FUER HAUPTMENUE", True, COLOR_WHITE)
            
            self.virtual_screen.blit(label, (VIRTUAL_WIDTH // 2 - label.get_width() // 2, 100))
            self.virtual_screen.blit(score_lbl, (VIRTUAL_WIDTH // 2 - score_lbl.get_width() // 2, 140))
            self.virtual_screen.blit(retry_lbl, (VIRTUAL_WIDTH // 2 - retry_lbl.get_width() // 2, 180))

        scaled_surf = pygame.transform.scale(self.virtual_screen, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.real_screen.blit(scaled_surf, (0, 0))

        for y in range(0, SCREEN_HEIGHT, 3):
            pygame.draw.line(self.real_screen, (0, 0, 0, 80), (0, y), (SCREEN_WIDTH, y))

        return self.real_screen

async def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Jankiman - Retro Arcade (MAME Style)")
    
    clock = pygame.time.Clock()
    game = Game()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()

        keys = pygame.key.get_pressed()
        game.update(keys)
        frame_surface = game.draw()
        
        screen.blit(frame_surface, (0, 0))
        pygame.display.flip()
        
        clock.tick(FPS)
        await asyncio.sleep(0)

if __name__ == "__main__":
    asyncio.run(main())
