import pygame
from pygame.sprite import Group
from settings import Settings
from ship import Ship
from bullet import Bullet
from alien import Alien
import game_functions as gf
from game_stats import GameStats
from button import Button
from scoreboard import Scoreboard


def run_game():
    # инициализация игры , settings и объекта экрана
    pygame.init()
    ai_settings = Settings()
    screen = pygame.display.set_mode((ai_settings.screen_width, ai_settings.screen_height))
    pygame.display.set_caption("Alien Invasion")

    # Создание экземпляра для хранения игровой статистики и создаём экзмпляр счёта
    stats = GameStats(ai_settings)
    sb = Scoreboard(ai_settings, screen, stats)

    # Создание корабля.

    ship = Ship(ai_settings, screen)

    # создание группы пуль
    bullets = Group()

    # создание кнопки play
    play_button = Button(ai_settings, screen, "играть")

    # создание группы пришельцев
    aliens = Group()

    # создание флота пришельцев
    gf.create_fleet(ai_settings, screen,  ship, aliens)


    # Запуск основного цикла игры.
    while True:
        gf.check_events(ai_settings, screen, stats, sb, play_button, ship, aliens, bullets)
        if stats.game_active:
            ship.update()
            gf.update_bullets(ai_settings, screen, stats, sb, ship, aliens, bullets)
            gf.check_bullet_alien_collisions(ai_settings, screen, stats, sb, ship, aliens, bullets)
            gf.update_aliens(ai_settings, stats, sb,  screen, ship, aliens, bullets)
        gf.update_screen(ai_settings, screen, stats, sb, ship, aliens, bullets, play_button)


run_game()