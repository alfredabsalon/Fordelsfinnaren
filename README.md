# Fordelsfinnaren

Søk på ein stad eller ein butikk og sjå kva fordelsprogram som gir rabatt der.
Nettsida fungerer òg som app på mobilen (legg ho til på heimskjermen).

## Korleis det heng saman

- `site/` er sjølve appen: `index.html` og `data.json` med alle tilboda.
- `innhenting/kjelder.py` har éin funksjon per fordelsprogram som hentar tilboda frå nettsida til programmet.
- `innhenting/bygg.py` køyrer alle kjeldene og skriv `site/data.json`. Feilar ei kjelde, blir dei førre tilboda for det programmet verande.
- `innhenting/program.csv` er lista over alle program. Legg til ei rad her for å få med eit nytt program.
- `.github/workflows/oppdater.yml` køyrer innhentinga kvar natt og publiserer appen på GitHub Pages.

## Program som blir oppdaterte automatisk

DealPass, OBOS, Bate, BOB, LO Favør og NSF.

NAF, Aftenbladet Fordel, Spenn, SAS EuroBonus Mastercard og Montér Klubb er lagde inn for hand
(24.11.2026), fordi sidene deira blir bygde med JavaScript eller ikkje har offentlege lister.

## Køyre lokalt

```
pip install -r innhenting/requirements.txt
python innhenting/bygg.py          # alle kjelder
python innhenting/bygg.py obos     # berre éi
python -m http.server -d site 8000 # opne http://localhost:8000
```
