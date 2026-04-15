import requests
from bs4 import BeautifulSoup
import json, time, os, re

BASE_URL = "https://obchod.fimas.cz"

START_URLS = [
    BASE_URL + "/BRZDY-NAPRAVY-VZDUCH-c2_0_1.htm",
    BASE_URL + "/-c85_0_1.htm",
    BASE_URL + "/ADR-nahradni-dily-c23_0_1.htm",
    BASE_URL + "/FAD-napravy-c79_0_1.htm",
    BASE_URL + "/oblozeni-brzdy-BPW-AGRO-c70_0_1.htm",
    BASE_URL + "/VZDUCHOVE-BRZDY-c61_0_1.htm",
    BASE_URL + "/ZVEDAK-HYDRAULICKY-c9_0_1.htm",
    BASE_URL + "/NABOJ-KOLA-c43_0_1.htm",
    BASE_URL + "/POUZDRA-c1_0_1.htm",
    BASE_URL + "/PERO-LISTOVE-c5_0_1.htm",
    BASE_URL + "/DISK-KOLA-c7_0_1.htm",
]

# Robot smí navštívit jen URL obsahující některý z těchto řetězců
POVOLENE = [
    '-c2_', '-c2-', '-c85', '-c23', '-c79', '-c70', '-c61',
    '-c9_', '-c9-', '-c43', '-c1_', '-c1-', '-c5_', '-c5-',
    '-c7_', '-c7-', '-c19',
    '-c3_', '-c3-', '-c4_', '-c4-', '-c6_', '-c6-',
    '-c8_', '-c8-', '-c10', '-c11', '-c14', '-c15', '-c16',
    '-c17', '-c18', '-c20', '-c21', '-c22', '-c24', '-c25',
    '-c26', '-c27', '-c28', '-c29', '-c30',
    '-c40', '-c41', '-c42', '-c44', '-c45', '-c46', '-c47',
    '-c48', '-c49', '-c50', '-c51', '-c52', '-c53', '-c54',
    '-c55', '-c56', '-c57', '-c58', '-c59', '-c60',
    '-c62', '-c63', '-c64', '-c65', '-c66', '-c67', '-c68',
    '-c69', '-c71', '-c72', '-c73', '-c74', '-c75', '-c76',
    '-c77', '-c78', '-c80', '-c81', '-c82',
    '-c100', '-c101', '-c102', '-c103', '-c104', '-c105',
    '-c106', '-c107', '-c108', '-c109', '-c110',
    '-c285', '-c286', '-c287', '-c311', '-c312', '-c313',
    '-c402', '-c427', '-c515', '-c597', '-c719', '-c720',
    '?strana=',
]

CATEGORY_MAP = {
    'brzdov\u00e9 oblo\u017een\u00ed': 'brzdove-oblozeni', 'oblo\u017een\u00ed brzdy': 'brzdove-oblozeni',
    'brzdov\u00fd v\u00e1lec': 'brzdovy-valec', 'v\u00e1lec brzdy': 'brzdovy-valec',
    'v\u00e1lce cz': 'brzdovy-valec', 'membr\u00e1nov\u00e9': 'brzdovy-valec',
    'buben brzdy s n\u00e1bojem': 'buben-s-nabojem',
    'buben brzdy': 'buben-brzdy', 'buben': 'buben-brzdy',
    '\u010delist brzdy': 'celist-brzdy',
    'kl\u00ed\u010d brzdy': 'klic-brzdy', 'p\u00e1ka kl\u00ed\u010de': 'paka-klice',
    'brzda ru\u010dn\u00ed': 'brzda-rucni',
    'membr\u00e1ny do v\u00e1lc\u016f': 'membrany-valcu', 'membr\u00e1ny': 'membrany-valcu',
    'n\u00e1hradn\u00ed d\u00edly v\u00e1lc\u016f': 'nd-valcu',
    'n\u00e1boj kola': 'naboj-kola', 'n\u00e1boj': 'naboj-kola',
    '\u010dep kola': 'cep-kola',
    '\u0161rouby kola': 'srouby-kola', 'matice kola': 'srouby-kola',
    'disk kola': 'disk-kola', 'disky': 'disk-kola',
    'pero listov\u00e9': 'pero-listove', 'pera listov\u00e1': 'pero-listove',
    't\u0159men pera': 'trmen-pera',
    '\u010depy': 'cepy-pouzdra', 'pouzdra': 'cepy-pouzdra', 'krou\u017eky': 'cepy-pouzdra',
    'ta\u017en\u00e1 oj': 'tazna-oj', 'oko ta\u017en\u00e9 oje': 'oko-tazne-oje',
    'zved\u00e1k hydraulick\u00fd': 'hydraul-zvedaky', 'zved\u00e1ky': 'hydraul-zvedaky',
    'man\u017eety': 'manzety', 'ulo\u017een\u00ed zved\u00e1k\u016f': 'ulozeni-zvedaku',
    'vzduchov\u00e9 brzdy': 'ventily-brzd',
    'vzduchojemy': 'vzduchojemy', 'rozvad\u011b\u010d': 'rozvadece',
    'blatn\u00edky': 'blatniky', 'bo\u010dnice': 'bocnice',
    'adr': 'buben-brzdy', 'colaert': 'buben-brzdy',
    'fad': 'buben-brzdy', 'bpw': 'brzdove-oblozeni',
}

def map_category(h1):
    t = h1.lower().strip()
    if t in CATEGORY_MAP: return CATEGORY_MAP[t]
    for k, v in CATEGORY_MAP.items():
        if k in t: return v
    return re.sub(r'[^a-z0-9]+', '-',
        t.replace('\u00e1','a').replace('\u00e9','e').replace('\u00ed','i')
        .replace('\u00f3','o').replace('\u00fa','u').replace('\u016f','u')
        .replace('\u00fd','y').replace('\u017e','z').replace('\u0161','s')
        .replace('\u010d','c').replace('\u0159','r').replace('\u010f','d')
        .replace('\u0165','t').replace('\u0148','n').replace('\u011b','e')
    ).strip('-')

print("=" * 60)
print("  ROBOT D\u00cdLY NA N\u00c1PRAVY")
print("=" * 60)

h = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
queue = START_URLS.copy()
visited = set()
products = {}
pages = 0
errors = 0

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

        # Debug prvnich 3 stranek
        if pages <= 3:
            cls = set()
            for d in soup.find_all('div', class_=True):
                for c in d.get('class', []): cls.add(c)
            print(f"      Classes: {sorted(cls)[:20]}")
            h1 = soup.find('h1')
            print(f"      H1: {h1.text.strip()[:50] if h1 else 'NONE'}")

        # Kategorie
        h1 = soup.find('h1') or soup.find('h2')
        cat_raw = h1.text.strip() if h1 else "Ostatn\u00ed"
        cat_id = map_category(cat_raw)

        # Produkty - vice selektoru
        prods = soup.find_all('div', class_='product')
        if not prods:
            prods = soup.find_all('div', class_=re.compile(r'^product', re.I))

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

            sy = p.find(class_='stock_yes')
            stock = 'skladem' if sy else 'na-dotaz'

            if link not in products:
                products[link] = {
                    "id": str(len(products)+1),
                    "name": name, "subtitle": subtitle,
                    "category": cat_id, "stock": stock, "url": link
                }

        if len(prods) > 0:
            print(f"      {len(prods)} prod, cat: {cat_id}")

        # Dalsi odkazy
        new = 0
        for a in soup.find_all('a', href=True):
            hr = a['href']
            if any(k in hr for k in POVOLENE) and '.htm' in hr:
                full = hr if hr.startswith('http') else BASE_URL + ('' if hr.startswith('/') else '/') + hr
                if full not in visited and full not in queue:
                    queue.append(full)
                    new += 1
        if new: print(f"      +{new} links")

        time.sleep(0.3)

    except Exception as e:
        print(f"      ERROR: {e}")
        errors += 1

# Ulozeni
result = list(products.values())
for i, p in enumerate(result, 1): p['id'] = str(i)

stats = {}
for p in result:
    stats[p['category']] = stats.get(p['category'], 0) + 1

path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data.json')
with open(path, 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=4)

print()
print("=" * 60)
print(f"  HOTOVO! {len(result)} produktu, {pages} stranek, {errors} chyb")
for c, n in sorted(stats.items(), key=lambda x: -x[1]):
    print(f"  {c:30s} {n:4d}")
print("=" * 60)
