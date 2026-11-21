#!/usr/bin/env python3
"""
calc.py — Calculatrice live pour Termux
Ctrl+K pour ouvrir depuis .bashrc
"""

import ast
import curses
import operator
import math
import re
from collections import deque
import os
os.environ.setdefault("ESCDELAY", "25")

# ─── Conversions disponibles ───────────────────────────────────────────────
CONVERSIONS = {
    # Distance
    "km_miles":   ("km",   "miles",  lambda x: x * 0.621371),
    "miles_km":   ("miles","km",     lambda x: x * 1.60934),
    "m_ft":       ("m",    "ft",     lambda x: x * 3.28084),
    "ft_m":       ("ft",   "m",      lambda x: x / 3.28084),
    "cm_inch":    ("cm",   "inch",   lambda x: x / 2.54),
    "inch_cm":    ("inch", "cm",     lambda x: x * 2.54),
    # Température
    "c_f":        ("°C",   "°F",     lambda x: x * 9/5 + 32),
    "f_c":        ("°F",   "°C",     lambda x: (x - 32) * 5/9),
    "c_k":        ("°C",   "K",      lambda x: x + 273.15),
    # Poids
    "kg_lbs":     ("kg",   "lbs",    lambda x: x * 2.20462),
    "lbs_kg":     ("lbs",  "kg",     lambda x: x / 2.20462),
    "g_oz":       ("g",    "oz",     lambda x: x / 28.3495),
    # Vitesse
    "kmh_mph":    ("km/h", "mph",    lambda x: x * 0.621371),
    "mph_kmh":    ("mph",  "km/h",   lambda x: x * 1.60934),
    # Volume
    "l_gal":      ("L",    "gal",    lambda x: x * 0.264172),
    "gal_l":      ("gal",  "L",      lambda x: x / 0.264172),
}

# ─── Contexte mathématique sécurisé ────────────────────────────────────────
SAFE_MATH = {
    "sqrt": math.sqrt, "cbrt": lambda x: x**(1/3),
    "sin":  math.sin,  "cos":  math.cos,  "tan": math.tan,
    "asin": math.asin, "acos": math.acos, "atan": math.atan,
    "log":  math.log,  "log2": math.log2, "log10": math.log10,
    "exp":  math.exp,  "abs":  abs,       "round": round,
    "floor":math.floor,"ceil": math.ceil, "pow":   pow,
    "pi":   math.pi,   "e":    math.e,    "tau":   math.tau,
    "inf":  math.inf,
}

# ─── Évaluation ────────────────────────────────────────────────────────────
def try_conversion(expr):
    """Détecte ex: '100 km to miles' ou '37 c to f'"""
    expr = expr.strip().lower()
    patterns = [
        (r"([\d.]+)\s*km\s*(to|en|->)\s*miles?",   "km_miles"),
        (r"([\d.]+)\s*miles?\s*(to|en|->)\s*km",    "miles_km"),
        (r"([\d.]+)\s*m\s*(to|en|->)\s*ft",         "m_ft"),
        (r"([\d.]+)\s*ft\s*(to|en|->)\s*m",         "ft_m"),
        (r"([\d.]+)\s*cm\s*(to|en|->)\s*inch",      "cm_inch"),
        (r"([\d.]+)\s*inch\s*(to|en|->)\s*cm",      "inch_cm"),
        (r"([\d.]+)\s*°?c\s*(to|en|->)\s*°?f",      "c_f"),
        (r"([\d.]+)\s*°?f\s*(to|en|->)\s*°?c",      "f_c"),
        (r"([\d.]+)\s*°?c\s*(to|en|->)\s*k",        "c_k"),
        (r"([\d.]+)\s*kg\s*(to|en|->)\s*lbs?",      "kg_lbs"),
        (r"([\d.]+)\s*lbs?\s*(to|en|->)\s*kg",      "lbs_kg"),
        (r"([\d.]+)\s*g\s*(to|en|->)\s*oz",         "g_oz"),
        (r"([\d.]+)\s*km/?h\s*(to|en|->)\s*mph",    "kmh_mph"),
        (r"([\d.]+)\s*mph\s*(to|en|->)\s*km/?h",    "mph_kmh"),
        (r"([\d.]+)\s*l\s*(to|en|->)\s*gal",        "l_gal"),
        (r"([\d.]+)\s*gal\s*(to|en|->)\s*l",        "gal_l"),
    ]
    for pattern, key in patterns:
        m = re.match(pattern, expr)
        if m:
            val = float(m.group(1))
            c = CONVERSIONS[key]
            result = c[2](val)
            return f"{val} {c[0]}  =  {smart_format(result)} {c[1]}"
    return None

def smart_format(n):
    """Formate intelligemment un nombre."""
    if isinstance(n, complex):
        return str(n)
    if n == int(n) and abs(n) < 1e15:
        return str(int(n))
    # Arrondi propre
    formatted = f"{n:.10g}"
    return formatted

# ─── Le Gardien ────────────────────────────────────────────────────────────
class Interdit(Exception):
    pass

BIN_OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
           ast.Div: operator.truediv, ast.FloorDiv: operator.floordiv,
           ast.Mod: operator.mod, ast.Pow: operator.pow}
UN_OPS = {ast.UAdd: operator.pos, ast.USub: operator.neg}

def gardien_eval(expr):
    """Évalue seulement ce qui est autorisé. Jamais de eval()."""
    if len(expr) > 200:
        raise Interdit("trop long")
    tree = ast.parse(expr, mode="eval")

    def walk(n):
        if isinstance(n, ast.Expression):
            return walk(n.body)
        if isinstance(n, ast.Constant) and type(n.value) in (int, float, complex):
            return n.value
        if isinstance(n, ast.Name):
            if n.id.startswith("_"):
                raise Interdit("interdit")
            if n.id in SAFE_MATH:
                return SAFE_MATH[n.id]
            raise ValueError("inconnu")
        if isinstance(n, ast.UnaryOp) and type(n.op) in UN_OPS:
            return UN_OPS[type(n.op)](walk(n.operand))
        if isinstance(n, ast.BinOp) and type(n.op) in BIN_OPS:
            a, b = walk(n.left), walk(n.right)
            if isinstance(n.op, ast.Pow) and abs(b) > 1000:
                raise Interdit("trop grand")
            return BIN_OPS[type(n.op)](a, b)
        if isinstance(n, ast.Call) and not n.keywords:
            f = walk(n.func)
            if not callable(f):
                raise ValueError("pas une fonction")
            args = [walk(a) for a in n.args]
            if f is SAFE_MATH.get("fact") and args and args[0] > 500:
                raise Interdit("trop grand")
            return f(*args)
        raise Interdit("interdit")

    return walk(tree)

def try_percent(expr):
    """Pourcentages boutique."""
    e = expr.strip().lower().replace(",", ".")
    num = r"(\d+(?:\.\d+)?)"
    m = re.fullmatch(rf"prix\s*{num}\s*b[ée]n[ée]fice\s*{num}\s*%", e)
    if m:
        prix, pct = float(m.group(1)), float(m.group(2))
        gain = prix * pct / 100
        return f"vente {smart_format(prix + gain)}  (gain {smart_format(gain)})"
    m = re.fullmatch(rf"{num}\s*([+-])\s*{num}\s*%", e)
    if m:
        base, op, pct = float(m.group(1)), m.group(2), float(m.group(3))
        delta = base * pct / 100
        return smart_format(base + delta if op == "+" else base - delta)
    m = re.fullmatch(rf"{num}\s*%\s*(?:de|of)\s*{num}", e)
    if m:
        return smart_format(float(m.group(1)) * float(m.group(2)) / 100)
    return None

def evaluate(expr):
    """Évalue une expression mathématique."""
    if not expr.strip():
        return ""
    # Tenter conversion d'abord
    conv = try_conversion(expr)
    if conv:
        return conv
    pct = try_percent(expr)
    if pct:
        return pct
    # Remplacements courants
    cleaned = expr.strip()
    cleaned = cleaned.replace("^", "**")
    cleaned = re.sub(r'(\d)\s*\(', r'\1*(', cleaned)   # 2(3) → 2*(3)
    cleaned = re.sub(r'\bmod\b', '%', cleaned)
    try:
        result = gardien_eval(cleaned)
        if isinstance(result, (int, float, complex)):
            return smart_format(result)
        return ""
    except Interdit:
        return "⚠  Interdit"
    except ZeroDivisionError:
        return "⚠  Division par zéro"
    except Exception:
        return ""

# ─── Interface curses ───────────────────────────────────────────────────────
def draw_ui(stdscr):
    curses.curs_set(1)
    curses.use_default_colors()

    # Couleurs
    curses.init_pair(1, curses.COLOR_CYAN,    -1)   # titre
    curses.init_pair(2, curses.COLOR_GREEN,   -1)   # résultat
    curses.init_pair(3, curses.COLOR_YELLOW,  -1)   # historique valeur
    curses.init_pair(4, curses.COLOR_WHITE,   -1)   # texte normal
    curses.init_pair(5, curses.COLOR_RED,     -1)   # erreur
    curses.init_pair(6, curses.COLOR_BLACK,   curses.COLOR_CYAN)  # header bg

    history = deque(maxlen=8)   # derniers calculs
    expr = ""
    cursor_pos = len(expr)

    HELP_LINES = [
        "  sqrt(x)  sin(x)  cos(x)  log(x)  log2(x)",
        "  pi  e  tau  abs(x)  round(x)  x**n",
        "  100 km to miles  |  37 c to f  |  70 kg to lbs",
        "  prix 5000 benefice 20%  |  20% de 5000",
    ]

    while True:
        stdscr.erase()
        max_y, max_x = stdscr.getmaxyx()
        W = min(max_x, 56)
        start_x = (max_x - W) // 2
        row = 1

        # ── Header ──────────────────────────────────────────────
        header = " ⚡ CALC — Termux Live Calculator "
        pad = (W - len(header)) // 2
        try:
            stdscr.addstr(row, start_x, "─" * W, curses.color_pair(1))
            stdscr.addstr(row + 1, start_x + pad, header, curses.color_pair(6) | curses.A_BOLD)
            stdscr.addstr(row + 2, start_x, "─" * W, curses.color_pair(1))
        except curses.error:
            pass
        row += 4

        # ── Zone de saisie ──────────────────────────────────────
        prompt = " › "
        try:
            stdscr.addstr(row, start_x, prompt, curses.color_pair(1) | curses.A_BOLD)
            stdscr.addstr(row, start_x + len(prompt), expr + " " * (W - len(prompt) - len(expr) - 1),
                          curses.color_pair(4) | curses.A_BOLD)
        except curses.error:
            pass
        row += 1

        # ── Ligne de séparation ─────────────────────────────────
        try:
            stdscr.addstr(row, start_x, "·" * W, curses.color_pair(1))
        except curses.error:
            pass
        row += 1

        # ── Résultat live ───────────────────────────────────────
        result = evaluate(expr)
        if result:
            eq_line = f"  = {result}"
            color = curses.color_pair(2) | curses.A_BOLD
            if "⚠" in result:
                color = curses.color_pair(5) | curses.A_BOLD
            try:
                stdscr.addstr(row, start_x, eq_line[:W], color)
            except curses.error:
                pass
        else:
            try:
                stdscr.addstr(row, start_x, "  ...", curses.color_pair(4))
            except curses.error:
                pass
        row += 2

        # ── Historique ──────────────────────────────────────────
        if history:
            try:
                stdscr.addstr(row, start_x, " Historique:", curses.color_pair(1))
            except curses.error:
                pass
            row += 1
            for (old_expr, old_res) in reversed(list(history)):
                line = f"  {old_expr[:20]:<20}  =  {old_res}"
                try:
                    stdscr.addstr(row, start_x, line[:W], curses.color_pair(3))
                except curses.error:
                    pass
                row += 1
            row += 1

        # ── Aide rapide ─────────────────────────────────────────
        try:
            stdscr.addstr(row, start_x, "─" * W, curses.color_pair(1))
            row += 1
            for line in HELP_LINES:
                stdscr.addstr(row, start_x, line[:W], curses.color_pair(4))
                row += 1
            stdscr.addstr(row, start_x, "─" * W, curses.color_pair(1))
            row += 1
            stdscr.addstr(row, start_x,
                          "  [Enter] sauvegarder  [Esc] quitter  [Ctrl+L] effacer",
                          curses.color_pair(4))
        except curses.error:
            pass

        # ── Positionner le curseur dans la saisie ───────────────
        cursor_col = start_x + len(prompt) + cursor_pos
        try:
            stdscr.move(5, min(cursor_col, max_x - 1))
        except curses.error:
            pass

        stdscr.refresh()

        # ── Lecture touche ──────────────────────────────────────
        key = stdscr.get_wch()

        if key in (27, "\x1b"):                          # Escape → quitter
            break
        elif key == "\x0c":                    # Ctrl+L → effacer
            expr = ""
            cursor_pos = 0
        elif key in (curses.KEY_BACKSPACE, "\x7f", "\b"):
            if cursor_pos > 0:
                expr = expr[:cursor_pos-1] + expr[cursor_pos:]
                cursor_pos -= 1
        elif key == curses.KEY_DC:             # Suppr
            if cursor_pos < len(expr):
                expr = expr[:cursor_pos] + expr[cursor_pos+1:]
        elif key == curses.KEY_LEFT:
            if cursor_pos > 0:
                cursor_pos -= 1
        elif key == curses.KEY_RIGHT:
            if cursor_pos < len(expr):
                cursor_pos += 1
        elif key == curses.KEY_HOME:
            cursor_pos = 0
        elif key == curses.KEY_END:
            cursor_pos = len(expr)
        elif key in ("\n", "\r"):              # Enter → sauvegarder dans historique
            if expr.strip() and result and "⚠" not in result:
                history.append((expr.strip(), result))
            expr = ""
            cursor_pos = 0
        elif isinstance(key, str) and key.isprintable():
            expr = expr[:cursor_pos] + key + expr[cursor_pos:]
            cursor_pos += 1


def main():
    curses.wrapper(draw_ui)


if __name__ == "__main__":
    main()
