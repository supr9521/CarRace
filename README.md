# 🏎️ CarRace – Závod autíček v terminálu

> **Školní projekt – Python | Funkcionální přístup (bez OOP)**  
> Masarykovo gymnázium Vsetín | Předmět: Programování v Pythonu

---

## 📋 Popis projektu

Naprogramuj terminálovou hru **CarRace** – závod autíčka po trase načtené z externího souboru.  
Hra je ovládána klávesnicí v reálném čase. Autíčko jede stále dopředu a hráč musí uhýbat překážkám.  
Čím déle přežije, tím více bodů získá – a s časem se hra zrychluje.

Celý projekt musí být napsán **pomocí funkcí** (bez tříd a OOP).  
Kód musí obsahovat **docstringy v Google formátu** a **komentáře** (oboje česky).  
Proměnné, funkce a parametry pojmenovávej **anglicky**, výstup pro uživatele **česky**.

---

## 🎯 Herní koncepty – vyber si!

| Varianta | Popis | Obtížnost |
|---|---|---|
| **A – Jeden hráč** | Autíčko jede samo, hráč uhýbá překážkám, hra se zrychluje | ⭐⭐ |
| **B – Dva hráči** | Dva hráči závodí na rozdělené obrazovce | ⭐⭐⭐ |

> 💡 Doporučujeme začít variantou A. Varianta B je rozšíření pro pokročilé.

---

## 🗂️ Struktura projektu

```
CarRace/
├── main.py               ← Spouštěcí soubor, menu, herní smyčka
├── modules/
│   ├── game.py           ← Logika: pohyb, kolize, skóre, run_game()
│   ├── render.py         ← Vykreslování: draw_frame(), status bar
│   ├── input_handler.py  ← Klávesnice: keyboard lib nebo msvcrt fallback
│   └── map_loader.py     ← Parser .crmap souborů
├── maps/
│   └── track_01.crmap    ← Ukázková mapa (Vsetín – Začátečník)
└── README.md
```

---

## 🗺️ Formát mapového souboru `.crmap`

Soubor `.crmap` je prostý textový soubor otevřitelný v libovolném editoru.

### Struktura:

```
# Komentáře začínají # s mezerou
[meta]
name=Název tratě
author=Autor
width=40
speed=0.09
lives=3

[track]
########################################
#  . . . . . . . . . . . . . . . . .  #
#  . . . .  X  . . . . . . . . . . .  #
#  . . . . . . . *  . . . . . . . . .  #
########################################
```

### Legenda symbolů:

| Symbol | Význam |
|---|---|
| `#` | Zeď / okraj trati |
| ` ` (mezera) | Volná plocha – průjezdné |
| `.` | Asfalt / dekorace – průjezdné |
| `X` | **Překážka** – kolize = ztráta života |
| `*` | **Bonus** – sebrání = extra body |

### Pravidla:
- Každý řádek `[track]` musí mít délku přesně `width` znaků
- Levý a pravý okraj jsou vždy `#`
- Mapa může mít libovolný počet řádků – tvoří „scrollující" trať
- Hra zobrazuje jen okno (viewport) a posunuje mapu směrem nahoru

---

## 🚦 Varianta A – Jeden hráč (povinná, Fáze 1)

### Mechanika:
- Autíčko stojí na pevné pozici (dolní část obrazovky)
- Mapa se **scrolluje zdola nahoru** – auto „jede"
- Hráč ovládá pohyb **doleva / doprava**
- Narazíš-li na `X` nebo `#` → ztráta života
- S rostoucím skóre se hra **zrychluje**
- Hra končí po ztrátě všech životů nebo projetí celé trati

### Ovládání:

| Klávesa | Akce |
|---|---|
| `A` nebo `←` | Pohyb doleva |
| `D` nebo `→` | Pohyb doprava |
| `P` | Pauza / pokračování |
| `Q` | Ukončit hru |

### Povinné funkce:

```python
def load_map(filepath: str) -> dict: ...
def draw_frame(track_window, car_x, lives, score, speed_level, max_lives, message) -> None: ...
def move_car(car_x: int, direction: str, track_width: int) -> int: ...
def check_collision(track_row: str, car_x: int) -> str: ...
def get_track_window(track_lines: list, scroll_pos: int, window_height: int) -> list: ...
def update_speed(base_speed: float, score: int) -> tuple: ...
def run_game(map_data: dict) -> None: ...
```

### Ukázka výstupu:

```
╔════════════════════════════════════════╗
║  . . . XX . . . . . . . . . . . . .   ║
║  . . .  . . . XX . . . . . . . . .    ║
║  . . . . .  . . . . . . . . . . .     ║
║     . . . . . . . . . . . . . . .     ║
║          [>]                          ║
╚════════════════════════════════════════╝
  ❤️  ❤️  ❤️   Skóre: 1250    Rychlost: ████░░░░░░ 2x
```

---

## 🏁 Varianta B – Dva hráči (pro pokročilé, Fáze 2)

> ⚠️ Vyžaduje **souběžné čtení dvou kláves** a **rozdělenou obrazovku**.

### Mechanika:
- Obrazovka rozdělena na **dvě poloviny** (Hráč 1 vlevo, Hráč 2 vpravo)
- Oba jedou po **stejné trati** nezávisle
- Kdo přežije déle nebo projede trať rychleji, vyhraje

### Klávesy:

| Akce | Hráč 1 | Hráč 2 |
|---|---|---|
| Vlevo | `A` | `←` |
| Vpravo | `D` | `→` |

### Technická poznámka:

```python
import keyboard

# Neblokující – ptáme se, zda je klávesa stisknuta právě TEĎ
if keyboard.is_pressed("a"):
    car1_x = move_car(car1_x, "left", track_width)
if keyboard.is_pressed("left"):
    car2_x = move_car(car2_x, "left", track_width)
```

> ⚠️ Na Windows nutno spustit terminál jako **správce**.

### Funkce navíc:

```python
def draw_split_screen(window1, car1_x, lives1, window2, car2_x, lives2) -> None: ...
def run_two_player_game(map_data: dict) -> None: ...
```

---

## 🔧 Fáze 2 – Rozšíření (vyber alespoň 2)

| Rozšíření | Popis |
|---|---|
| **2a) Více map** | Menu pro výběr tratě ze složky `maps/`, různé obtížnosti |
| **2b) Highscore** | Uložení jména a skóre do `highscore.txt`, TOP 5 při startu |
| **2c) Bonusy na trati** | Symbol `*` přidá body nebo životy |
| **2d) Intro animace** | ASCII art s názvem hry a animovaným uvítáním |
| **2e) Editor map** | Jednoduchý terminálový nástroj pro tvorbu `.crmap` souborů |

---

## 🌟 Fáze 3 – Bonusy (pro nadšence)

- **Barvy**: `colorama` – obarvení autíčka, překážek, bonusů
- **Zvuky**: `winsound.Beep()` při kolizi nebo bonusu
- **Procedurální generátor**: Náhodně vygeneruj `.crmap` se zadanou obtížností
- **Replay**: Ulož každý tah a přehraj závod po skončení

---

## 📦 Instalace závislostí

```bash
pip install keyboard      # čtení kláves (multiplatformní)
pip install colorama      # barvy v terminálu (Fáze 3)
```

> 💡 **Alternativa bez instalace (Windows)**: Projekt automaticky použije `msvcrt`
> pokud `keyboard` není k dispozici.

---

## 🏗️ Doporučený postup

1. Nastav projekt – složka, soubory, virtuální prostředí
2. Načti mapu – `map_loader.py`, ověř výstup pomocí `print()`
3. Vykresli trať – funkce `draw_frame()` s pevným výřezem
4. Rozhýbej trať – `get_track_window()` + scroll
5. Přidej autíčko – vykreslení, ovládání
6. Přidej kolize – `check_collision()`, životy
7. Herní smyčka – `run_game()`, skóre, zrychlení
8. Refaktoring – docstringy, komentáře, čistý kód
9. Fáze 2 – rozšíření

---

## 📝 Požadavky na kód

- Každá funkce musí mít **docstring v Google formátu** (česky)
- Proměnné, funkce, parametry – **anglicky**
- Výstup pro uživatele – **česky**
- Žádné globální proměnné pro stav hry – stav předávej jako **parametry**
- `main.py` musí mít `if __name__ == "__main__":`

### Vzor dokumentované funkce:

```python
def update_speed(base_speed: float, score: int) -> tuple:
    \"\"\"Vypočítá aktuální rychlost hry podle skóre.

    Každých 300 bodů se zkrátí sleep o 10 %. Min. hodnota je 0.02 s.

    Args:
        base_speed: Výchozí délka tiku ve vteřinách (z metadat mapy).
        score: Aktuální skóre hráče.

    Returns:
        Dvojice (current_speed, speed_level).

    Example:
        >>> update_speed(0.09, 300)
        (0.081, 1)
    \"\"\"
    level = min(score // 300, 10)
    speed = max(base_speed * (0.9 ** level), 0.02)
    return speed, level
```

---

## 📊 Hodnocení

| Kritérium | Body |
|---|---|
| Varianta A – funkční hra s načítáním mapy | 35 b. |
| Správná struktura souborů a funkcí | 15 b. |
| Docstringy a komentáře (Google formát) | 15 b. |
| Fáze 2 – min. 2 rozšíření | 20 b. |
| Varianta B nebo další rozšíření | 15 b. |
| Fáze 3 – bonusy | až +10 b. |
| **Celkem** | **100 b.** |

---

## 📅 Termíny

| Fáze | Termín |
|---|---|
| Fáze 1 (Varianta A) | 2 týdny od zadání |
| Fáze 2 nebo Varianta B | 4 týdny od zadání |
| Fáze 3 | 5 týdnů od zadání |

---

## 💡 Tipy

- **Mazání obrazovky**: `os.system("cls")` (Win) / `os.system("clear")` (Linux/Mac)
- **Stav autíčka**: Slovník `{"x": 5, "lives": 3, "score": 0, "invincible_ticks": 0}`
- **Scroll**: Proměnná `scroll_pos` = index prvního viditelného řádku mapy
- **Plynulost**: Začni s `time.sleep(0.08)`, pak přidej zrychlení
- **Testuj po částech**: Každá funkce zvlášť s `print()`, pak teprve smyčka