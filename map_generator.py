"""
Generátor mapových souborů formátu .crmap pro projekt CarRace.

Skript vytvoří .crmap soubor s klikatící se cestou zadané šířky.
Tvar cesty je generován kombinací sinusových vln pro přirozený vzhled zatáček.

Použití:
    python map_generator.py

Výstup:
    Soubor .crmap uložený do složky maps/

Example:
    Spuštění::

        $ python map_generator.py
"""

import math
import os


# ── Výchozí parametry generátoru ─────────────────────────────────────────────

# Celková šířka každého řádku mapy (musí souhlasit s width v [meta])
TRACK_WIDTH = 60

# Šířka průjezdné části cesty (mezery)
ROAD_WIDTH = 6

# Počet řádků trati (bez horní a dolní zdi)
TRACK_ROWS = 200

# Frekvence sinusových vln – ovlivňují tvar zatáček
# Vyšší číslo = ostřejší a rychlejší zatáčky
FREQ_1 = 1.5   # hlavní vlna
FREQ_2 = 1.1   # doplňková vlna (nepravidelnost)

# Amplituda každé vlny (0.5 + 0.5 = dohromady 1.0 = plný rozsah)
AMP_1 = 0.5
AMP_2 = 0.5

SPEED = 0.2  # výchozí délka tiku ve vteřinách (nižší = rychlejší)
BONUS_EVERY = 15  # každých N řádků se umístí bonus (*), 0 = žádné bonusy


def generate_road_centers(rows: int, track_width: int, road_width: int,
                           freq1: float, freq2: float,
                           amp1: float, amp2: float) -> list:
    """Vypočítá střed cesty pro každý řádek trati.

    Střed se pohybuje plynule pomocí kombinace dvou sinusových vln.
    Výsledná pozice je omezena tak, aby cesta nikdy nevyjela za okraje.

    Args:
        rows: Počet řádků trati.
        track_width: Celková šířka řádku (znaky).
        road_width: Šířka průjezdné části (znaky).
        freq1: Frekvence první sinusové vlny.
        freq2: Frekvence druhé sinusové vlny.
        amp1: Amplituda první vlny (součet amp1 + amp2 by měl být 1.0).
        amp2: Amplituda druhé vlny.

    Returns:
        Seznam celých čísel – index středu cesty pro každý řádek.
    """
    centers = []

    # Minimální a maximální možný střed cesty (s rezervou 2 znaků od okraje)
    min_center = road_width // 2 + 2
    max_center = track_width - road_width // 2 - 3

    for row in range(rows):
        # Parametr t jde od 0 do 2π přes celou délku trati
        t = (row / rows) * 2 * math.pi

        # Kombinace dvou sinů – výsledek je v rozsahu -1.0 až +1.0
        offset = math.sin(t * freq1) * amp1 + math.sin(t * freq2) * amp2

        # Mapujeme offset (-1..+1) na rozsah (min_center..max_center)
        center = int(min_center + (offset + 1) / 2 * (max_center - min_center))
        centers.append(center)

    return centers


def build_row(center: int, road_width: int, track_width: int,
              bonus_col: int = -1) -> str:
    """Sestaví jeden řádek trati jako řetězec délky track_width.

    Args:
        center: Index středu průjezdné části.
        road_width: Šířka průjezdné části (znaky).
        track_width: Celková šířka řádku.
        bonus_col: Index sloupce s bonusem (*). Hodnota -1 = žádný bonus.

    Returns:
        Řetězec délky track_width složený ze znaků '#', ' ' a případně '*'.

    Example:
        >>> build_row(center=20, road_width=6, track_width=40)
        '##################      ##################'
    """
    road_start = center - road_width // 2
    road_end   = road_start + road_width

    row_chars = []
    for col in range(track_width):
        if road_start <= col < road_end:
            # Průjezdná část – bonus nebo mezera
            if col == bonus_col:
                row_chars.append("*")
            else:
                row_chars.append(" ")
        else:
            row_chars.append("#")

    return "".join(row_chars)


def generate_track_lines(rows: int, track_width: int, road_width: int,
                          freq1: float, freq2: float,
                          amp1: float, amp2: float,
                          bonus_every: int = 0) -> list:
    """Vygeneruje všechny řádky trati včetně horní a dolní zdi.

    Args:
        rows: Počet řádků trati (bez krajních zdí).
        track_width: Celková šířka každého řádku.
        road_width: Šířka průjezdné části.
        freq1: Frekvence první sinusové vlny zatáček.
        freq2: Frekvence druhé sinusové vlny zatáček.
        amp1: Amplituda první vlny.
        amp2: Amplituda druhé vlny.
        bonus_every: Každých N řádků se uprostřed cesty umístí bonus (*).
                     Hodnota 0 = žádné bonusy.

    Returns:
        Seznam řetězců – řádky trati včetně horní a dolní zdi.
    """
    centers = generate_road_centers(rows, track_width, road_width,
                                    freq1, freq2, amp1, amp2)

    track_lines = []
    track_lines.append("#" * track_width)   # horní zeď

    for row_idx, center in enumerate(centers):
        # Umístění bonusu doprostřed cesty každých bonus_every řádků
        bonus_col = -1
        if bonus_every > 0 and row_idx % bonus_every == 0:
            bonus_col = center   # střed průjezdné části

        line = build_row(center, road_width, track_width, bonus_col)
        track_lines.append(line)

    track_lines.append("#" * track_width)   # dolní zeď
    return track_lines


def build_crmap_content(name: str, author: str, track_width: int,
                         speed: float, lives: int, description: str,
                         track_lines: list) -> str:
    """Sestaví celý obsah .crmap souboru jako řetězec.

    Args:
        name: Název trati (zobrazí se v menu).
        author: Autor mapy.
        track_width: Šířka řádku – musí souhlasit s délkou řádků track_lines.
        speed: Výchozí délka tiku ve vteřinách (nižší = rychlejší).
        lives: Počet životů hráče.
        description: Krátký popis trati.
        track_lines: Seznam řádků trati (výstup generate_track_lines).

    Returns:
        Řetězec – kompletní obsah .crmap souboru připravený k zápisu.
    """
    meta_section = (
        "# ============================================================\n"
        "# CarRace Map File (.crmap)\n"
        "# ============================================================\n"
        "\n"
        "[meta]\n"
        f"name={name}\n"
        f"author={author}\n"
        f"width={track_width}\n"
        f"speed={speed}\n"
        f"lives={lives}\n"
        f"description={description}\n"
        "\n"
        "[track]\n"
    )
    track_section = "\n".join(track_lines) + "\n"
    return meta_section + track_section


def save_crmap(content: str, filepath: str) -> None:
    """Uloží obsah mapy do souboru .crmap.

    Vytvoří cílovou složku, pokud neexistuje.

    Args:
        content: Kompletní obsah souboru jako řetězec.
        filepath: Cesta k výstupnímu souboru.
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"  ✅ Uloženo: {filepath}")


def validate_track(track_lines: list, expected_width: int) -> bool:
    """Ověří, že všechny řádky trati mají správnou délku.

    Args:
        track_lines: Seznam řádků trati.
        expected_width: Očekávaná délka každého řádku.

    Returns:
        True pokud jsou všechny řádky správně dlouhé, jinak False.
    """
    errors = [
        (i, len(line))
        for i, line in enumerate(track_lines)
        if len(line) != expected_width
    ]
    if errors:
        for row_idx, length in errors:
            print(f"  ❌ Chyba: řádek {row_idx} má délku {length}, očekáváno {expected_width}")
        return False

    print(f"  ✅ Validace OK – všech {len(track_lines)} řádků má délku {expected_width}")
    return True


# ── Hlavní část – generování map ──────────────────────────────────────────────

if __name__ == "__main__":

    base_dir = os.path.join(os.path.dirname(__file__), "maps")

    print("🗺️  CarRace – Generátor map\n")

    print("Generuji: track_06.crmap")
    lines_medium = generate_track_lines(
        rows=TRACK_ROWS,
        track_width=TRACK_WIDTH,
        road_width=ROAD_WIDTH,
        freq1=FREQ_1,
        freq2=FREQ_2,
        amp1=AMP_1,
        amp2=AMP_2,
        bonus_every=BONUS_EVERY # bonus každých 15 řádků
    )
    validate_track(lines_medium, TRACK_WIDTH)
    content_medium = build_crmap_content(
        name="Klikatá horská cesta – Střední",
        author="Masarykovo gymnázium Vsetín",
        track_width=TRACK_WIDTH,
        speed=SPEED,
        lives=3,
        description="Cesta šířky 6, plynulé zatáčky. Drž se v pruhu!",
        track_lines=lines_medium,
    )
    save_crmap(content_medium, os.path.join(base_dir, "track_03_medium.crmap"))

    # ── Mapa 2: Těžká obtížnost, cesta šířky 4, ostřejší zatáčky ─────────────
    print("\nGeneruji: track_04_hard.crmap")
    lines_hard = generate_track_lines(
        rows=TRACK_ROWS,
        track_width=TRACK_WIDTH,
        road_width=ROAD_WIDTH - 2,  # užší cesta
        freq1=FREQ_1,   # ostřejší zatáčky
        freq2=FREQ_2,
        amp1=AMP_1,
        amp2=AMP_2,
        bonus_every=BONUS_EVERY,
    )
    validate_track(lines_hard, TRACK_WIDTH)
    content_hard = build_crmap_content(
        name="Horská rokle – Těžká",
        author="Masarykovo gymnázium Vsetín",
        track_width=TRACK_WIDTH,
        speed=SPEED,
        lives=3,
        description="Úzká cesta šířky 4, ostré zatáčky. Pro zkušené závodníky!",
        track_lines=lines_hard,
    )
    save_crmap(content_hard, os.path.join(base_dir, "track_04_hard.crmap"))

    print("\n  Hotovo! Mapy jsou uloženy ve složce maps/")