# ─── Lot 9 : boutons, LED, plot, état, progression, accueil ────────────────
import math, time, ast, datetime

ZONE_TOP = 15

_G = """
0=███|█ █|█ █|█ █|███
1= █ |██ | █ | █ |███
2=███|  █|███|█  |███
3=███|  █|███|  █|███
4=█ █|█ █|███|  █|  █
5=███|█  |███|  █|███
6=███|█  |███|█ █|███
7=███|  █|  █|  █|  █
8=███|█ █|███|█ █|███
9=███|█ █|███|  █|███
-=   |   |███|   |   
.=   |   |   |   | █ 
A= █ |█ █|███|█ █|█ █
B=██ |█ █|██ |█ █|██ 
O=███|█ █|█ █|█ █|███
U=█ █|█ █|█ █|█ █|███
D=██ |█ █|█ █|█ █|██ 
E=███|█  |██ |█  |███
V=█ █|█ █|█ █|█ █| █ 
L=█  |█  |█  |█  |███
S=███|█  |███|  █|███
"""
FONT = {" ": ["   "] * 5}
for _l in _G.strip("\n").split("\n"):
    FONT[_l[0]] = [r.ljust(3) for r in _l[2:].split("|")]

_BTNS = [("+", "+"), ("−", "-"), ("×", "*"), ("÷", "/"),
         ("(", "("), (")", ")"), ("%", "%"), ("⌫", None)]
_hot = {"row": -1, "cells": []}
_st = {"last": None, "lvl": 0.0}

def _hit(x, y):
    for y0, y1, x0, x1, v in _hot.get("zones", []):
        if y0 <= y <= y1 and x0 <= x < x1:
            return v
    if abs(y - _hot["row"]) <= 1:
        for x0, x1, v in _hot["cells"]:
            if x0 <= x < x1:
                return curses.KEY_BACKSPACE if v is None else v
    return None

_DBG = {"on": None, "t0": 0.0}

def _dbg(msg):
    try:
        f = os.path.expanduser("~/.calc_debug.log")
        if _DBG["on"] is None:
            _DBG["on"] = os.path.exists(os.path.expanduser("~/.calc_debug_on"))
            _DBG["t0"] = time.time()
            if _DBG["on"]:
                open(f, "w").close()
        if _DBG["on"]:
            with open(f, "a") as h:
                h.write("%7.3f %s\n" % (time.time() - _DBG["t0"], msg))
    except Exception:
        pass

def _kdesc(k):
    if isinstance(k, str):
        return "·" if k.isprintable() else repr(k)
    return str(k)

def set_tactile(cmd):
    on = (not _st.get("mouse")) if cmd == "tactile" else cmd.endswith("on")
    f = os.path.expanduser("~/.calc_souris")
    try:
        if on:
            open(f, "a").close()
            curses.mouseinterval(0)
            curses.mousemask(curses.BUTTON1_PRESSED)
        else:
            if os.path.exists(f):
                os.remove(f)
            curses.mousemask(0)
    except Exception:
        pass
    _st["mouse"] = on

class MouseProxy:
    def __init__(self, scr):
        self._s = scr
        MOUSE_ON = os.path.exists(os.path.expanduser("~/.calc_souris"))
        _st["mouse"] = MOUSE_ON
        if MOUSE_ON:
            try:
                curses.mouseinterval(0)
                curses.mousemask(curses.BUTTON1_PRESSED)
            except curses.error:
                pass
    def __getattr__(self, n):
        return getattr(self._s, n)
    def get_wch(self):
        while True:
            k = self._s.get_wch()
            _dbg("touche " + _kdesc(k))
            if k == curses.KEY_MOUSE:
                try:
                    _i, mx_, my_, _z, _b = curses.getmouse()
                except curses.error:
                    continue
                v = _hit(mx_, my_)
                if v is not None:
                    return v
                continue
            if k in (27, "\x1b"):
                seq = self._esc_tail()
                if seq is None:
                    return k
                _dbg("séquence ignorée après Échap : " + "".join(_kdesc(c) for c in seq))
                continue
            return k
    def _esc_tail(self):
        sc = self._s
        out = ""
        sc.timeout(30)
        try:
            while len(out) < 40:
                try:
                    c = sc.get_wch()
                except curses.error:
                    break
                if not isinstance(c, str):
                    continue
                out += c
                if len(out) == 1 and c not in "[O":
                    break
                if len(out) > 1 and "@" <= c <= "~":
                    break
        finally:
            sc.timeout(-1)
        return out or None
    def getch(self):
        while True:
            k = self._s.getch()
            if k == curses.KEY_MOUSE:
                try:
                    _i, mx_, my_, _z, _b = curses.getmouse()
                except curses.error:
                    continue
                v = _hit(mx_, my_)
                if v is not None:
                    return v if isinstance(v, int) else ord(v)
                continue
            return k

# ── évaluateur sûr (pour LED et plot) ──
def _fact_led(v):
    if v < 0 or v > 500 or int(v) != v:
        raise ValueError
    return math.factorial(int(v))

_F0 = {"sqrt": math.sqrt, "log": math.log, "log2": math.log2, "log10": math.log10,
       "exp": math.exp, "fact": _fact_led, "gcd": math.gcd, "lcm": math.lcm,
       "hypot": math.hypot, "max": max, "min": min, "abs": abs, "round": round}
_BIN = {ast.Add: lambda a, b: a + b, ast.Sub: lambda a, b: a - b,
        ast.Mult: lambda a, b: a * b, ast.Div: lambda a, b: a / b,
        ast.Mod: lambda a, b: a % b, ast.FloorDiv: lambda a, b: a // b}

def _ev(n, F, V):
    if isinstance(n, ast.Expression):
        return _ev(n.body, F, V)
    if isinstance(n, ast.Constant) and type(n.value) in (int, float):
        return n.value
    if isinstance(n, ast.Name) and n.id in V:
        return V[n.id]
    if isinstance(n, ast.UnaryOp) and isinstance(n.op, (ast.USub, ast.UAdd)):
        v = _ev(n.operand, F, V)
        return -v if isinstance(n.op, ast.USub) else v
    if isinstance(n, ast.BinOp):
        a = _ev(n.left, F, V); b = _ev(n.right, F, V)
        if isinstance(n.op, ast.Pow):
            if abs(b) > 300 or abs(a) > 1e100:
                raise ValueError
            return a ** b
        f = _BIN.get(type(n.op))
        if f:
            return f(a, b)
    if (isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
            and n.func.id in F and not n.keywords):
        return F[n.func.id](*[_ev(a, F, V) for a in n.args])
    raise ValueError("non géré")

def _safe(expr, x=None, deg=False, ans=None):
    e = expr.strip().replace("^", "**").replace("×", "*").replace("÷", "/").replace("−", "-")
    F = dict(_F0)
    if deg:
        F["sin"] = lambda v: math.sin(math.radians(v))
        F["cos"] = lambda v: math.cos(math.radians(v))
        F["tan"] = lambda v: math.tan(math.radians(v))
    else:
        F.update(sin=math.sin, cos=math.cos, tan=math.tan)
    V = {"pi": math.pi, "e": math.e, "tau": math.tau}
    if x is not None:
        V["x"] = x
    if ans is not None:
        V["ans"] = ans
    v = _ev(ast.parse(e, mode="eval"), F, V)
    if isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v):
        raise ValueError
    return v

# ── lecture de l'état de calc.py (best effort) ──
def _find(*names):
    g = globals()
    for n in names:
        if n in g and not callable(g[n]) and not isinstance(g[n], type(math)):
            return g[n]
    for key in ("state", "STATE", "cfg", "CFG", "config", "CONFIG", "settings", "SETTINGS", "data"):
        d = g.get(key)
        if isinstance(d, dict):
            for n in names:
                if n in d:
                    return d[n]
    return None

def _mode():
    try:
        return "deg" if MODE["deg"] else "rad"
    except Exception:
        return None

def _usd():
    r = _find("rates", "RATES", "taux", "TAUX")
    v = None
    if isinstance(r, dict):
        for k in ("usd", "USD", "Usd"):
            if k in r:
                v = r[k]; break
    if v is None:
        v = _find("usd", "USD", "taux_usd", "TAUX_USD")
    if isinstance(v, (int, float)) and not isinstance(v, bool) and v:
        if v < 1:
            v = 1 / v
        return "USD %s" % (("%d" % v) if float(v).is_integer() else ("%.2f" % v))
    return None

def _barre_etat():
    parts = []
    m = _mode()
    if m:
        parts.append(m)
    try:
        t = _conf_load().get("theme") or "sombre"
    except Exception:
        t = None
    if isinstance(t, str) and t:
        parts.append(t)
    u = _usd()
    if u:
        parts.append(u)
    parts.append(datetime.datetime.now().strftime("%H:%M"))
    return " │ ".join(parts)

# ── dessins ──
def _fmt(v, maxch):
    t = str(int(v)) if float(v).is_integer() and abs(v) < 1e12 else format(v, ".8g")
    if len(t) > maxch:
        t = format(v, ".4g")
    return t.replace("e+", "E").replace("e", "E")[:maxch]

def _led(stdscr, v, y0, mx):
    t = _fmt(v, max(1, (mx - 2) // 4))
    rows = [""] * 5
    for ch in t:
        g = FONT.get(ch, FONT[" "])
        for i in range(5):
            rows[i] += g[i] + " "
    x = max(0, mx - 1 - len(rows[0]))
    for i in range(5):
        stdscr.addstr(y0 + i, x, rows[i], curses.color_pair(1) | curses.A_BOLD)

def _plot(stdscr, expr, y0, h, mx, deg):
    body = expr.strip()[4:].strip()
    parts = body.split()
    lo, hi = (-360.0, 360.0) if deg else (-2 * math.pi, 2 * math.pi)
    if len(parts) >= 3:
        try:
            lo, hi = float(parts[-2]), float(parts[-1])
            body = " ".join(parts[:-2])
        except ValueError:
            pass
    if not body:
        stdscr.addstr(y0, 2, "plot sin(x)   |   plot x**2 -5 5", curses.color_pair(4) | curses.A_DIM)
        return
    w = max(10, mx - 6)
    ys = []
    for i in range(w):
        x = lo + (hi - lo) * i / (w - 1)
        try:
            ys.append(_safe(body, x=x, deg=deg))
        except Exception:
            ys.append(None)
    vals = [v for v in ys if v is not None]
    if not vals:
        stdscr.addstr(y0, 2, "fonction incomplète…", curses.color_pair(4) | curses.A_DIM)
        return
    mn, mxv = min(vals), max(vals)
    if mn == mxv:
        mn -= 1; mxv += 1
    grid = [[" "] * w for _ in range(h)]
    if mn < 0 < mxv:
        r0 = h - 1 - int(round((0 - mn) / (mxv - mn) * (h - 1)))
        for c in range(w):
            grid[r0][c] = "─"
    if lo < 0 < hi:
        c0 = int(round((0 - lo) / (hi - lo) * (w - 1)))
        for r in range(h):
            grid[r][c0] = "│" if grid[r][c0] == " " else "┼"
    for r in range(h):
        stdscr.addstr(y0 + r, 3, "".join(grid[r]), curses.color_pair(3))
    for c, v in enumerate(ys):
        if v is None:
            continue
        r = h - 1 - int(round((v - mn) / (mxv - mn) * (h - 1)))
        stdscr.addstr(y0 + r, 3 + c, "●", curses.color_pair(1) | curses.A_BOLD)
    lab = "x[%g ; %g]  y[%.3g ; %.3g]" % (lo, hi, mn, mxv)
    stdscr.addstr(y0 + h, 3, lab[:mx - 4], curses.color_pair(4) | curses.A_DIM)

def _bar(stdscr, my, lv):
    n = int(round(max(0.0, min(1.0, lv)) * 10))
    attr = curses.color_pair(1) if lv >= 1 else curses.color_pair(4) | curses.A_DIM
    stdscr.addstr(my - 1, 1, "[" + "█" * n + "░" * (10 - n) + "]", attr)

def _buttons(stdscr, my, mx):
    w = 5 if len(_BTNS) * 5 <= mx - 2 else 4
    x0 = max(1, (mx - len(_BTNS) * w) // 2)
    _hot["row"] = my - 4
    _hot["cells"] = []
    for i, (lab, val) in enumerate(_BTNS):
        x = x0 + i * w
        a = curses.color_pair(4) | curses.A_REVERSE
        stdscr.addstr(my - 5, x, " " * (w - 1), a)
        stdscr.addstr(my - 4, x, lab.center(w - 1), a | curses.A_BOLD)
        _hot["cells"].append((x, x + w, val))

def extras_draw(stdscr, expr):
    try:
        my, mx = stdscr.getmaxyx()
        if my < 12 or mx < 24:
            return
        deg = (_mode() == "deg")
        e = (expr or "").strip()
        low = e.lower()
        zend = my - 7
        zh = zend - ZONE_TOP
        for r in range(ZONE_TOP, my - 1):
            stdscr.move(r, 0)
            stdscr.clrtoeol()
        level = 0.0
        first = low.split()[0] if low.split() else ""
        if first == "plot":
            level = 1.0
            if zh >= 5:
                _plot(stdscr, e, ZONE_TOP, min(zh - 1, 12), mx, deg)
        elif e:
            try:
                _st["last"] = _safe(e, deg=deg, ans=_st["last"])
                level = 1.0
            except SyntaxError:
                level = 0.4
            except Exception:
                level = 0.15
            if first in globals().get("CMDS", set()):
                level = 0.7
            if _st["last"] is not None and zh >= 5 and level >= 1.0:
                try:
                    _led(stdscr, _st["last"], ZONE_TOP, mx)
                except Exception:
                    pass
        if _st.get("mouse"):
            _buttons(stdscr, my, mx)
        stdscr.addstr(my - 2, 1, _barre_etat()[:mx - 2], curses.color_pair(3))
        if mx >= 40:
            stdscr.addstr(my - 1, 0, " " * 13)
            prev = _st["lvl"]
            if level != prev:
                for k in range(1, 5):
                    _bar(stdscr, my, prev + (level - prev) * k / 4)
                    stdscr.refresh()
                    time.sleep(0.015)
            _bar(stdscr, my, level)
            _st["lvl"] = level
    except Exception:
        pass

def _accueil_du_jour():
    return True  # accueil à chaque lancement
    f = os.path.expanduser("~/.calc_accueil")
    today = datetime.date.today().isoformat()
    try:
        with open(f) as h:
            if h.read().strip() == today:
                return False
    except OSError:
        pass
    try:
        with open(f, "w") as h:
            h.write(today)
    except OSError:
        pass
    return True

def splash(stdscr):
    try:
        try:
            curses.curs_set(0)
        except curses.error:
            pass
        try:
            curses.use_default_colors()
            curses.init_pair(7, curses.COLOR_CYAN, -1)
            col = curses.color_pair(7) | curses.A_BOLD
        except curses.error:
            col = curses.A_BOLD
        stdscr.nodelay(True)
        stdscr.erase()
        my, mx = stdscr.getmaxyx()
        big = mx >= 29 and my >= 14
        y = max(0, (my - 14) // 2)
        skip = False
        if big:
            for wi, word in enumerate(("ABOUDEV", "LABS")):
                x = max(0, (mx - (len(word) * 4 - 1)) // 2)
                for li, ch in enumerate(word):
                    g = FONT[ch]
                    for i in range(5):
                        stdscr.addstr(y + wi * 6 + i, x + li * 4, g[i], col)
                    stdscr.refresh()
                    time.sleep(0.28)
                    if stdscr.getch() != -1:
                        skip = True; break
                if skip:
                    break
            ty = y + 12
        else:
            t = "AbouDev Labs"
            stdscr.addstr(my // 2, max(0, (mx - len(t)) // 2), t, col)
            ty = my // 2 + 2
        if not skip:
            for off, tag in enumerate(("Termux Live Calculator", "TikTok : Aboujohan.dev", "daboujohan@gmail.com")):
                if ty + off >= my:
                    break
                x = max(0, (mx - len(tag)) // 2)
                for i, ch in enumerate(tag):
                    stdscr.addstr(ty + off, x + i, ch, curses.A_BOLD if off == 0 else curses.A_DIM)
                    stdscr.refresh()
                    time.sleep(0.04)
            stdscr.refresh()
            for _ in range(30):
                time.sleep(0.05)
                if stdscr.getch() != -1:
                    break
    except Exception:
        pass
    finally:
        try:
            stdscr.nodelay(False)
            curses.flushinp()
            curses.curs_set(1)
            stdscr.erase()
            stdscr.refresh()
        except Exception:
            pass

