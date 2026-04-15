# dilynanapravy.cz

Specializovaný katalog náhradních dílů na nápravy pro zemědělské a automobilové přívěsy.

**FIMAS s.r.o. Nové Veselí**

## Nasazení

Aplikace je single-file HTML, deploy přes Vercel:

1. Push na GitHub
2. Připojit repozitář ve Vercel
3. DNS nasměrovat na Vercel (dilynanapravy.cz)

## Data

Produktová data se načítají z `data.json`. Soubor může být generován automaticky pomocí `robot.py` (scraping z obchod.fimas.cz).

Formát záznamu:
```json
{
  "id": "1",
  "name": "buben brzdy 300x60",
  "subtitle": "ADR, 440230511242",
  "category": "buben-brzdy",
  "stock": "skladem",
  "url": "https://obchod.fimas.cz/..."
}
```

Kategorie: `brzdove-oblozeni`, `brzdovy-valec`, `buben-brzdy`, `buben-s-nabojem`, `celist-brzdy`, `klic-brzdy`, `paka-klice`, `brzda-rucni`, `membrany-valcu`, `nd-valcu`, `naboj-kola`, `cep-kola`, `srouby-kola`, `disk-kola`, `pero-listove`, `trmen-pera`, `cepy-pouzdra`, `tazna-oj`, `oko-tazne-oje`, `hydraul-zvedaky`, `manzety`, `ulozeni-zvedaku`, `ventily-brzd`, `vzduchojemy`, `rozvadece`, `blatniky`, `bocnice`
