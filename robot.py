import requests
from bs4 import BeautifulSoup
import json, time, os, re

BASE_URL = "https://obchod.fimas.cz"

# ZDROJOVE URL — vsechny kategorie z e-shopu tykajici se brzd a naprav
START_URLS = [
    # Hlavni sekce
    BASE_URL + "/BRZDY-NAPRAVY-VZDUCH-c2_0_1.htm",
    BASE_URL + "/-c85_0_1.htm",
    # Nápravy podle vyrobce
    BASE_URL + "/ADR-COLAERT-ESSIEUX-c23_0_1.htm",
    BASE_URL + "/BPW-AGRO-napravy-c70_0_1.htm",
    BASE_URL + "/FAD-napravy-c79_0_1.htm",
    BASE_URL + "/KEZMAROK-napravy-a-dily-c117_0_1.htm",
    BASE_URL + "/NAPRAVY-c44_0_1.htm",
    BASE_URL + "/Napravy-N900-MV2-027-c10_218_2.htm",
    BASE_URL + "/Naprava-nahradni-dily-c16_123_2.htm",
    BASE_URL + "/POLONAPRAVA-c45_0_1.htm",
    BASE_URL + "/Vahadlo-a-dily-napravy-c97_572_2.htm",
    BASE_URL + "/Dily-podvozku-vahadla-c12_107_2.htm",
    # Brzdy
    BASE_URL + "/BRZDOVE-OBLOZENI-DESKY-c35_0_1.htm",
    BASE_URL + "/BRZDOVY-VALEC-c36_0_1.htm",
    BASE_URL + "/BUBEN-BRZDY-c37_0_1.htm",
    BASE_URL + "/BUBEN-BRZDY-S-NABOJEM-c38_0_1.htm",
    BASE_URL + "/CELIST-BRZDY-c39_0_1.htm",
    BASE_URL + "/CEP-BRZDOVE-CELISTI-c129_0_1.htm",
    BASE_URL + "/KLIC-BRZDY-c42_0_1.htm",
    BASE_URL + "/KRYT-BRZDOVEHO-BUBNU-c126_0_1.htm",
    BASE_URL + "/NYTY-PRO-OBLOZENI-c127_0_1.htm",
    BASE_URL + "/PAKA-BRZDOVEHO-KLICE-c125_0_1.htm",
    BASE_URL + "/PRUZINA-BRZDOVE-CELISTI-c46_0_1.htm",
    BASE_URL + "/oblozeni-brzdy-BPW-AGRO-c70_0_1.htm",
    BASE_URL + "/VZDUCHOVE-BRZDY-c61_0_1.htm",
    # Kolo / naboj
    BASE_URL + "/CEP-KOLA-NAPRAVY-c41_0_1.htm",
    BASE_URL + "/DISK-KOLA-c8_0_1.htm",
    BASE_URL + "/GUFERO-A-KROUZEK-NAPRAVY-c64_0_1.htm",
    BASE_URL + "/KROUZEK-STREDICI-c54_0_1.htm",
    BASE_URL + "/LOZISKO-NAPRAVY-c65_0_1.htm",
    BASE_URL + "/MATICE-DISKOVA-c50_0_1.htm",
    BASE_URL + "/NABOJ-KOLA-c43_0_1.htm",
    BASE_URL + "/SROUB-KOLA-c49_0_1.htm",
    BASE_URL + "/VICKO-NABOJE-c58_0_1.htm",
    BASE_URL + "/VLOZKA-SROUBU-KOLA-c56_0_1.htm",
    # Podvozek
    BASE_URL + "/POUZDRA-c1_0_1.htm",
    BASE_URL + "/PERO-LISTOVE-c5_0_1.htm",
    BASE_URL + "/PODLOZKA-PEROVA-c55_0_1.htm",
]

POVOLENE = [
    '-c2_', '-c2-', '-c85', '-c23', '-c79', '-c70', '-c61',
    '-c43', '-c1_', '-c1-', '-c5_', '-c5-', '-c7_', '-c7-',
    '-c8_', '-c10', '-c11', '-c12', '-c14', '-c15', '-c16',
    '-c17', '-c18', '-c19', '-c20', '-c21', '-c22', '-c24',
    '-c25', '-c26', '-c27', '-c28', '-c29', '-c30',
    '-c35', '-c36', '-c37', '-c38', '-c39',
    '-c40', '-c41', '-c42', '-c44', '-c45', '-c46', '-c47',
    '-c48', '-c49', '-c50', '-c51', '-c52', '-c53', '-c54',
    '-c55', '-c56', '-c57', '-c58', '-c59', '-c60',
    '-c62', '-c63', '-c64', '-c65', '-c66', '-c67', '-c68',
    '-c69', '-c71', '-c72', '-c73', '-c74', '-c75', '-c76',
    '-c77', '-c78', '-c80', '-c81', '-c82',
    '-c97', '-c100', '-c101', '-c102', '-c103', '-c104', '-c105',
    '-c106', '-c107', '-c108', '-c109', '-c110', '-c117',
    '-c125', '-c126', '-c127', '-c129',
    '-c218', '-c572', '-c123',
    '-c285', '-c286', '-c287', '-c311', '-c312', '-c313',
    '-c402', '-c427', '-c515', '-c597', '-c719', '-c720',
    '?strana=',
]

# ============================================================
# WHITELIST — kategorizace podle nazvu produktu
# Poradi je dulezite: prioritnejsi (specifictejsi) klice jsou prvni.
# ============================================================
PRODUCT_KEYWORDS = [
    # === PRIORITA 110 — nejspecifictejsi nove kategorie ===
    (110, 'kryt bubnu', 'kryt-bubnu'),
    (110, 'kryt brzdoveho bubnu', 'kryt-bubnu'),
    (110, 'kryt brzdového bubnu', 'kryt-bubnu'),
    (110, 'nyt pro obloz', 'nyty-obloz'),
    (110, 'nýt pro obloz', 'nyty-obloz'),
    (110, 'nyty pro obloz', 'nyty-obloz'),
    (110, 'nýty pro obloz', 'nyty-obloz'),
    (110, 'cep brzdove celisti', 'cep-brzdove-celisti'),
    (110, 'čep brzdové čelisti', 'cep-brzdove-celisti'),
    (110, 'cep celisti', 'cep-brzdove-celisti'),
    (110, 'čep čelisti', 'cep-brzdove-celisti'),
    (110, 'pruzina brzdov celisti', 'pruzina-celisti'),
    (110, 'pružina brzdové čelisti', 'pruzina-celisti'),
    (110, 'pruzina celisti', 'pruzina-celisti'),
    (110, 'pružina čelisti', 'pruzina-celisti'),
    (110, 'pruzina celist', 'pruzina-celisti'),
    (110, 'pružina čelist', 'pruzina-celisti'),
    (110, 'vicko naboje', 'vicko-naboje'),
    (110, 'víčko náboje', 'vicko-naboje'),
    (110, 'vlozka sroubu kola', 'vlozka-sroubu'),
    (110, 'vložka šroubu kola', 'vlozka-sroubu'),
    (110, 'krouzek stredici', 'krouzek-stredici'),
    (110, 'kroužek středicí', 'krouzek-stredici'),
    (110, 'krouzek stredic', 'krouzek-stredici'),
    (110, 'kroužek středic', 'krouzek-stredici'),
    (110, 'gufero', 'gufero-krouzek'),
    (110, 'gufero a krouzek', 'gufero-krouzek'),
    (110, 'gufero a kroužek', 'gufero-krouzek'),
    (110, 'lozisko naprav', 'lozisko-napravy'),
    (110, 'ložisko náprav', 'lozisko-napravy'),
    (110, 'lozisko nabo', 'lozisko-napravy'),
    (110, 'ložisko nábo', 'lozisko-napravy'),
    (110, 'podlozka perova', 'podlozka-perova'),
    (110, 'podložka pérová', 'podlozka-perova'),
    (110, 'podlozka pero', 'podlozka-perova'),
    (110, 'podložka péro', 'podlozka-perova'),
    (110, 'polonaprav', 'polonaprava'),
    (110, 'polonáprav', 'polonaprava'),
    (110, 'paka brzdoveho klice', 'paka-klice'),
    (110, 'páka brzdového klíče', 'paka-klice'),
    (110, 'paka brzdov klice', 'paka-klice'),
    (110, 'páka brzdov klíče', 'paka-klice'),

    # === PRIORITA 100 — specifictejsi ===
    (100, 'vahadl naprav', 'vahadlo-napravy'),
    (100, 'vahadlo naprav', 'vahadlo-napravy'),
    (100, 'cep vahadla', 'vahadlo-napravy'),
    (100, 'čep vahadla', 'vahadlo-napravy'),
    (100, 'cep kola vahadl', 'vahadlo-napravy'),
    (100, 'čep kola vahadl', 'vahadlo-napravy'),
    (100, 'vahadl', 'dily-vahadla'),  # fallback pro ostatni vahadla
    (100, 'buben brzdy s naboj', 'buben-s-nabojem'),
    (100, 'buben brzdy s náboj', 'buben-s-nabojem'),
    (100, 'pero listov', 'pero-listove'),
    (100, 'pera listov', 'pero-listove'),
    (100, 'cep pera', 'cepy-pouzdra'),
    (100, 'čep pera', 'cepy-pouzdra'),
    (100, 'pouzdro pera', 'cepy-pouzdra'),
    (100, 'cep kola naprav', 'cep-kola'),
    (100, 'čep kola náprav', 'cep-kola'),
    (100, 'cep kola', 'cep-kola'),
    (100, 'čep kola', 'cep-kola'),
    (100, 'paka klice', 'paka-klice'),
    (100, 'páka klíče', 'paka-klice'),
    (100, 'trmen pera', 'trmen-pera'),
    (100, 'třmen pera', 'trmen-pera'),

    # === PRIORITA 90 — napravy podle vyrobce ===
    (90, 'naprava adr', 'napravy-adr'),
    (90, 'náprava adr', 'napravy-adr'),
    (90, 'naprava colaert', 'napravy-adr'),
    (90, 'náprava colaert', 'napravy-adr'),
    (90, 'naprava bpw', 'napravy-bpw'),
    (90, 'náprava bpw', 'napravy-bpw'),
    (90, 'naprava fad', 'napravy-fad'),
    (90, 'náprava fad', 'napravy-fad'),
    (90, 'naprava kezmarok', 'napravy-kezmarok'),
    (90, 'náprava kežmarok', 'napravy-kezmarok'),
    (90, 'naprava n900', 'napravy-n900'),
    (90, 'náprava n900', 'napravy-n900'),
    (90, 'naprava mv2-027', 'napravy-n900'),
    (90, 'náprava mv2-027', 'napravy-n900'),

    # === PRIORITA 80 — hlavni terminy ===
    # Brzdy
    (80, 'buben brzdy', 'buben-brzdy'),
    (80, 'buben s naboj', 'buben-s-nabojem'),
    (80, 'buben s náboj', 'buben-s-nabojem'),
    (80, 'brzdov obloz', 'brzdove-oblozeni'),
    (80, 'brzdové obloz', 'brzdove-oblozeni'),
    (80, 'oblozeni brzd', 'brzdove-oblozeni'),
    (80, 'obložení brzd', 'brzdove-oblozeni'),
    (80, 'obloženi brzd', 'brzdove-oblozeni'),
    (80, 'brzdov destic', 'brzdove-oblozeni'),
    (80, 'brzdové destič', 'brzdove-oblozeni'),
    (70, 'obloženi ', 'brzdove-oblozeni'),
    (70, 'obložení ', 'brzdove-oblozeni'),
    (70, 'oblozeni ', 'brzdove-oblozeni'),
    (80, 'celist brzdy', 'celist-brzdy'),
    (80, 'čelist brzdy', 'celist-brzdy'),
    (80, 'celist brzdov', 'celist-brzdy'),
    (80, 'čelist brzdov', 'celist-brzdy'),
    (80, 'klic brzdy', 'klic-brzdy'),
    (80, 'klíč brzdy', 'klic-brzdy'),
    (80, 'klic brzdov', 'klic-brzdy'),
    (80, 'klíč brzdov', 'klic-brzdy'),
    (80, 'klic rozperny', 'klic-brzdy'),
    (80, 'klíč rozpěrný', 'klic-brzdy'),
    (80, 'paka brzdov', 'paka-klice'),
    (80, 'páka brzdov', 'paka-klice'),
    (80, 'brzdovy valec', 'brzdovy-valec'),
    (80, 'brzdový válec', 'brzdovy-valec'),
    (80, 'valec brzdy', 'brzdovy-valec'),
    (80, 'válec brzdy', 'brzdovy-valec'),
    (80, 'valec brzdov', 'brzdovy-valec'),
    (80, 'válec brzdov', 'brzdovy-valec'),
    (80, 'membranovy valec', 'brzdovy-valec'),
    (80, 'membránový válec', 'brzdovy-valec'),
    (80, 'brzda rucni', 'brzda-rucni'),
    (80, 'brzda ruční', 'brzda-rucni'),
    (80, 'rucni brzda', 'brzda-rucni'),
    (80, 'ruční brzda', 'brzda-rucni'),
    (80, 'membrana valc', 'membrany-valcu'),
    (80, 'membrána válc', 'membrany-valcu'),
    (80, 'nahradni dily valc', 'nd-valcu'),
    (80, 'náhradní díly válc', 'nd-valcu'),
    (80, 'opravarsk sada valc', 'nd-valcu'),
    (80, 'opravárenská sada válc', 'nd-valcu'),

    # Kolo / naboj
    (80, 'naboj kola', 'naboj-kola'),
    (80, 'náboj kola', 'naboj-kola'),
    (80, 'disk kola', 'disk-kola'),
    (80, 'sroub kola', 'srouby-kola'),
    (80, 'šroub kola', 'srouby-kola'),
    (80, 'srouby kola', 'srouby-kola'),
    (80, 'šrouby kola', 'srouby-kola'),
    (80, 'matice diskov', 'srouby-kola'),
    (80, 'matice kola', 'srouby-kola'),
    (80, 'tesneni nabo', 'naboj-kola'),
    (80, 'těsnění nábo', 'naboj-kola'),

    # Napravy - fallback obecne (po specifickych vyrobcich)
    (80, 'napravy', 'napravy-obecne'),
    (80, 'nápravy', 'napravy-obecne'),
    (80, 'naprava', 'napravy-obecne'),
    (80, 'náprava', 'napravy-obecne'),

    # Vzduchove brzdy
    (80, 'ventil brzd', 'ventily-brzd'),
    (80, 'brzdovy ventil', 'ventily-brzd'),
    (80, 'brzdový ventil', 'ventily-brzd'),
    (80, 'ventil prives', 'ventily-brzd'),
    (80, 'ventil přívěs', 'ventily-brzd'),
    (80, 'ventil ovlad', 'ventily-brzd'),
    (80, 'ventil ovlád', 'ventily-brzd'),
    (80, 'ventil odvodn', 'ventily-brzd'),
    (80, 'ventil modulator', 'ventily-brzd'),
    (80, 'ventil modulátor', 'ventily-brzd'),
    (80, 'ventil prepoust', 'ventily-brzd'),
    (80, 'ventil přepoušt', 'ventily-brzd'),
    (80, 'ventil dvoj', 'ventily-brzd'),
    (80, 'ventil trojcest', 'ventily-brzd'),
    (80, 'ventil tlac', 'ventily-brzd'),
    (80, 'ventil tlač', 'ventily-brzd'),
    (80, 'ventil jednos', 'ventily-brzd'),
    (80, 'ventil reduk', 'ventily-brzd'),
    (80, 'ventil zpetn', 'ventily-brzd'),
    (80, 'ventil zpětn', 'ventily-brzd'),
    (80, 'ventil vyfuk', 'ventily-brzd'),
    (80, 'ventil rele', 'ventily-brzd'),
    (80, 'ventil relé', 'ventily-brzd'),
    (80, 'wabco', 'ventily-brzd'),
    (80, 'knorr-bremse', 'ventily-brzd'),
    (80, 'haldex', 'ventily-brzd'),
    (80, 'vzduchoj', 'vzduchojemy'),
    (80, 'rozvadec vzduch', 'rozvadece'),
    (80, 'rozvaděč vzduch', 'rozvadece'),
    (80, 'rozvadec brzd', 'rozvadece'),
    (80, 'rozvaděč brzd', 'rozvadece'),
    (80, 'regulator brzd', 'ventily-brzd'),
    (80, 'regulátor brzd', 'ventily-brzd'),
    (80, 'spojkov hlavice', 'ventily-brzd'),
    (80, 'spojková hlavice', 'ventily-brzd'),
    (80, 'hadice brzd', 'nd-valcu'),
    (80, 'brzdov hadice', 'nd-valcu'),
    (80, 'brzdová hadice', 'nd-valcu'),
    (80, 'trubka brzd', 'nd-valcu'),
    (80, 'trubka vzduch', 'nd-valcu'),
    (80, 'spona brzd', 'nd-valcu'),
    (80, 'podlozka brzd', 'nd-valcu'),
    (80, 'podložka brzd', 'nd-valcu'),
    (80, 'ulozeni brzd', 'nd-valcu'),
    (80, 'uložení brzd', 'nd-valcu'),

    # Cep svisly / vicko horni atd.
    (80, 'cep svisl', 'cep-kola'),
    (80, 'čep svisl', 'cep-kola'),
    (80, 'svisly cep', 'cep-kola'),
    (80, 'svislý čep', 'cep-kola'),
    (80, 'vicko horni', 'cep-kola'),
    (80, 'víčko horní', 'cep-kola'),
    (80, 'vicko doln', 'cep-kola'),
    (80, 'víčko doln', 'cep-kola'),
    (80, 'krouzek pojistn', 'cepy-pouzdra'),
    (80, 'kroužek pojistn', 'cepy-pouzdra'),
    (80, 'krouzek navarn', 'cepy-pouzdra'),
    (80, 'kroužek navarn', 'cepy-pouzdra'),

    # Obecne pruziny (bez celist/vratn/pridavn -> prida se pri specifictejsim)
    (80, 'pruzina talirov', 'nd-valcu'),
    (80, 'pružina talířov', 'nd-valcu'),
    (80, 'pruzina pridavn', 'nd-valcu'),
    (80, 'pružina přídavn', 'nd-valcu'),
    (80, 'pruzina vratn', 'pruzina-celisti'),
    (80, 'pružina vratn', 'pruzina-celisti'),
]

# Blacklist — produkty mimo tema (presne: nepatri do brzd ani naprav)
BLACKLIST_KEYWORDS = [
    # Tazne ustroji
    'tazna oj', 'tažná oj',
    'oje tazn', 'oje tažn',
    'oko tazne', 'oko tažné',
    'oko zavesn', 'oko závěsn',
    'tazne oko', 'tažné oko',
    'deska pod tazn', 'deska pod tažn',
    'ringfeder', 'jost kz',
    'cep kralovsk', 'čep královsk',

    # Hydraulika / zvedaky
    'zvedak', 'zvedák',
    'manzeta zvedak', 'manžeta zvedák',
    'manzeta hydraul', 'manžeta hydraul',
    'manzeta kozen', 'manžeta kožen',
    'ulozeni zvedak', 'uložení zvedák',
    'hydraul',

    # Prislusenstvi (bocnice, blatniky, ram)
    'bocnice', 'bočnice',
    'blatnik', 'blatník',
    'ram podvoz', 'rám podvoz',
    'ram horni', 'rám horní',
    'ram doln', 'rám dolní',
    'drzak rezerv', 'držák rezerv',
    'bedna', 'kanystr',
    'klin zaklad', 'klín zaklád',
    'nastav', 'nástav',

    # Znaceni / svetla / elektro
    'trojuhelnik', 'trojúhelník',
    'konektor', 'adapter', 'adaptér',
    'kabel propojov', 'zastrck', 'zástrčk',
    'svitiln', 'svítiln', 'majak', 'maják',
    'odrazk', 'odrážk', 'reflexn',
    'tabulka', 'stitek', 'štítek', 'samolepk',
    'nabijeck', 'nabíječk',
    'topen', 'vymenik', 'výměník',

    # Vyvevy
    'vyvev', 'vývěv', 'perrot', 'lopatk', 'dyza', 'dýza',
    'lamela vyvev', 'lamela vývěv',
    'tryska', 'sifon', 'sifón',

    # Jine
    'kardan', 'hridel kardan', 'hřídel kardan',
    'tocna', 'točna',
    'kohout', 'hadice propojov',
    'zabezpeceni nakladu', 'zabezpečení nákladu',
    'zaves sada', 'závěs sada',
    'hlavice spojov',
    'kapatk', 'kápátk',
    'katalog',  # "katalog PS2..." atd.

    # Generic spojovaci material bez kontextu kola/brzdy
    'sroub m ', 'šroub m ',
    'matice m16x', 'matice m20x', 'matice m24x', 'matice m30x',
]

def categorize_product(name, subtitle=''):
    text = (name + ' ' + subtitle).lower()
    for bl in BLACKLIST_KEYWORDS:
        if bl in text:
            return None
    best_priority = 0
    best_cat = None
    for priority, keyword, cat_id in PRODUCT_KEYWORDS:
        if keyword in text and priority > best_priority:
            best_priority = priority
            best_cat = cat_id
    return best_cat

print("=" * 60)
print("  ROBOT DILY NA NAPRAVY v4 (rozsirene kategorie)")
print("=" * 60)

h = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
queue = START_URLS.copy()
visited = set()
products = {}
pages = 0
errors = 0
vyrazeno = 0

while queue:
    url = queue.pop(0)
    if url in visited: continue
    visited.add(url)
    pages += 1
    short = url.split('/')[-1][:55]
    print(f"[{pages:3d}] {short}")

    try:
        r = requests.get(url, headers=h, timeout=20)
        r.encoding = 'utf-8'
        if r.status_code != 200:
            print(f"      HTTP {r.status_code}")
            errors += 1
            continue

        soup = BeautifulSoup(r.text, 'html.parser')

        prods = soup.find_all('div', class_='product')
        if not prods:
            prods = soup.find_all('div', class_=re.compile(r'^product', re.I))

        na_strance_ok = 0
        na_strance_vyrazeno = 0

        for p in prods:
            td = p.find('div', class_='productTitleContent')
            if not td: td = p.find('h3')
            if not td:
                for a in p.find_all('a', href=True):
                    if a.text.strip() and len(a.text.strip()) > 3 and '-d' in a.get('href',''):
                        td = a; break
            if not td: continue

            atag = td.find('a') if td.name != 'a' else td
            if not atag or not atag.text.strip(): continue

            name = atag.text.strip()
            href = atag.get('href', '')
            if not href: continue
            link = href if href.startswith('http') else BASE_URL + ('' if href.startswith('/') else '/') + href

            sub = p.find('p', class_='productSubtitle') or p.find('span', class_='productSubtitle')
            subtitle = sub.text.strip() if sub else ""

            cat_id = categorize_product(name, subtitle)
            if cat_id is None:
                na_strance_vyrazeno += 1
                continue

            img_url = ""
            img_box = p.find('div', class_='img_box')
            if not img_box: img_box = p.find('div', class_='productImage')
            if not img_box: img_box = p.find('a', class_='productImage')
            if img_box:
                img = img_box.find('img')
                if img and img.get('src'):
                    src = img['src']
                    img_url = src if src.startswith('http') else BASE_URL + ('' if src.startswith('/') else '/') + src
            if not img_url:
                img = p.find('img')
                if img and img.get('src'):
                    src = img['src']
                    if not src.startswith('data:') and 'spacer' not in src.lower():
                        img_url = src if src.startswith('http') else BASE_URL + ('' if src.startswith('/') else '/') + src

            stock = 'skladem' if p.find(class_='stock_yes') else 'na-dotaz'

            if link not in products:
                products[link] = {
                    "id": str(len(products)+1),
                    "name": name,
                    "subtitle": subtitle,
                    "category": cat_id,
                    "stock": stock,
                    "image": img_url,
                    "url": link
                }
                na_strance_ok += 1

        vyrazeno += na_strance_vyrazeno

        if na_strance_ok > 0 or na_strance_vyrazeno > 0:
            print(f"      +{na_strance_ok} produktu, -{na_strance_vyrazeno} vyrazeno")

        for a in soup.find_all('a', href=True):
            hr = a['href']
            if any(k in hr for k in POVOLENE) and '.htm' in hr:
                full = hr if hr.startswith('http') else BASE_URL + ('' if hr.startswith('/') else '/') + hr
                if full not in visited and full not in queue:
                    queue.append(full)

        time.sleep(0.3)

    except Exception as e:
        print(f"      ERROR: {e}")
        errors += 1

result = list(products.values())
for i, p in enumerate(result, 1): p['id'] = str(i)

stats = {}
for p in result:
    stats[p['category']] = stats.get(p['category'], 0) + 1

s_foto = sum(1 for p in result if p.get('image'))

path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data.json')
with open(path, 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=4)

print()
print("=" * 60)
print(f"  HOTOVO!")
print(f"  Produktu: {len(result)} (s fotkou: {s_foto})")
print(f"  Vyrazeno (mimo tema): {vyrazeno}")
print(f"  Stranek: {pages}, chyb: {errors}")
print(f"  Kategorii: {len(stats)}")
print("-" * 60)
for c, n in sorted(stats.items(), key=lambda x: -x[1]):
    print(f"  {c:30s} {n:4d}")
print("=" * 60)
