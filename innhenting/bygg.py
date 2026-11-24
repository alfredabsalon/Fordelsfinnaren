"""Hentar tilbod frå alle kjeldene og skriv site/data.json.
Køyr:  python innhenting/bygg.py            (alle)
       python innhenting/bygg.py obos bate  (berre nokre)"""
import csv, json, re, sys, datetime, pathlib, traceback
from kjelder import KJELDER

ROT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROT / "site" / "data.json"
KMAP = {"Daglegvare":"Daglegvare","Drivstoff":"Bil og transport","Fly":"Hotell og reise","Hotell":"Hotell og reise",
        "Handel":"Handel","Bank og kort":"Bank og forsikring","Medlemskap":"Anna"}

def pid(namn, fast):
    return fast.get(namn) or re.sub(r"[^a-z0-9]+", "-", namn.lower()).strip("-")

def main(berre):
    gammal = json.loads(DATA.read_text(encoding="utf-8"))
    tilbod = [t for t in gammal["tilbod"] if not t.get("programniva")]
    status = gammal.get("status", {})
    idag = datetime.date.today().isoformat()
    for p, fn in KJELDER.items():
        if berre and p not in berre: continue
        try:
            nye = fn()
            if len(nye) < 3: raise ValueError(f"berre {len(nye)} tilbod, held på dei gamle")
            tilbod = [t for t in tilbod if t["p"] != p] + nye
            status[p] = {"henta": idag, "tal": len(nye), "ok": True}
            print(f"{p}: {len(nye)} tilbod")
        except Exception as e:
            status.setdefault(p, {})["ok"] = False
            status[p]["feil"] = str(e)[:200]
            print(f"{p}: FEIL, held på dei gamle tilboda ({e})"); traceback.print_exc()

    fast = {"Bank Norwegian Visa":"banknorwegian","re:member Reward":"remember","DealPass (TF Bank Mastercard)":"dealpass",
            "Instabank kredittkort":"instabank","LO Favør":"lofavor","NAF-medlemsfordelar":"naf","OBOS-medlem":"obos",
            "Norsk Sykepleierforbund (NSF)":"nsf","Aftenbladet Fordel":"aftenbladet-fordel","BOB-medlem":"bob-medlem",
            "Bate-medlem":"bate","Spenn":"spenn","SAS EuroBonus Mastercard":"sas-eurobonus-mastercard","Montér Klubb":"monter-klubb"}
    program = {}
    med_tilbod = {t["p"] for t in tilbod}
    for r in csv.DictReader(open(ROT / "innhenting" / "program.csv", encoding="utf-8"), delimiter=";"):
        i = pid(r["program"], fast)
        program[i] = {"namn": r["program"], "kat": r["kategori"], "eigar": r["eigar"], "kostnad": r["kostnad_a_bli_med"], "nettstad": r["nettstad"]}
        if i not in med_tilbod:
            tilbod.append({"p": i, "namn": r["program"], "kat": KMAP.get(r["kategori"], "Anna"), "tittel": r["hovudfordelar"], "sok": r["eigar"], "programniva": True})
    DATA.write_text(json.dumps({"oppdatert": idag, "status": status, "program": program, "tilbod": tilbod},
                               ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"Skreiv {len(tilbod)} rader for {len(program)} program")

if __name__ == "__main__":
    main(set(sys.argv[1:]))
