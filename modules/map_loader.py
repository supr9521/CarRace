import os
from typing import Optional


def list_maps(folder: str) -> list:
    """Vrátí seřazený seznam cest ke všem .crmap souborům ve složce.

    Args:
        folder: Cesta ke složce s mapami.

    Returns:
        Seřazený seznam absolutních cest. Prázdný seznam, pokud složka neexistuje.
    """
    if not os.path.isdir(folder):
        return []
    return [
        os.path.join(folder, f)
        for f in sorted(os.listdir(folder))
        if f.endswith(".crmap")
    ]


def _parse_meta(lines: list) -> dict:
    """Parsuje sekci [meta] a vrátí slovník s metadaty mapy.

    Args:
        lines: Řádky sekce [meta] (bez hlavičky).

    Returns:
        Slovník s klíči name, author, width, speed, lives, description.
    """
    meta = {
        "name": "Neznámá mapa",
        "author": "Neznámý",
        "width": 40,
        "speed": 0.08,
        "lives": 3,
        "description": "",
    }
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" in line:
            key, _, value = line.partition("=")
            key, value = key.strip(), value.strip()
            if key == "width":
                meta["width"] = int(value)
            elif key == "speed":
                meta["speed"] = float(value)
            elif key == "lives":
                meta["lives"] = int(value)
            else:
                meta[key] = value
    return meta


def _parse_track(lines: list) -> list:
    """Parsuje sekci [track] a vrátí seznam řádků trati.

    Args:
        lines: Řádky sekce [track] (bez hlavičky [track]).

    Returns:
        Seznam řetězců – řádky trati. Prázdné řádky a čisté komentáře jsou vynechány.
    """
    track_lines = []
    for line in lines:
        stripped = line.rstrip("\n")

        # Přeskočíme POUZE čistě prázdné řádky
        if stripped.strip() == "":
            continue

        # Přeskočíme POUZE řádky, které jsou CELÉ komentář:
        # tj. začínají "# " A neobsahují znaky trati (X, *, .)
        # Řádky trati jako "#  . . . X . . .  #" NESMÍME zahazovat!
        if stripped.strip().startswith("# ") and "#" not in stripped.strip()[2:]:
            continue

        track_lines.append(stripped)
    return track_lines


def load_map(filepath: str) -> Optional[dict]:
    """Načte a parsuje mapový soubor formátu .crmap.

    Args:
        filepath: Cesta k .crmap souboru.

    Returns:
        Slovník s klíči \'meta\' (dict) a \'track\' (list řádků),
        nebo None při chybě.

    Example:
        >>> data = load_map("maps/track_01.crmap")
        >>> print(data["meta"]["name"])
        Závodní okruh Vsetín – Začátečník
    """
    if not os.path.isfile(filepath):
        print(f"  ❌ Soubor nenalezen: {filepath}")
        return None

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.readlines()
    except OSError as err:
        print(f"  ❌ Chyba při čtení: {err}")
        return None

    meta_lines, track_lines = [], []
    current_section = None

    for line in content:
        s = line.strip()
        if s == "[meta]":
            current_section = "meta"
        elif s == "[track]":
            current_section = "track"
        elif current_section == "meta":
            meta_lines.append(line)
        elif current_section == "track":
            track_lines.append(line)

    meta = _parse_meta(meta_lines)
    track = _parse_track(track_lines)

    if not track:
        print("  ❌ Sekce [track] je prázdná nebo chybí.")
        return None

    return {"meta": meta, "track": track}
