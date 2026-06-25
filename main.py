
import os
from modules.map_loader import load_map, list_maps
from modules.game import run_game


def show_menu() -> str:
    """Zobrazí hlavní menu a vrátí cestu k vybrané mapě.

    Returns:
        Cesta k .crmap souboru, nebo prázdný řetězec při ukončení.
    """
    os.system("cls" if os.name == "nt" else "clear")
    print("=" * 44)
    print("   🏎️  CarRace – Závod autíček v terminálu")
    print("=" * 44)

    maps_folder = os.path.join(os.path.dirname(__file__), "maps")
    available_maps = list_maps(maps_folder)

    if not available_maps:
        print("  ❌ Žádné mapy nenalezeny ve složce \'maps/\'")
        input("  Stiskni Enter pro ukončení...")
        return ""

    print("\n  Dostupné tratě:")
    for index, map_path in enumerate(available_maps, start=1):
        print(f"  [{index}] {os.path.basename(map_path)}")

    print("\n  [Q] Ukončit hru\n")

    while True:
        choice = input("  Vyber trať (číslo): ").strip().upper()
        if choice == "Q":
            return ""
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(available_maps):
                return available_maps[idx]
        print("  ⚠️  Neplatná volba, zkus to znovu.")


def main() -> None:
    """Hlavní funkce programu. Spustí menu a herní smyčku."""
    while True:
        selected_map_path = show_menu()

        if not selected_map_path:
            print("\n  Nashledanou! 👋\n")
            break

        map_data = load_map(selected_map_path)

        if map_data is None:
            print("  ❌ Mapu se nepodařilo načíst.")
            input("  Stiskni Enter pro návrat...")
            continue

        run_game(map_data)

        print("\n  Hrát znovu? [A / N]: ", end="")
        if input().strip().upper() != "A":
            print("\n  Nashledanou! 👋\n")
            break


if __name__ == "__main__":
    main()
