import os
import keyboard as _kb

# ── Detekce dostupné knihovny ─────────────────────────────────────────────────
_USE_KEYBOARD_LIB = False
try:
    import keyboard as _kb
    _USE_KEYBOARD_LIB = True
except ImportError:
    pass

# Mapování logických akcí na fyzické klávesy (keyboard lib)
_KEY_MAP = {
    "left":  ["left", "a"],
    "right": ["right", "d"],
    "pause": ["p"],
    "quit":  ["q"],
}

# Mapování bajt → akce pro msvcrt (šipky se skládají ze dvou bajtů)
_MSVCRT_MAP = {
    b"a": "left",  b"A": "left",
    b"d": "right", b"D": "right",
    b"K": "left",  # druhý bajt šipky doleva (po prefixu \\xe0)
    b"M": "right", # druhý bajt šipky doprava
    b"p": "pause", b"P": "pause",
    b"q": "quit",  b"Q": "quit",
}


def get_pressed_keys() -> set:
    """Vrátí množinu aktuálně stisknutých logických kláves.

    Funkce je neblokující – vrátí výsledek okamžitě.

    Returns:
        Množina řetězců z hodnot: \'left\', \'right\', \'pause\', \'quit\'.
        Prázdná množina, pokud není nic stisknuto.
    """
    if _USE_KEYBOARD_LIB:
        return _read_keyboard_lib()
    return _read_msvcrt()


def _read_keyboard_lib() -> set:
    """Přečte stisknuté klávesy pomocí knihovny keyboard.

    Returns:
        Množina logických akcí.
    """
    pressed = set()
    for action, keys in _KEY_MAP.items():
        if any(_kb.is_pressed(k) for k in keys):
            pressed.add(action)
    return pressed


def _read_msvcrt() -> set:
    """Přečte jednu stisknutou klávesu pomocí msvcrt (Windows only).

    Returns:
        Jednoprvková množina s akcí, nebo prázdná množina.
    """
    try:
        import msvcrt
        if msvcrt.kbhit():
            key = msvcrt.getch()
            if key in (b"\\xe0", b"\\x00"):
                key = msvcrt.getch()  # druhý bajt speciální klávesy
            action = _MSVCRT_MAP.get(key)
            if action:
                return {action}
    except ImportError:
        pass
    return set()


def input_method_info() -> str:
    """Vrátí název aktivní metody čtení kláves.

    Returns:
        Popis aktivní metody jako řetězec.
    """
    if _USE_KEYBOARD_LIB:
        return "keyboard (pip)"
    if os.name == "nt":
        return "msvcrt (Windows built-in)"
    return "žádná – spusť: pip install keyboard"
