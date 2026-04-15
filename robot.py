import requests
from bs4 import BeautifulSoup
import json
import time
import os
import re

BASE_URL = "https://obchod.fimas.cz"

# ============================================================
# STARTOVACÍ ADRESY — hlavní sekce s díly na nápravy
# ============================================================
START_URLS = [
    # dilynanapravy.cz sekce (brzdové obložení, válce, bubny, čepy, čelisti, disky)
    "https://obchod.fimas.cz/-c85_0_1.htm",
    # BRZDY - NÁPRAVY - celková sekce
    "https://obchod.fimas.cz/BRZDY-NAPRAVY-VZDUCH-c2_0_1.htm",
    # ADR, COLAERT ESSIEUX nápravy
    "https://obchod.fimas.cz/ADR-nahradni-dily-c23_0_1.htm",
    # FAD nápravy
    "https://obchod.fimas.cz/FAD-napravy-c79_0_1.htm",
    # BPW AGRO nápravy
    "https://obchod.fimas.cz/oblozeni-brzdy-BPW-AGRO-c70_0_1.htm",
    # Vzduchové brzdy
    "https://obchod.fimas.cz/VZDUCHOVE-BRZDY-c61_0_1.htm",
    # Hydraulické zvedáky
    "https://obchod.fimas.cz/ZVEDAK-HYDRAULICKY-c9_0_1.htm",
    # Náboj kola
    "https://obchod.fimas.cz/NABOJ-KOLA-c43_0_1.htm",
    # Čepy, pouzdra, kroužky
    "https://obchod.fimas.cz/POUZDRA-c1_0_1.htm",
    # Pera listová
    "https://obchod.fimas.cz/PERO-LISTOVE-c5_0_1.htm",
]

# Povolené kódy kategorií pro crawling (robot smí vstoupit jen sem)
POVOLENE_KODY = [
    'c85', 'c2_', 'c2-', 'c23', 'c79', 'c70', 'c61', 'c9_', 'c9-',
    'c43', 'c1_', 'c1-', 'c5_', 'c5-', 'c19',
    # Podkategorie brzd a náprav
    'c3_', 'c3-', 'c4_', 'c4-', 'c6_', 'c6-', 'c7_', 'c7-',
    'c8_', 'c8-', 'c10', 'c11', 'c14', 'c15', 'c16', 'c17', 'c18',
    'c20', 'c21', 'c22', 'c24', 'c25', 'c26', 'c27', 'c28',
    'c40', 'c41', 'c42', 'c44', 'c45', 'c46', 'c47', 'c48', 'c49',
    'c50', 'c51', 'c52', 'c53', 'c54', 'c55', 'c56', 'c57', 'c58',
    'c59', 'c60', 'c62', 'c63', 'c64', 'c65', 'c66', 'c67', 'c68',
    'c69', 'c71', 'c72', 'c73', 'c74', 'c75', 'c76', 'c77', 'c78',
    'c80', 'c81', 'c82',
    'c100', 'c101', 'c102', 'c103', 'c104', 'c105',
    'c106', 'c107', 'c108', 'c109', 'c110',
    'c285', 'c286', 'c287',  # čepy, pouzdra, kroužky
    'c311', 'c312', 'c313',  # pera listová
    'c402', 'c427', 'c515', 'c597',  # BPW, ADR podkategorie
    'c719', 'c720', 'c721',  # FAD podkategorie
]

# ============================================================
# MAPOVÁNÍ KATEGORIÍ — název z H1 e-shopu → ID v aplikaci
# ============================================================
CATEGORY_MAP = {
    # Brzdy a brzdové díly
    'brzdové obložení': 'brzdove-oblozeni',
    'brzdové desky': 'brzdove-oblozeni',
    'obložení brzdy': 'brzdove-oblozeni',
    'brzdový válec': 'brzdovy-valec',
    'válec brzdy': 'brzdovy-valec',
    'válce': 'brzdovy-valec',
    'válce cz': 'brzdovy-valec',
    'membránové': 'brzdovy-valec',
    'buben brzdy s nábojem': 'buben-s-nabojem',
    'buben brzdy': 'buben-brzdy',
    'buben': 'buben-brzdy',
    'čelist brzdy': 'celist-brzdy',
    'čelist': 'celist-brzdy',
    'klíč brzdy': 'klic-brzdy',
    'páka klíče': 'paka-klice',
    'brzda ruční': 'brzda-rucni',
    'ruční brzda': 'brzda-rucni',
    'membrány': 'membrany-valcu',
    'membrány do válců': 'membrany-valcu',
    'náhradní díly válců': 'nd-valcu',
    # Kolo a náboj
    'náboj kola': 'naboj-kola',
    'náboj': 'naboj-kola',
    'čep kola': 'cep-kola',
    'čep': 'cep-kola',
    'šrouby kola': 'srouby-kola',
    'šroub kola': 'srouby-kola',
    'matice kola': 'srouby-kola',
    'disk kola': 'disk-kola',
    'disk': 'disk-kola',
    # Podvozek a odpružení
    'pero listové': 'pero-listove',
    'pera listová': 'pero-listove',
    'třmen pera': 'trmen-pera',
    'třmeny': 'trmen-pera',
    'čepy': 'cepy-pouzdra',
    'pouzdra': 'cepy-pouzdra',
    'kroužky': 'cepy-pouzdra',
    'kroužky čepů': 'cepy-pouzdra',
    # Tažné ústrojí
    'tažná oj': 'tazna-oj',
    'oj tažná': 'tazna-oj',
    'oko tažné oje': 'oko-tazne-oje',
    # Hydraulika
    'zvedák hydraulický': 'hydraul-zvedaky',
    'hydraulické zvedáky': 'hydraul-zvedaky',
    'zvedáky': 'hydraul-zvedaky',
    'manžety': 'manzety',
    'manžety do zvedáků': 'manzety',
    'uložení zvedáků': 'ulozeni-zvedaku',
    'uložení': 'ulozeni-zvedaku',
    # Vzduchové brzdy
    'vzduchové brzdy': 'ventily-brzd',
    'ventil': 'ventily-brzd',
    'ventily': 'ventily-brzd',
    'vzduchojemy': 'vzduchojemy',
    'rozvaděč': 'rozvadece',
    'rozvaděče': 'rozvadece',
    # Příslušenství
    'blatník': 'blatniky',
    'blatníky': 'blatniky',
    'držák blatníku': 'blatniky',
    'bočnice': 'bocnice',
    'kování bočnic': 'bocnice',
}

def map_category(h1_text):
    """Namapuje nadpis kategorie z e-shopu na ID kategorie v aplikaci."""
    text = h1_text.lower().strip()
    # Přesná shoda
    if text in CATEGORY_MAP:
        return CATEGORY_MAP[text]
    # Částečná shoda — hledáme klíčová slova
    for klic, cat_id in CATEGORY_MAP.items():
        if klic in text:
            return cat_id
    # Fallback: zjednodušit název
    return re.sub(r'[^a-z0-9]+', '-', text.replace('á','a').replace('é','e')
        .replace('í','i').replace('ó','o').replace('ú','u').replace('ů','u')
        .replace('ý','y').replace('ž','z').replace('š','s').replace('č','c')
        .replace('ř','r').replace('ď','d').replace('ť','t').replace('ň','n')
        .replace('ě','e')).strip('-')


# ============================================================
# HLAVNÍ CRAWLING
# ============================================================
print("=" * 60)
print("  ROBOT DÍLY NA NÁPRAVY — dilynanapravy.cz")
print("  Stahování dat z obchod.fimas.cz")
print("=" * 60)

hlavicka = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}

urls_to_visit = START_URLS.copy()
visited_urls = set()
vsechny_produkty = {}
pocitadlo_stranek = 0

while urls_to_visit:
    aktualni_url = urls_to_visit.pop(0)

    if aktualni_url in visited_urls:
        continue

    visited_urls.add(aktualni_url)
    pocitadlo_stranek += 1

    kratky_nazev = aktualni_url.split('/')[-1][:50]
    print(f"[{pocitadlo_stranek:3d}] Čtu: {kratky_nazev}...")

    try:
        res = requests.get(aktualni_url, headers=hlavicka, timeout=15)
        res.encoding = 'utf-8'
        s = BeautifulSoup(res.text, 'html.parser')

        # Přečteme nadpis kategorie (H1) a namapujeme
        nadpis = s.find('h1')
        kategorie_raw = nadpis.text.strip() if nadpis else "Ostatní díly"
        kategorie_id = map_category(kategorie_raw)

        # Stahování produktů
        produkty = s.find_all('div', class_='product')
        for p in produkty:
            title_div = p.find('div', class_='productTitleContent')
            if not title_div:
                continue

            a_tag = title_div.find('a')
            nazev = a_tag.text.strip()

            odkaz = a_tag['href']
            if not odkaz.startswith('http'):
                odkaz = BASE_URL + odkaz if odkaz.startswith('/') else BASE_URL + '/' + odkaz

            subtitle_tag = p.find('p', class_='productSubtitle')
            podtitul = subtitle_tag.text.strip() if subtitle_tag else ""

            sklad = p.find('div', class_='stock_yes') or p.find('div', class_='stock_no')
            if sklad:
                sklad_text = sklad.text.strip().lower()
                dostupnost = 'skladem' if 'sklad' in sklad_text else 'na-dotaz'
            else:
                dostupnost = 'na-dotaz'

            unikatni_klic = odkaz

            if unikatni_klic not in vsechny_produkty:
                vsechny_produkty[unikatni_klic] = {
                    "id": str(len(vsechny_produkty) + 1),
                    "name": nazev,
                    "subtitle": podtitul,
                    "category": kategorie_id,
                    "stock": dostupnost,
                    "url": odkaz
                }

        # Hledání dalších odkazů — jen v povolených sekcích
        for a in s.find_all('a', href=True):
            href = a['href']

            je_spravny = any(kod in href for kod in POVOLENE_KODY) or '?strana=' in href

            if je_spravny and '.htm' in href:
                plny_odkaz = href if href.startswith('http') else \
                    BASE_URL + href if href.startswith('/') else \
                    BASE_URL + '/' + href
                if plny_odkaz not in visited_urls and plny_odkaz not in urls_to_visit:
                    urls_to_visit.append(plny_odkaz)

        time.sleep(0.3)

    except Exception as e:
        print(f"  -> CHYBA: {e}")
        continue

# ============================================================
# ULOŽENÍ
# ============================================================
seznam = list(vsechny_produkty.values())

# Re-indexace ID
for i, produkt in enumerate(seznam, 1):
    produkt['id'] = str(i)

# Statistiky kategorií
kategorie_stats = {}
for p in seznam:
    cat = p['category']
    kategorie_stats[cat] = kategorie_stats.get(cat, 0) + 1

aktualni_slozka = os.path.dirname(os.path.abspath(__file__))
cesta = os.path.join(aktualni_slozka, 'data.json')

with open(cesta, 'w', encoding='utf-8') as f:
    json.dump(seznam, f, ensure_ascii=False, indent=4)

print()
print("=" * 60)
print(f"  HOTOVO! Staženo {len(seznam)} produktů")
print(f"  Prohledáno {pocitadlo_stranek} stránek")
print(f"  Kategorií: {len(kategorie_stats)}")
print("-" * 60)
for cat, count in sorted(kategorie_stats.items(), key=lambda x: -x[1]):
    print(f"  {cat:30s} {count:4d} ks")
print("=" * 60)
