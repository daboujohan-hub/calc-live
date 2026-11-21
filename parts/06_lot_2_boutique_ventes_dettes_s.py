# ─── Lot 2 : boutique (ventes, dettes, stock, rappels, facture) ────────────
from datetime import datetime
DATA_FILE = os.path.expanduser("~/.calc_data.json")
HIST_FILE = os.path.expanduser("~/calc_historique.txt")
FACT_DIR = os.path.expanduser("~/calc_factures")

def _load():
    try:
        with open(DATA_FILE) as f:
            d = json.load(f)
    except Exception:
        d = {}
    for k, v in (("ventes", []), ("dettes", {}), ("stock", {}), ("rappels", [])):
        d.setdefault(k, v)
    return d

def _save(d):
    with open(DATA_FILE, "w") as f:
        json.dump(d, f, ensure_ascii=False)

def _lot2(expr, apply=False):
    e = expr.strip().lower()
    num = r"(\d+(?:\.\d+)?)"
    nom = r"(\w[\w'-]*)"
    qte = rf"(?:\s*[x*]\s*{num})?"
    today = datetime.now().strftime("%Y-%m-%d")

    # vente riz 2500 x3
    m = re.fullmatch(rf"vente\s+{nom}\s+{num}{qte}", e)
    if m:
        n, pr = m.group(1), float(m.group(2))
        q = float(m.group(3)) if m.group(3) else 1.0
        txt = f"{n} {smart_format(pr)} x{smart_format(q)} = {smart_format(pr * q)}"
        if not apply:
            return "Entrée pour enregistrer : " + txt
        d = _load()
        d["ventes"].append({"d": today, "n": n, "p": pr, "q": q})
        if n in d["stock"]:
            d["stock"][n] = max(0, d["stock"][n] - q)
        _save(d)
        return "vente enregistrée : " + txt
    if e == "ventes":
        v = _load()["ventes"]
        jour = [x for x in v if x["d"] == today]
        t = sum(x["p"] * x["q"] for x in jour)
        tot = sum(x["p"] * x["q"] for x in v)
        return f"aujourd'hui {smart_format(t)} ({len(jour)} ventes) | total {smart_format(tot)}"

    # dette awa 5000   /   dette awa -2000 (paiement)
    m = re.fullmatch(rf"dette\s+{nom}\s+(-?\d+(?:\.\d+)?)", e)
    if m:
        n, v = m.group(1), float(m.group(2))
        if v == 0:
            return None
        if not apply:
            return f"Entrée pour noter : {n} {'+' if v > 0 else '-'}{smart_format(abs(v))}"
        d = _load()
        x = d["dettes"].get(n, 0) + v
        if x <= 0:
            d["dettes"].pop(n, None)
            msg = f"{n} ne doit plus rien"
        else:
            d["dettes"][n] = x
            msg = f"{n} doit {smart_format(x)}"
        _save(d)
        return msg
    if e == "dettes":
        dd = _load()["dettes"]
        if not dd:
            return "aucune dette"
        liste = ", ".join(f"{n} {smart_format(x)}" for n, x in sorted(dd.items(), key=lambda t: -t[1]))
        return f"total {smart_format(sum(dd.values()))} : {liste}"

    # stock riz +10  /  stock riz -2  /  stock riz  /  stock
    m = re.fullmatch(rf"stock\s+{nom}\s*([+-])\s*{num}", e)
    if m:
        n, sg, v = m.group(1), m.group(2), float(m.group(3))
        d = _load()
        x = d["stock"].get(n, 0) + (v if sg == "+" else -v)
        if x < 0:
            return "⚠  stock insuffisant"
        if not apply:
            return f"Entrée : {n} passe à {smart_format(x)}"
        d["stock"][n] = x
        _save(d)
        return f"stock {n} : {smart_format(x)}"
    m = re.fullmatch(rf"stock\s+{nom}", e)
    if m:
        x = _load()["stock"].get(m.group(1))
        return "inconnu" if x is None else f"{m.group(1)} : {smart_format(x)}"
    if e == "stock":
        st = _load()["stock"]
        return ", ".join(f"{n} {smart_format(x)}" for n, x in sorted(st.items())) or "stock vide"

    # rappel 17h appeler client  /  rappel 17h30 ...  /  rappels
    m = re.fullmatch(r"rappel\s+(\d{1,2})h(\d{2})?\s+(.+)", e)
    if m:
        h, mi = int(m.group(1)), int(m.group(2) or 0)
        if h > 23 or mi > 59:
            return "⚠  heure invalide"
        hh = f"{h:02d}:{mi:02d}"
        if not apply:
            return f"Entrée pour noter : {hh} {m.group(3)}"
        d = _load()
        d["rappels"].append({"d": today, "h": hh, "t": m.group(3)})
        _save(d)
        return f"rappel noté : {hh} {m.group(3)}"
    if e == "rappels":
        r = sorted((x["h"], x["t"]) for x in _load()["rappels"] if x["d"] == today)
        return " ; ".join(f"{h} {t}" for h, t in r) or "aucun rappel aujourd'hui"

    # facture riz 2500 x3, huile 1000 x2
    m = re.fullmatch(r"facture\s+(.+)", e)
    if m:
        lignes = []
        for part in re.split(r"[,;]", m.group(1)):
            mm = re.fullmatch(rf"\s*{nom}\s+{num}{qte}\s*", part)
            if not mm:
                return None
            pr = float(mm.group(2))
            q = float(mm.group(3)) if mm.group(3) else 1.0
            lignes.append((mm.group(1), pr, q))
        total = sum(pr * q for _, pr, q in lignes)
        if not apply:
            return f"total {smart_format(total)} ({len(lignes)} articles) - Entrée pour créer"
        os.makedirs(FACT_DIR, exist_ok=True)
        now = datetime.now()
        path = os.path.join(FACT_DIR, f"facture_{now:%Y%m%d_%H%M%S}.txt")
        with open(path, "w") as f:
            f.write(f"FACTURE  {now:%d/%m/%Y %H:%M}\n" + "-" * 34 + "\n")
            for n, pr, q in lignes:
                f.write(f"{n.capitalize():<12}{smart_format(pr):>8} x{smart_format(q):<4}{smart_format(pr * q):>8}\n")
            f.write("-" * 34 + f"\nTOTAL{smart_format(total):>29}\n")
        return f"facture créée : {os.path.basename(path)}"
    return None

def try_lot2(expr, apply=False):
    try:
        return _lot2(expr, apply)
    except Exception:
        return "⚠  erreur d'enregistrement" if apply else None

