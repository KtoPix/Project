import pygame
import random
import math
import sys

# Инициализация Pygame
pygame.init()

# Размеры экрана
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 1000
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Стрелялка")

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
GRAY = (150, 150, 150)  # Новый цвет для щита

# Состояния игры
GAME_STATE_MENU = 0  # Меню
GAME_STATE_PLAYING = 1  # Играем
GAME_STATE_GAME_OVER = 2  # Конец игры

# Загрузка изображения врага
enemy_image = pygame.image.load("angry.png")  # Путь к вашему изображению


# Класс кнопки
class Button:
    def __init__(self, x, y, width, height, text, color, hover_color, action):
        self.rect = pygame.Rect(x, y, width, height)  # Прямоугольник кнопки
        self.text = text  # Текст кнопки
        self.color = color  # Цвет кнопки
        self.hover_color = hover_color  # Цвет при наведении
        self.action = action  # Действие при нажатии
        self.font = pygame.font.Font(None, 36)  # Шрифт

    def draw(self, screen):
        color = self.color  # Цвет кнопки
        if self.rect.collidepoint(pygame.mouse.get_pos()):  # Если курсор над кнопкой
            color = self.hover_color  # Меняем цвет на цвет при наведении
        pygame.draw.rect(screen, color, self.rect)  # Рисуем кнопку
        text_surface = self.font.render(self.text, True, BLACK)  # Рендерим текст
        text_rect = text_surface.get_rect(center=self.rect.center)  # Выравниваем текст
        screen.blit(text_surface, text_rect)  # Выводим текст на экран

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):  # Если на кнопку нажали мышкой
            self.action()  # Выполняем действие


# Игрок - убрали спрайт
class Player:
    def __init__(self, color, width, height):

        self.image = pygame.Surface([width, height])  # Создаем поверхность для игрока
        self.image.fill(color)  # Заливаем цветом
        self.rect = self.image.get_rect()  # Получаем прямоугольник поверхности
        self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)  # Ставим в центр экрана
        self.speed = 5  # скорость игрока
        # Добавляем щит
        self.shield_image = pygame.Surface([width + 10, height + 10])  # Поверхность для щита
        self.shield_image.fill(GRAY)  # Заливаем серым
        self.shield_rect = self.shield_image.get_rect(
            center=self.rect.center)  # Получаем прямоугольник щита и ставим в центр

        self.lives = 3  # Начальное количество жизней
        self.max_lives = 3  # Максимальное количество жизней
        self.hit_damage = 1  # начальный урон от столкновения
        self.start_time = 0  # Время начала игры

    def update(self):
        self.shield_rect.center = self.rect.center  # Перемещаем щит в центр игрока
        keys = pygame.key.get_pressed()  # Получаем нажатые клавиши
        if keys[pygame.K_w]:  # Если нажата W
            self.rect.y -= self.speed  # Перемещаем вверх
        if keys[pygame.K_s]:  # Если нажата S
            self.rect.y += self.speed  # Перемещаем вниз
        if keys[pygame.K_a]:  # Если нажата A
            self.rect.x -= self.speed  # Перемещаем влево
        if keys[pygame.K_d]:  # Если нажата D
            self.rect.x += self.speed  # Перемещаем вправо

        # Ограничиваем передвижение игрока по экрану
        if self.rect.left < 0:  # Если игрок ушел за левую границу
            self.rect.left = 0  # Ставим его на границу
        if self.rect.right > SCREEN_WIDTH:  # Если за правую границу
            self.rect.right = SCREEN_WIDTH  # Ставим на границу
        if self.rect.top < 0:  # Если за верхнюю границу
            self.rect.top = 0  # Ставим на границу
        if self.rect.bottom > SCREEN_HEIGHT:  # Если за нижнюю границу
            self.rect.bottom = SCREEN_HEIGHT  # Ставим на границу

    def draw(self, screen):
        screen.blit(self.shield_image, self.shield_rect)  # Рисуем щит
        screen.blit(self.image, self.rect)  # Рисуем игрока

    def shoot(self, target_x, target_y):
        bullet = Bullet(self.rect.centerx, self.rect.centery, target_x, target_y)  # Создаем пулю
        all_sprites.add(bullet)  # Добавляем пулю во все спрайты
        bullets.add(bullet)  # Добавляем пулю в группу пуль


# Враг - спрайт
class Enemy(pygame.sprite.Sprite):
    def __init__(self, enemy_type):
        super().__init__()
        self.enemy_type = enemy_type
        if enemy_type == 'fast':
            self.image = pygame.transform.scale(enemy_image, (20, 20))  # Уменьшаем изображение для быстрого врага
            self.speed_multiplier = 1.8 + random.random() * 0.5  # немного быстрее обычных
            self.lives = 1  # 1 жизнь
        elif enemy_type == 'strong':
            self.image = pygame.transform.scale(enemy_image, (40, 40))  # Увеличиваем изображение для сильного врага
            self.speed_multiplier = 0.8 + random.random() * 0.5  # медленнее
            self.lives = 2  # 2 жизни
        else:  # normal
            self.image = pygame.transform.scale(enemy_image, (30, 30))  # Обычный размер для обычного врага
            self.speed_multiplier = 1 + random.random() * 0.5  # случайное увеличение скорости от 1 до 1.5
            self.lives = 1  # 1 жизнь

        self.rect = self.image.get_rect()

        # Появление из случайного края
        side = random.randint(0, 3)  # Выбор случайного края (0-верх, 1-право, 2-низ, 3-лево)
        if side == 0:  # Верхний край
            self.rect.x = random.randint(0, SCREEN_WIDTH)
            self.rect.y = -30
        elif side == 1:  # Правый край
            self.rect.x = SCREEN_WIDTH + 30
            self.rect.y = random.randint(0, SCREEN_HEIGHT)
        elif side == 2:  # Нижний край
            self.rect.x = random.randint(0, SCREEN_WIDTH)
            self.rect.y = SCREEN_HEIGHT + 30
        else:  # Левый край
            self.rect.x = -30
            self.rect.y = random.randint(0, SCREEN_HEIGHT)

        # Направление движения к игроку
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery

        length = math.sqrt(dx * dx + dy * dy)  # Длина вектора до игрока
        self.speed_x = dx / length  # Нормализованный вектор
        self.speed_y = dy / length  # Нормализованный вектор

        self.speed_x *= self.speed_multiplier * 4  # Увеличиваем скорость
        self.speed_y *= self.speed_multiplier * 4  # Увеличиваем скорость

    def update(self):
        self.rect.x += self.speed_x  # Двигаем врага по оси х
        self.rect.y += self.speed_y  # Двигаем врага по оси у

        if self.rect.left > SCREEN_WIDTH or self.rect.right < 0 or self.rect.top > SCREEN_HEIGHT or self.rect.bottom < 0:  # Если враг за экраном
            self.kill()  # Удаляем врага


# Пуля - спрайт
class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, target_x, target_y):
        super().__init__()
        self.image = pygame.Surface([10, 10])  # Создаем поверхность
        self.image.fill(GREEN)  # Заливаем зеленым цветом
        self.rect = self.image.get_rect()  # Получаем прямоугольник
        self.rect.center = (x, y)  # Ставим в точку выстрела

        # Вычисление направления к курсору
        dx = target_x - self.rect.centerx
        dy = target_y - self.rect.centery
        length = math.sqrt(dx * dx + dy * dy)
        if length == 0:  # Если длина равна 0
            self.speed_x = 0
            self.speed_y = 0
        else:  # Иначе
            self.speed_x = dx / length * 8  # Нормализованный вектор, умножаем на скорость
            self.speed_y = dy / length * 8

    def update(self):
        self.rect.x += self.speed_x  # Двигаем пулю по оси х
        self.rect.y += self.speed_y  # Двигаем пулю по оси у
        if self.rect.left > SCREEN_WIDTH or self.rect.right < 0 or self.rect.top > SCREEN_HEIGHT or self.rect.bottom < 0:  # Если пуля за экраном
            self.kill()  # Удаляем пулю


# Инициализируем игровые переменные
game_state = GAME_STATE_MENU  # Начальное состояние - меню
all_sprites = pygame.sprite.Group()  # Группа всех спрайтов
enemies = pygame.sprite.Group()  # Группа врагов
bullets = pygame.sprite.Group()  # Группа пуль
player = None  # Игрок
clock = pygame.time.Clock()  # Таймер
enemy_timer = 0  # Таймер появления врагов
score = 0  # Очки
font = pygame.font.Font(None, 36)  # Шрифт

menu_images = []  # Список изображений для меню

# Инициализация меню
for _ in range(10):  # Создаем 10 смайликов
    size = random.randint(20, 80)  # Случайный размер
    x = random.randint(0, SCREEN_WIDTH - size)  # Случайное положение
    y = random.randint(0, SCREEN_HEIGHT - size)
    scaled_image = pygame.transform.scale(enemy_image, (size, size))  # Масштабируем изображение
    menu_images.append((scaled_image, (x, y)))  # Добавляем изображение в список

# Создаем кнопки
start_button = Button(
    SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 50, 200, 50, "Начать игру", WHITE, (200, 200, 200),
    lambda: set_game_state(GAME_STATE_PLAYING)  # Действие при нажатии на кнопку - начать игру
)

restart_button = Button(
    SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2, 200, 50, "В главное меню", WHITE, (200, 200, 200),
    lambda: set_game_state(GAME_STATE_MENU)  # Действие - в меню
)

play_again_button = Button(
    SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 + 70, 200, 50, "Начать заново", WHITE, (200, 200, 200),
    lambda: set_game_state(GAME_STATE_PLAYING)  # Действие - начать игру заново
)

# Переменная состояния паузы и таймер
is_paused = False
total_paused_time = 0  # Переменная для хранения суммарного времени паузы
pause_start_time = 0


# Функция для установки состояния игры
def set_game_state(state):
    global game_state, all_sprites, enemies, bullets, player, score, menu_images, is_paused, total_paused_time, pause_start_time
    game_state = state  # Меняем состояние
    is_paused = False  # Снимаем паузу при смене состояния
    total_paused_time = 0
    pause_start_time = 0

    if game_state == GAME_STATE_PLAYING:  # Если играем
        all_sprites = pygame.sprite.Group()  # Создаем группы
        enemies = pygame.sprite.Group()
        bullets = pygame.sprite.Group()
        score = 0  # Обнуляем счет

        player = Player(WHITE, 40, 40)  # Создаем игрока
        player.start_time = pygame.time.get_ticks()  # Засекаем время начала игры
    elif game_state == GAME_STATE_MENU:  # Если в меню
        all_sprites = pygame.sprite.Group()  # Создаем группы
        enemies = pygame.sprite.Group()
        bullets = pygame.sprite.Group()
        player = None  # Обнуляем игрока
    elif game_state == GAME_STATE_GAME_OVER:  # Если конец игры
        all_sprites = pygame.sprite.Group()  # Создаем группы
        enemies = pygame.sprite.Group()
        bullets = pygame.sprite.Group()


# Функция для отрисовки меню
def draw_menu():
    screen.fill(BLACK)  # Заливаем фон черным
    start_button.draw(screen)  # Рисуем кнопку

    font = pygame.font.Font(None, 72)  # Шрифт для заголовка
    text_surface = font.render("Добро пожаловать!", True, WHITE)  # Рендерим заголовок
    text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4))  # Ставим в центр
    screen.blit(text_surface, text_rect)  # Рисуем заголовок

    for image, pos in menu_images:  # Выводим все смайлики из списка
        screen.blit(image, pos)


# Функция отрисовки экрана конца игры
def draw_game_over():
    screen.fill(BLACK)  # Заливаем фон черным
    font = pygame.font.Font(None, 72)  # Шрифт для надписи
    text_surface = font.render("Game Over", True, RED)  # Рендерим надпись
    text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4))  # Ставим надпись по центру
    screen.blit(text_surface, text_rect)  # Выводим текст на экран

    # Выводим счет
    font = pygame.font.Font(None, 48)  # Шрифт для счета
    score_text_surface = font.render(f"Score: {score}", True, WHITE)  # Рендерим счет
    score_text_rect = score_text_surface.get_rect(
        center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))  # Выравниваем счет
    screen.blit(score_text_surface, score_text_rect)  # Выводим на экран

    restart_button.draw(screen)  # Рисуем кнопку в меню
    play_again_button.draw(screen)  # Рисуем кнопку играть заново


# Функция отрисовки игрового интерфейса (изменена)
def draw_ui(screen, player, start_time):
    if player:
        # Полоска здоровья
        health_bar_width = 200
        health_bar_height = 20
        health_bar_x = 10
        health_bar_y = 10

        health_ratio = player.lives / player.max_lives
        health_width = int(health_bar_width * health_ratio)

        pygame.draw.rect(screen, RED, (health_bar_x, health_bar_y, health_bar_width, health_bar_height))
        pygame.draw.rect(screen, GREEN, (health_bar_x, health_bar_y, health_width, health_bar_height))

        # Таймер
        # Вычисляем время, прошедшее с момента запуска игры
        elapsed_time = (pygame.time.get_ticks() - player.start_time - total_paused_time) / 1000
        time_text = font.render(f"Time: {elapsed_time:.1f}", True, WHITE)
        time_rect = time_text.get_rect(topright=(SCREEN_WIDTH - 10, 10))
        screen.blit(time_text, time_rect)


# Главный цикл игры
running = True
enemy_spawn_interval = 20
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if game_state == GAME_STATE_MENU:
            start_button.handle_event(event)
        elif game_state == GAME_STATE_GAME_OVER:
            restart_button.handle_event(event)
            play_again_button.handle_event(event)
        elif game_state == GAME_STATE_PLAYING and event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and player is not None:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                player.shoot(mouse_x, mouse_y)
        # Пауза при нажатии Esc
        elif game_state == GAME_STATE_PLAYING and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                is_paused = not is_paused
                if is_paused:
                    pause_start_time = pygame.time.get_ticks()  # запоминаем время начала паузы
                else:
                    total_paused_time += pygame.time.get_ticks() - pause_start_time  # Добавляем время паузы
                    pause_start_time = 0

    # Логика и отрисовка игры в зависимости от состояния
    if game_state == GAME_STATE_MENU:
        draw_menu()
    elif game_state == GAME_STATE_PLAYING:
        screen.fill(BLACK)
        if not is_paused:
            # Создаем врагов
            enemy_timer += clock.tick()
            if enemy_timer > enemy_spawn_interval:
                enemy_type = random.choices(['normal', 'fast', 'strong'], weights=[7, 2, 1])[0]
                enemy = Enemy(enemy_type)
                all_sprites.add(enemy)
                enemies.add(enemy)
                enemy_timer = 0

            # Обновление спрайтов
            all_sprites.update()

            if player:
                player.update()
                player.draw(screen)

            # Проверка столкновений
            hits = pygame.sprite.groupcollide(enemies, bullets, False, True)
            if hits:
                for enemy in hits:
                    enemy.lives -= 1
                    if enemy.lives <= 0:
                        enemy.kill()
                        score += 10

            if player:
                current_time = pygame.time.get_ticks()
                elapsed_time = (current_time - player.start_time) / 1000

                if elapsed_time > 180:
                    player.hit_damage = 3
                elif elapsed_time > 60:
                    player.hit_damage = 2

                for enemy in enemies:
                    if player.shield_rect.colliderect(enemy.rect):
                        player.lives -= player.hit_damage
                        enemy.kill()
                        if player.lives <= 0:
                            set_game_state(GAME_STATE_GAME_OVER)
        else:
            pause_text = font.render("Пауза", True, WHITE)
            pause_rect = pause_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(pause_text, pause_rect)

        all_sprites.draw(screen)
        if player:
            # Отображение интерфейса, но время вычисляется иначе
            draw_ui(screen, player, player.start_time)

    elif game_state == GAME_STATE_GAME_OVER:
        draw_game_over()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()