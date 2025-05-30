#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import glob
import pandas as pd
import fitz  # PyMuPDF

# ---------- KONFIGURACJA DOMYŚLNA I MENU -----------------------------------

USTAWIENIA_FILE = "ustawienia.txt"
DOMYSLNE = {
    "FONT_SIZE": 14,
    "OFFSET_X": 50,
    "OFFSET_Y": 50,
    "EXCEL_FILE": "nazwa_pliku.xlsx"
}

SEP = ', '
RYSUNKI_DIR = 'Rysunki'
MISSING_FILE = 'brak_rysunku_pdf.txt'


def zapisz_ustawienia(ust):
    with open(USTAWIENIA_FILE, "w", encoding="utf-8") as f:
        for k, v in ust.items():
            f.write(f"{k}={v}\n")


def wczytaj_ustawienia():
    if not os.path.exists(USTAWIENIA_FILE):
        zapisz_ustawienia(DOMYSLNE)
        return DOMYSLNE.copy()
    ust = {}
    with open(USTAWIENIA_FILE, "r", encoding="utf-8") as f:
        for linia in f:
            if "=" in linia:
                k, v = linia.strip().split("=")
                ust[k] = int(v) if k.startswith("OFFSET") or k == "FONT_SIZE" else v
    return ust


def menu_startowe(ust):
    print("=== MENU KONFIGURACJI ===")
    try:
        ust["FONT_SIZE"] = int(input(f"Wielkość czcionki [{ust['FONT_SIZE']}]: ") or ust["FONT_SIZE"])
        ust["OFFSET_X"] = int(input(f"Przesunięcie X [{ust['OFFSET_X']}]: ") or ust["OFFSET_X"])
        ust["OFFSET_Y"] = int(input(f"Przesunięcie Y [{ust['OFFSET_Y']}]: ") or ust["OFFSET_Y"])
        ust["EXCEL_FILE"] = input(f"Nazwa pliku Excel [{ust['EXCEL_FILE']}]: ") or ust["EXCEL_FILE"]
    except ValueError:
        print("⚠️  Błąd wartości, pozostają ustawienia domyślne lub wcześniejsze.")
    zapisz_ustawienia(ust)
    return ust


# ---------- FUNKCJE --------------------------------------------------------

def build_line(row: pd.Series, skip: str = 'Rysunek') -> str:
    """Buduje pojedynczą linię tekstu z wartości kolumn ≠ skip."""
    result = []
    for k, v in row.items():
        if k == skip or k.lower() == 'korekta' or pd.isna(v):
            continue
        val = str(v).strip()
        key = k.lower().strip()

        if key in ('anz.', 'anz', 'anzahl', 'szt'):
            val += 'szt'
        elif key in ('posn', 'poz', 'pos', 'pozycja'):
            val = 'p' + val

        result.append(val)

    return SEP.join(result)


def collect_rows(df: pd.DataFrame) -> dict:
    base_dir = os.path.join(os.getcwd(), RYSUNKI_DIR)
    result = {}
    for _, row in df.iterrows():
        base = str(row['Rysunek']).strip()
        line = build_line(row)
        if base not in result:
            exact = glob.glob(os.path.join(base_dir, f'{base}.pdf'))
            ext = glob.glob(os.path.join(base_dir, f'{base}_*.pdf'))
            result[base] = {
                'pdf': exact[0] if exact else (ext[0] if ext else None),
                'lines': []
            }
        if line:
            korekta = row.get("korekta", "")
            result[base]['lines'].append((line, korekta))
    return result


def parse_korekta(korekta: str) -> tuple[int, int]:
    dx = dy = 0
    if isinstance(korekta, str):
        for fragment in korekta.split(','):
            f = fragment.strip().upper()
            if f.startswith("P"): dx += int(f[1:])
            if f.startswith("L"): dx -= int(f[1:])
            if f.startswith("G"): dy -= int(f[1:])
            if f.startswith("D"): dy += int(f[1:])
    return dx, dy


def write_lines_to_pdf(src_pdf: str, dst_pdf: str, lines: list[tuple[str, str]], font_size: int, offset_x: int, offset_y: int):
    with fitz.open(src_pdf) as doc:
        page = doc[0]
        spacing = font_size + 4
        start_y = page.rect.height - offset_y - spacing * len(lines)
        for idx, (txt, korekta) in enumerate(lines):
            dx, dy = parse_korekta(korekta)
            x = offset_x + dx
            y = start_y + idx * spacing + dy
            page.insert_text((x, y), txt, fontsize=font_size, color=(0, 0, 0))
        doc.save(dst_pdf)


# ---------- GŁÓWNA FUNKCJA -------------------------------------------------

def main():
    ust = wczytaj_ustawienia()
    ust = menu_startowe(ust)
    pdf_dir = os.path.join(os.getcwd(), RYSUNKI_DIR)
    if not os.path.isdir(pdf_dir):
        raise FileNotFoundError(f'Brak folderu: {pdf_dir}')
    df = pd.read_excel(ust["EXCEL_FILE"], dtype=str)
    if 'Rysunek' not in df.columns:
        raise KeyError("W Excelu brak kolumny 'Rysunek'.")
    data = collect_rows(df)
    missing = []
    for base, info in data.items():
        src = info['pdf']
        if src is None:
            missing.append(base)
            continue
        dst = src.replace('.pdf', '_+opracowanie.pdf')
        write_lines_to_pdf(src, dst, info['lines'], ust["FONT_SIZE"], ust["OFFSET_X"], ust["OFFSET_Y"])
        print(f'✔  {os.path.basename(dst)} (dodano {len(info["lines"])} lin.)')
    if missing:
        with open(MISSING_FILE, 'w', encoding='utf-8') as f:
            for m in missing:
                f.write(f'{m}\n')
        print(f'\n⚠  Brak {len(missing)} PDF-ów – lista w {MISSING_FILE}')
    print('\nGotowe!')


if __name__ == '__main__':
    main()
