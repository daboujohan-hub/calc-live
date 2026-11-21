# ─── Lot 1 : maths, degrés, devises, surface, monnaie ──────────────────────
import json
MODE = {"deg": False}
TAUX_FILE = os.path.expanduser("~/.calc_taux.json")
TAUX = {"cfa": 1.0, "eur": 655.957, "usd": 570.0}   # valeur de 1 unité en CFA
try:
    with open(TAUX_FILE) as _f:
        TAUX.update({k: float(v) for k, v in json.load(_f).items() if k in TAUX})
except Exception:
    pass

def _trig(f):
    return lambda x: f(math.radians(x)) if MODE["deg"] else f(x)

def _atrig(f):
    return lambda x: math.degrees(f(x)) if MODE["deg"] else f(x)

def _fact(x):
    if x != int(x) or not 0 <= x <= 170:
        raise ValueError("fact")
    return math.factorial(int(x))

def _pow(a, b):
    if abs(b) > 1000:
        raise Interdit("trop grand")
    return pow(a, b)

SAFE_MATH.update({
    "sin": _trig(math.sin), "cos": _trig(math.cos), "tan": _trig(math.tan),
    "asin": _atrig(math.asin), "acos": _atrig(math.acos), "atan": _atrig(math.atan),
    "sinh": math.sinh, "cosh": math.cosh, "tanh": math.tanh,
    "sind": lambda x: math.sin(math.radians(x)),
    "cosd": lambda x: math.cos(math.radians(x)),
    "tand": lambda x: math.tan(math.radians(x)),
    "rad": math.radians, "deg": math.degrees,
    "fact": _fact, "gcd": math.gcd, "lcm": math.lcm,
    "hypot": math.hypot, "max": max, "min": min, "pow": _pow,
})

DEVISES = {"cfa": "cfa", "fcfa": "cfa", "xof": "cfa", "eur": "eur", "euro": "eur",
           "euros": "eur", "usd": "usd", "dollar": "usd", "dollars": "usd"}
NOMS = {"cfa": "CFA", "eur": "EUR", "usd": "USD"}
COUPURES = [10000, 5000, 2000, 1000, 500, 250, 200, 100, 50, 25, 10, 5, 1]

def _lot1(expr, apply=False):
    e = expr.strip().lower().replace(",", ".")
    num = r"(\d+(?:\.\d+)?)"
    # mode degrés / radians
    m = re.fullmatch(r"mode\s*(deg|degres|degrés|rad|radians)", e)
    if m:
        deg = m.group(1).startswith("deg")
        if apply:
            MODE["deg"] = deg
            return "mode degrés activé" if deg else "mode radians activé"
        return "Entrée pour passer en " + ("degrés" if deg else "radians")
    # taux usd 600
    m = re.fullmatch(rf"taux\s*(usd|eur)\s*{num}", e)
    if m:
        v = float(m.group(2))
        if v <= 0:
            return "⚠  taux invalide"
        if apply:
            TAUX[m.group(1)] = v
            try:
                with open(TAUX_FILE, "w") as f:
                    json.dump(TAUX, f)
            except Exception:
                pass
            return f"taux enregistré : 1 {m.group(1).upper()} = {smart_format(v)} CFA"
        return f"Entrée pour fixer 1 {m.group(1).upper()} = {smart_format(v)} CFA"
    # 5000 cfa to eur
    d = "|".join(DEVISES)
    m = re.fullmatch(rf"{num}\s*({d})\s*(?:to|en|->)\s*({d})", e)
    if m:
        v, a, b = float(m.group(1)), DEVISES[m.group(2)], DEVISES[m.group(3)]
        res = v * TAUX[a] / TAUX[b]
        return f"{smart_format(v)} {NOMS[a]}  =  {smart_format(round(res, 2))} {NOMS[b]}"
    # surface 5x4
    m = re.fullmatch(rf"surface\s*{num}\s*[x*×]\s*{num}", e)
    if m:
        a, b = float(m.group(1)), float(m.group(2))
        return f"{smart_format(a * b)} m²  (périmètre {smart_format(2 * (a + b))} m)"
    # monnaie 10000 - 7500
    m = re.fullmatch(rf"monnaie\s*{num}\s*(?:-|à|pour)\s*{num}", e)
    if m:
        diff = float(m.group(1)) - float(m.group(2))
        if diff < 0:
            return f"⚠  il manque {smart_format(-diff)}"
        if diff == 0:
            return "rien à rendre"
        txt = f"rendre {smart_format(diff)}"
        if diff == int(diff):
            reste, parts = int(diff), []
            for c in COUPURES:
                q, reste = divmod(reste, c)
                if q:
                    parts.append(f"{q}x{c}")
            txt += "  (" + " + ".join(parts) + ")"
        return txt
    return None

def try_lot1(expr, apply=False):
    try:
        return _lot1(expr, apply)
    except Exception:
        return None

