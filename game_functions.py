import sys
import pygame
from time import sleep

from bullet import Bullet
from alien import Alien


def check_events(ai_settings, screen, stats, sb, play_button, ship, aliens, bullets):
    """Обрабатывает нажатия клавиш и события мыши."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            chek_keydown_events(event, ai_settings, screen, stats, ship, bullets)
        elif event.type == pygame.KEYUP:
            chek_keyup_events(event, ship)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            check_play_button(ai_settings, screen, stats, sb, play_button, ship, aliens, bullets, mouse_x, mouse_y)


def chek_keydown_events(event, ai_settings, screen, stats, ship, bullets):
    """ ревгриует на нажатие клавиш """
    if event.key == pygame.K_RIGHT:
        # Переместить корабль вправо.
        ship.moving_right = True
    elif event.key == pygame.K_LEFT:
        # Переместить корабль влево.
        ship.moving_left = True
    elif event.key == pygame.K_SPACE:
        fire_bullet(ai_settings, screen, ship, bullets)
    elif event.key == pygame.K_q:
        sys.exit()
    elif event.key == pygame.K_p:
        play(stats)
    elif event.key == pygame.K_x:
        pornomod(ai_settings, ship)#, alien)
    elif event.key == pygame.K_n:
        normal(ai_settings, ship)


def chek_keyup_events(event, ship):
    """ ревгриует на отпускание клавиш """
    if event.key == pygame.K_RIGHT:
        # Переместить корабль вправо.
        ship.moving_right = False
    elif event.key == pygame.K_LEFT:
        # Переместить корабль влево.
        ship.moving_left = False


def play(stats):
    # Сброс игровой статистики.
    pygame.mouse.set_visible(False)
    stats.reset_stats()
    stats.game_active = True



def check_play_button(ai_settings, screen, stats, sb, play_button, ship, aliens, bullets, mouse_x, mouse_y):
    """Запускает новую игру при нажатии кнопки Play."""
    button_cliked = play_button.rect.collidepoint(mouse_x, mouse_y)
    if button_cliked and not stats.game_active:
        ai_settings.initialize_dynamic_settings()
        play(stats)
        # Сброс игровой статистики и уровня
        sb.prep_score()
        sb.prep_high_score()
        sb.prep_level()
        sb.prep_ships()
        # Очистка списков пришельцев и пуль.
        aliens.empty()
        bullets.empty()

        # Создание нового флота и размещение корабля в центре.
        create_fleet(ai_settings, screen, ship, aliens)
        ship.center_ship()


def update_screen(ai_settings, screen, stats, sb, ship, aliens, bullets, play_button):
    # При каждом проходе цикла перерисовывается экран.
    # Все пули выводятся позади изображений корабля и пришельцев.
    screen.fill(ai_settings.bg_color)
    for bullet in bullets.sprites():
        bullet.draw_bullet()
    ship.blitme()
    aliens.draw(screen)
    sb.show_score()
    # Кнопка Play отображается в том случае, если игра неактивна.
    if not stats.game_active:
        play_button.draw_button()
    # Отображение последнего прорисованного экрана.
    pygame.display.flip()


def update_bullets(ai_settings, screen, stats, sb, ship, aliens, bullets):
    """Обновляет позиции пуль и уничтожает старые пули."""
    # Обновление позиций пуль.
    bullets.update()
    # Удаление пуль, вышедших за край экрана.
    for bullet in bullets.copy():
        if bullet.rect.bottom <= 0:
            bullets.remove(bullet)


def check_bullet_alien_collisions(ai_settings, screen, stats, sb, ship, aliens, bullets):
    """Обработка коллизий пуль с пришельцами."""
    # Проверка попаданий в пришельцев.
    # При обнаружении попадания удалить пулю и пришельца.
    collisions = pygame.sprite.groupcollide(bullets, aliens, True, True)
    if collisions:
        for aliens in collisions.values():
            stats.score += ai_settings.alien_points * len(aliens)
            sb.prep_score()
        check_high_score(stats, sb)
    if len(aliens) == 0:
        # Уничтожение пуль, повышение скорости и создание нового флота.
        stats.level += 1
        sb.prep_level()
        bullets.empty()
        ai_settings.increase_speed()
        create_fleet(ai_settings, screen, ship, aliens)


def update_aliens(ai_settings, stats, sb, screen, ship, aliens, bullets):
    """
    Проверяет, достиг ли флот края экрана,
      после чего обновляет позиции всех пришельцев во флоте.
    """
    check_fleet_edges(ai_settings, aliens)
    aliens.update()

    # проверяет столконовение alien-ship.
    if pygame.sprite.spritecollideany(ship, aliens):
        ship_hit(ai_settings, stats, sb, screen, ship, aliens, bullets)
    # Проверка пришельцев, добравшихся до нижнего края экрана.
    check_aliens_bottom(ai_settings, stats, sb, screen, ship, aliens, bullets)


def fire_bullet(ai_settings, screen, ship, bullets):
    """Выпускает пулю, если максимум еще не достигнут."""
    # Создание новой пули и включение ее в группу bullets.
    if len(bullets) < ai_settings.bullets_allowed:
        # Создание новой пули и включение ее в группу bullets.
        new_bullet = Bullet(ai_settings, screen, ship)
        bullets.add(new_bullet)


def create_fleet(ai_settings, screen, ship, aliens):
    """Создает флот пришельцев."""
    # Создание пришельца и вычисление количества пришельцев в ряду.
    alien = Alien(ai_settings, screen)
    number_aliens_x = get_number_aliens_x(ai_settings, alien.rect.width)
    number_rows = get_number_rows(ai_settings, ship.rect.height, alien.rect.height)
    for row_number in range(number_rows):
        # Создание первого ряда пришельцев.
        for alien_number in range(number_aliens_x):
            # Создание пришельца и размещение его в ряду.
            create_alien(ai_settings, screen, aliens, alien_number, row_number)


def get_number_aliens_x(ai_settings, alien_width):
    """Вычисляет количество пришельцев в ряду."""
    available_space_x = ai_settings.screen_width - (alien_width * 2)
    number_aliens_x = int(available_space_x / (alien_width * 2))
    return number_aliens_x


def create_alien(ai_settings, screen, aliens, alien_number, row_number):
    """Создает пришельца и размещает его в ряду."""
    alien = Alien(ai_settings, screen)
    alien_width = alien.rect.width
    alien.x = alien_width + 2 * alien_width * alien_number
    alien.rect.x = alien.x
    alien.rect.y = alien.rect.height + 2 * alien.rect.height * row_number
    aliens.add(alien)


def get_number_rows(ai_settings, ship_height, alien_height):
    """Определяет количество рядов, помещающихся на экране."""
    available_space_y = (ai_settings.screen_height - (3 * alien_height) - ship_height)
    number_rows = int(available_space_y / (ship_height * 2))
    return number_rows


def check_fleet_edges(ai_settings, aliens):
    """Реагирует на достижение пришельцем края экрана."""
    for alien in aliens.sprites():
        if alien.check_edges():
            change_fleet_direction(ai_settings, aliens)
            break


def change_fleet_direction(ai_settings, aliens):
    """Опускает весь флот и меняет направление флота."""
    for alien in aliens.sprites():
        alien.rect.y += ai_settings.fleet_drop_speed
    ai_settings.fleet_direction *= -1


def ship_hit(ai_settings, stats, sb, screen, ship, aliens, bullets):
    """Обрабатывает столкновение корабля с пришельцем."""
    if stats.ships_left > 0:
        # Уменьшение ships_left.
        stats.ships_left -= 1
        # Обновление игровой информации.
        sb.prep_ships()
    else:
        stats.game_active = False
        pygame.mouse.set_visible(True)
    # Очистка списков пришельцев и пуль.
    aliens.empty()
    bullets.empty()
    # Создание нового флота и размещение корабля в центре.
    create_fleet(ai_settings, screen, ship, aliens)
    ship.center_ship()
    # Пауза.
    sleep(0.5)


def check_aliens_bottom(ai_settings, stats, sb, screen, ship, aliens, bullets):
    """Проверяет, добрались ли пришельцы до нижнего края экрана."""
    screen_rect = screen.get_rect()
    for alien in aliens.sprites():
        if alien.rect.bottom >= screen_rect.bottom:
            # Происходит то же, что при столкновении с кораблем.
            ship_hit(ai_settings, stats, sb, screen, ship, aliens, bullets)
            break


def check_high_score(stats, sb):
    """Проверяет, появился ли новый рекорд."""
    if stats.score > stats.high_score:
        stats.high_score = stats.score
        sb.prep_high_score()


def pornomod(ai_settings, ship):
    ship.image = pygame.image.load('images/ship2.png')
    ai_settings.bg_color = (237, 62, 62)

        #alien.image = pygame.image.load('images/alien2.png')

def normal(ai_settings, ship):
    ship.image = pygame.image.load('images/ship.png')
    ai_settings.bg_color = (0, 200, 230)