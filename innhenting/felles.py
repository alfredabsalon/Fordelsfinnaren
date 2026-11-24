"""Felles hjelpefunksjonar for innhentinga."""
import re, time, requests
from bs4 import BeautifulSoup

UA = {"User-Agent": "Fordelsfinnaren/1.0 (privat fordelsoversikt; hentar éin gong i døgnet)"}

def hent(url, **kw):
    time.sleep(1)  # ver snill mot nettsidene
    r = requests.get(url, headers=UA, timeout=30, **kw)
    r.raise_for_status()
    return r

def suppe(url):
    return BeautifulSoup(hent(url).text, "html.parser")

def prosent(tekst):
    """Største prosenttal i teksten, t.d. '15–30 % rabatt' -> 30."""
    tal = [int(x) for x in re.findall(r"(\d{1,3})\s*(?:%|prosent)", tekst or "")]
    for a, b in re.findall(r"(\d{1,3})\s*[–-]\s*(\d{1,3})\s*(?:%|prosent)", tekst or ""):
        tal.append(int(b))
    tal = [t for t in tal if 0 < t <= 100]
    return max(tal) if tal else None

def meta(s):
    m = s.find("meta", attrs={"name": "description"}) or s.find("meta", attrs={"property": "og:description"})
    return (m.get("content") or "").strip() if m else ""

def h1(s):
    return s.h1.get_text(" ", strip=True) if s.h1 else ""

KAT_ORD = [("Opplevingar", "fornøy|park|bad|bowling|paintball|escape|klatre|trampoline|akvari|opplev"),
           ("Kultur", "kino|teater|konsert|museum|scene|opera|festival|bok|lydbok"),
           ("Hotell og reise", "hotel|hotell|reise|cruise|fly|ferie|camping|hytte"),
           ("Bil og transport", "bil|dekk|drivstoff|lading|taxi|leigebil|leiebil|parkering"),
           ("Bank og forsikring", "bank|lån|forsikr|advokat|spare"),
           ("Bustad og hjem", "bolig|bustad|maling|kjøkken|interiør|møbel|straum|strøm|alarm|elektr|bygg"),
           ("Sport og trening", "sport|trening|fotball|ski|håndball|ishockey|sats"),
           ("Mat og drikke", "pizza|restaurant|mat|kafe|kafé"),
           ("Helse og velvære", "apotek|frisør|briller|hud|spa|optik")]

def gjett_kategori(tekst):
    t = (tekst or "").lower()
    for k, mønster in KAT_ORD:
        if re.search(mønster, t):
            return k
    return "Anna"

def tilbod(program, namn, tittel, kat=None, stad=None, verdi="auto", sesong=None):
    namn, tittel = namn.strip(), re.sub(r"\s+", " ", tittel or "").strip()
    v = prosent(tittel) if verdi == "auto" else verdi
    r = {"p": program, "namn": namn, "kat": kat or gjett_kategori(namn + " " + tittel), "tittel": tittel or namn}
    if v: r["verdi"] = v
    if stad: r["stad"] = stad
    if sesong: r["sesong"] = sesong
    return r
