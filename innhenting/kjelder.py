"""Éin funksjon per fordelsprogram. Kvar funksjon returnerer ei liste med tilbod.
Feilar ein kjelde, held bygg.py fram med dei førre tilboda for det programmet."""
import re
from felles import hent, suppe, meta, h1, tilbod, gjett_kategori

DP_KAT = {"Restaurant":"Mat og drikke","Kafé":"Mat og drikke","Spisesteder":"Mat og drikke","Fastfood":"Mat og drikke",
  "Hotell i Norge":"Hotell og reise","Hotell i Europa":"Hotell og reise","Hotell i Verden":"Hotell og reise","Ferie":"Hotell og reise",
  "Cruisereiser":"Hotell og reise","Spesialreiser":"Hotell og reise","Leiebil":"Bil og transport","Bil":"Bil og transport",
  "Hus og hjem":"Bustad og hjem","Håndverk":"Bustad og hjem","Opplevelser":"Opplevingar","Underholdning":"Opplevingar",
  "Fornøyelsespark":"Opplevingar","Bowling":"Opplevingar","Kurs":"Opplevingar","Kultur":"Kultur","Treningssenter":"Sport og trening",
  "Hud og kroppspleie":"Helse og velvære","SPA og Massasje":"Helse og velvære"}

def dealpass():
    ut, o = [], 0
    while True:
        deals = hent(f"https://tfbank.dealpass.no/ajax/deals?offset={o}&limit=50").json().get("deals") or []
        if not deals: return ut
        for d in deals:
            s = d.get("supplier") or {}
            v = max(float(d["discount"].get(k) or 0) for k in ("basic", "premium", "platinum"))
            kat = next((DP_KAT[c["name"]] for c in d.get("categories") or [] if c["name"] in DP_KAT), "Handel")
            r = tilbod("dealpass", d["name"], f"{int(v)} % rabatt" if 0 < v < 100 else d["name"], kat=kat, verdi=int(v) if 0 < v < 100 else None)
            if d.get("expires"): r["gyldig_til"] = d["expires"][:10]
            ut.append(r)
        o += 50

OBOS_KAT = ["reise","okonomi","bolig","kultur","abonnementstjenester","sport","transport","annet","fornoyelsesparker","idrett"]
def obos():
    ut, sett = [], set()
    for k in OBOS_KAT:
        s = suppe(f"https://www.obos.no/medlem/medlemsfordeler/kategori/{k}")
        for a in s.select('a[href*="/medlem/medlemsfordeler/"]'):
            href = a.get("href", "")
            if "/kategori/" in href or href.rstrip("/").endswith("medlemsfordeler") or href in sett: continue
            delar = [t for t in a.stripped_strings]
            if len(delar) < 2: continue
            sett.add(href)
            tekst = " ".join(delar[1:])
            ses = next((x for x in ("Stengt for sesongen", "Utsolgt") if x in tekst), None)
            ut.append(tilbod("obos", delar[0], tekst.replace(ses or "", ""), sesong=ses))
    return ut

def bate():
    s = suppe("https://bate.no/sidekart")
    lenkjer = sorted({a["href"] for a in s.select('a[href^="/fordeler/"]') if a["href"].count("/") == 2})
    ut = []
    for l in lenkjer:
        p = suppe("https://bate.no" + l)
        namn = re.sub(r"^[^\wÆØÅæøå]+|^(Kampanje|Medlemsdager)\s*\|?\s*", "", h1(p)).strip(" |")
        ut.append(tilbod("bate", namn or l.split("/")[-1], meta(p), stad="Rogaland"))
    return ut

def bob():
    xml = hent("https://www.bob.no/sitemap.xml").text
    urls = [u for u in re.findall(r"<loc>([^<]+)</loc>", xml) if re.search(r"/medlem-og-beboer/medlemsfordeler/[^/]+/$", u)]
    ut = []
    for u in urls:
        p = suppe(u)
        ut.append(tilbod("bob-medlem", h1(p) or u.rstrip("/").split("/")[-1], meta(p), stad="Vestland"))
    return ut

def lofavor():
    s = suppe("https://www.lofavor.no/")
    urls = sorted({a["href"] for a in s.select("a[href]") if re.search(r"lofavor\.no/(ferie-og-[a-z]+|hus-og-hjem|bank|juridisk)/", a["href"])})
    ut = []
    for u in urls:
        p = suppe(u)
        ut.append(tilbod("lofavor", h1(p).replace("LOfavør", "").strip() or u.split("/")[-1], meta(p)))
    return ut

def nsf():
    ut = []
    for u in ["https://www.nsf.no/forsikring-og-medlemsfordeler/rabattavtaler", "https://www.nsf.no/hoteller-og-hytter"]:
        s = suppe(u)
        for h in s.select("main h3, main h2"):
            p = h.find_next("p")
            namn = h.get_text(" ", strip=True)
            if p and len(namn) < 60 and not namn.lower().startswith(("hvilke", "få siste")):
                ut.append(tilbod("nsf", namn, p.get_text(" ", strip=True).replace("Logg inn på nsf.no for å få rabatt.", "").replace("Logg inn på nsf.no for å se rabattkoden.", "")))
    return ut

# Program som berre kan hentast med nettlesar (sida blir bygd med JavaScript) eller som ikkje har
# offentlege lister. Desse er oppdaterte for hand 24.11.2026 og blir verande som dei er til vi lagar
# ei betre løysing: NAF, Aftenbladet Fordel, Spenn, SAS EuroBonus Mastercard, Montér Klubb.
KJELDER = {"dealpass": dealpass, "obos": obos, "bate": bate, "bob-medlem": bob, "lofavor": lofavor, "nsf": nsf}
