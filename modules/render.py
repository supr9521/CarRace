import os

CAR_SYMBOL   = "[>]"    # vizuální reprezentace autíčka (3 znaky)
CAR_WIDTH    = len(CAR_SYMBOL)
LIVES_FULL   = "❤️ "
LIVES_EMPTY  = "🖤 "
BAR_FULL     = "█"
BAR_EMPTY    = "░"
BAR_WIDTH    = 20
MAX_SPEED_LEVEL = 10


def clear_screen() -> None:
    """Smaže obsah terminálu.

    Použije cls na Windows nebo clear na Linuxu / Macu.
    """
    os.system("cls" if os.name == "nt" else "clear")


def _lives_str(lives: int, max_lives: int) -> str:
    """Sestaví řetězec se symboly životů.

    Args:
        lives: Počet zbývajících životů.
        max_lives: Maximální počet životů.

    Returns:
        Řetězec, např. \'❤️  ❤️  🖤 \' pro lives=2, max_lives=3.
    """
    return LIVES_FULL * max(lives, 0) + LIVES_EMPTY * max(max_lives - lives, 0)


def _speed_bar(speed_level: int) -> str:
    """Sestaví progress bar rychlosti.

    Args:
        speed_level: Aktuální úroveň (0 – MAX_SPEED_LEVEL).

    Returns:
        Řetězec, např. \'████░░░░░░░░░░░░░░░░ 2x\'.
    """
    filled = int((speed_level / MAX_SPEED_LEVEL) * BAR_WIDTH)
    bar = BAR_FULL * filled + BAR_EMPTY * (BAR_WIDTH - filled)
    return f"{bar} {speed_level + 1}x"


def draw_frame(
    track_window: list,
    car_x: int,
    lives: int,
    score: int,
    speed_level: int = 0,
    max_lives: int = 3,
    message: str = "",
) -> None:
    """Vykreslí celý herní snímek do terminálu.

    Args:
        track_window: Viditelné řádky trati (list řetězců).
        car_x: Horizontální pozice levého okraje autíčka.
        lives: Zbývající životy hráče.
        score: Aktuální skóre.
        speed_level: Úroveň rychlosti pro progress bar.
        max_lives: Maximální počet životů.
        message: Volitelná zpráva pod herním polem.
    """
    clear_screen()

    track_width = len(track_window[0]) if track_window else 40

    print("╔" + "═" * track_width + "╗")
    for row in track_window:
        print("║" + row + "║")

    # Řádek s autíčkem
    car_row = list(" " * track_width)
    for offset, ch in enumerate(CAR_SYMBOL):
        idx = car_x + offset
        if 0 <= idx < track_width:
            car_row[idx] = ch
    print("║" + "".join(car_row) + "║")

    print("╚" + "═" * track_width + "╝")

    # Stavový řádek
    print(f"  {_lives_str(lives, max_lives)}  Skóre: {score:<6}  Rychlost: {_speed_bar(speed_level)}")

    if message:
        print(f"\n  ✨ {message}")

    print()
    print("  Ovládání: A / ←  doprava  D / →  |  P pauza  |  Q konec")


def draw_game_over(score: int, reason: str = "") -> None:
    """Vykreslí obrazovku konce hry.

    Args:
        score: Dosažené skóre.
        reason: Popis důvodu konce hry.
    """
    clear_screen()
    print()
    print("  ╔══════════════════════════════╗")
    print("  ║        💥 KONEC HRY 💥        ║")
    print("  ╚══════════════════════════════╝")
    if reason:
        print(f"\n  {reason}")
    print(f"\n  Tvoje skóre: {score}")
    print("\n  Stiskni Enter pro návrat do menu...")


def draw_pause() -> None:
    """Vykreslí oznámení o pauze."""
    print()
    print("  ⏸️  HRA POZASTAVENA – stiskni P pro pokračování")