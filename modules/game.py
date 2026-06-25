"""
Modul s herní logikou projektu CarRace.

Obsahuje funkce pro pohyb autíčka, detekci kolizí, výpočet rychlosti
a hlavní herní smyčku.

Example:
    Použití::

        from modules.game import run_game
        from modules.map_loader import load_map

        map_data = load_map("maps/track_01.crmap")
        run_game(map_data)
"""

import time
from modules.render import draw_frame, draw_game_over, draw_pause
from modules.input_handler import get_pressed_keys

# ── Herní konstanty ───────────────────────────────────────────────────────────
VIEWPORT_HEIGHT  = 10    # počet viditelných řádků trati nad autíčkem
SCORE_PER_ROW    = 10    # body za každý projety řádek
SCORE_BONUS      = 100   # body za sebrání bonusu (*)
SPEED_UP_EVERY   = 300   # každých N bodů se zvýší úroveň rychlosti
MAX_SPEED_LEVEL  = 10    # maximální úroveň rychlosti

OBSTACLE_CHAR = "X"
BONUS_CHAR    = "*"
WALL_CHAR     = "#"


def create_car_state(start_x: int, lives: int) -> dict:
    """Vytvoří výchozí stav autíčka jako slovník.

    Args:
        start_x: Výchozí horizontální pozice (index levého okraje symbolu).
        lives: Počet životů na začátku.

    Returns:
        Slovník se stavem: x, lives, score, invincible_ticks.
    """
    return {
        "x": start_x,
        "lives": lives,
        "score": 0,
        "invincible_ticks": 0,  # dočasná nezranitelnost po kolizi
    }


def move_car(car_x: int, direction: str, track_width: int) -> int:
    """Posune autíčko o jeden krok doleva nebo doprava.

    Hlídá okraje trati – autíčko nemůže vyjet za zeď.
    Symbol [>] má šířku 3 znaky.

    Args:
        car_x: Aktuální horizontální pozice levého okraje autíčka.
        direction: Směr pohybu – 'left' nebo 'right'.
        track_width: Celková šířka řádku trati (včetně zdí #).

    Returns:
        Nová horizontální pozice autíčka.

    Example:
        >>> move_car(5, "left", 40)
        4
        >>> move_car(1, "left", 40)
        1
    """
    car_symbol_width = 3
    if direction == "left":
        return max(car_x - 1, 1)                               # 1 = za levou zdí
    if direction == "right":
        return min(car_x + 1, track_width - car_symbol_width - 1)
    return car_x


def get_track_window(track_lines: list, scroll_pos: int, window_height: int) -> list:
    """Vrátí výřez trati pro aktuální pozici scrollu.

    Překážky přijíždějí shora – scroll_pos klesá, viewport zobrazuje
    řádky od scroll_pos dolů. Chrání před záporným indexem i přetečením.

    Args:
        track_lines: Všechny řádky načtené trati.
        scroll_pos: Index prvního (horního) viditelného řádku.
        window_height: Výška viewportu – počet zobrazených řádků.

    Returns:
        Seznam window_height řetězců reprezentujících viditelnou část trati.
    """
    total = len(track_lines)
    window = []
    for offset in range(window_height):
        idx = scroll_pos + offset
        idx = max(0, min(idx, total - 1))   # ochrana před přetečením
        window.append(track_lines[idx])
    return window


def check_collision(track_row: str, car_x: int) -> str:
    """Zjistí, s čím se autíčko střetlo na daném řádku.

    Kontroluje tři znaky odpovídající šířce symbolu [>].

    Args:
        track_row: Řetězec jednoho řádku trati.
        car_x: Horizontální pozice levého okraje autíčka.

    Returns:
        Jeden z řetězců: 'wall', 'obstacle', 'bonus', 'clear'.

    Example:
        >>> check_collision("#  XX  #", 3)
        'obstacle'
        >>> check_collision("#      #", 3)
        'clear'
    """
    for offset in range(3):   # šířka [>] = 3 znaky
        idx = car_x + offset
        if 0 <= idx < len(track_row):
            ch = track_row[idx]
            if ch == WALL_CHAR:
                return "wall"
            if ch == OBSTACLE_CHAR:
                return "obstacle"
            if ch == BONUS_CHAR:
                return "bonus"
    return "clear"


def update_speed(base_speed: float, score: int) -> tuple:
    """Vypočítá aktuální rychlost hry podle skóre.

    Každých SPEED_UP_EVERY bodů se zkrátí sleep o 10 %.
    Minimální hodnota je 0.02 s.

    Args:
        base_speed: Výchozí délka tiku ve vteřinách (z metadat mapy).
        score: Aktuální skóre hráče.

    Returns:
        Dvojice (current_speed, speed_level).

    Example:
        >>> update_speed(0.09, 0)
        (0.09, 0)
        >>> update_speed(0.09, 300)
        (0.081, 1)
    """
    level = min(score // SPEED_UP_EVERY, MAX_SPEED_LEVEL)
    speed = max(base_speed * (0.9 ** level), 0.02)
    return speed, level


def run_game(map_data: dict) -> None:
    """Hlavní herní smyčka pro jednoho hráče.

    Mapa se scrolluje NAHORU – scroll_pos začíná na konci mapy a klesá.
    Překážky přijíždějí shora dolů směrem k autíčku, které stojí dole.

    Každý tik:
    1. přečte stisknuté klávesy
    2. posune autíčko (doleva / doprava)
    3. sníží scroll_pos o 1 (mapa jede nahoru)
    4. zkontroluje kolize na řádku těsně nad autem
    5. aktualizuje skóre a rychlost
    6. vykreslí snímek

    Hra končí po ztrátě všech životů nebo projetí celé trati.

    Args:
        map_data: Slovník vrácený load_map() s klíči 'meta' a 'track'.
    """
    meta        = map_data["meta"]
    track_lines = map_data["track"]
    track_width = meta["width"]
    base_speed  = meta["speed"]
    max_lives   = meta["lives"]

    start_x    = track_width // 2 - 1
    car        = create_car_state(start_x, max_lives)
    total_rows = len(track_lines)

    # OPRAVA: začínáme na KONCI mapy, scroll_pos bude klesat → mapa jede nahoru
    scroll_pos = total_rows - VIEWPORT_HEIGHT - 1

    running   = True
    paused    = False
    message   = ""
    msg_ticks = 0

    while running:
        # ── Vstup ────────────────────────────────────────────────────────────
        pressed = get_pressed_keys()

        if "pause" in pressed:
            paused = not paused
            time.sleep(0.2)   # debounce – zamezí rychlému přepínání
            if paused:
                draw_pause()
            continue

        if paused:
            time.sleep(0.1)
            continue

        if "quit" in pressed:
            break

        if "left" in pressed:
            car["x"] = move_car(car["x"], "left", track_width)
        if "right" in pressed:
            car["x"] = move_car(car["x"], "right", track_width)

        # ── Scroll mapy nahoru ────────────────────────────────────────────────
        # OPRAVA: scroll_pos klesá → překážky přijíždějí shora
        scroll_pos -= 1

        # ── Konec trati ───────────────────────────────────────────────────────
        if scroll_pos <= 0:
            car["score"] += SCORE_PER_ROW * 5   # bonus za dokončení
            draw_frame(
                get_track_window(track_lines, 0, VIEWPORT_HEIGHT),
                car["x"], car["lives"], car["score"],
                max_lives=max_lives,
                message="🎉 Projel jsi celou trať! Gratulujeme!"
            )
            time.sleep(2)
            break

        # ── Rychlost ──────────────────────────────────────────────────────────
        current_speed, speed_level = update_speed(base_speed, car["score"])

        # ── Skóre za projety řádek ────────────────────────────────────────────
        car["score"] += SCORE_PER_ROW

        # ── Kontrola kolize ───────────────────────────────────────────────────
        # Kolize kontrolujeme na POSLEDNÍM řádku viewportu – těsně nad autem
        coll_idx  = max(0, min(scroll_pos + VIEWPORT_HEIGHT - 1, total_rows - 1))
        coll_row  = track_lines[coll_idx]
        coll_type = check_collision(coll_row, car["x"])

        if car["invincible_ticks"] > 0:
            car["invincible_ticks"] -= 1
        elif coll_type in ("obstacle", "wall"):
            car["lives"] -= 1
            car["invincible_ticks"] = 10   # 10 tiků nezranitelnosti po nárazu
            message   = f"💥 Rána! Zbývají životy: {car['lives']}"
            msg_ticks = 4
            if car["lives"] <= 0:
                running = False
        elif coll_type == "bonus":
            car["score"] += SCORE_BONUS
            message   = f"⭐ Bonus! +{SCORE_BONUS} bodů!"
            msg_ticks = 4

        # Zpráva zmizí po msg_ticks ticích
        if msg_ticks > 0:
            msg_ticks -= 1
        else:
            message = ""

        # ── Vykreslení snímku ─────────────────────────────────────────────────
        window = get_track_window(track_lines, scroll_pos, VIEWPORT_HEIGHT)
        draw_frame(
            track_window=window,
            car_x=car["x"],
            lives=car["lives"],
            score=car["score"],
            speed_level=speed_level,
            max_lives=max_lives,
            message=message,
        )

        time.sleep(current_speed)

    # ── Konec hry ─────────────────────────────────────────────────────────────
    reason = "Utratil jsi všechny životy. 😢" if car["lives"] <= 0 else ""
    draw_game_over(score=car["score"], reason=reason)
    input()