# ─── Lot 10 : écran « À propos » ───────────────────────────────────────────
import textwrap

APROPOS_CMDS = ("apropos", "a propos", "à propos", "about", "presentation",
                "présentation", "info", "infos")

ABOUT = {
    "PROJET": [
        ("h", "CALC · Termux Live Calculator"),
        ("t", "Une calculatrice vivante dans le terminal : le résultat se calcule pendant que tu tapes."),
        ("", ""),
        ("s", "Ce qu'elle sait faire"),
        ("l", "Calcul scientifique, conversions, devises FCFA / EUR / USD"),
        ("l", "Outils de boutique : prix et bénéfice, monnaie, ventes, dettes, stock, rappels, factures"),
        ("l", "Mesure de terrain : surface, hauteur, distance GPS entre deux téléphones"),
        ("l", "Sécurité : PIN et sauvegarde chiffrée AES-256"),
        ("l", "Interface : thèmes, résultat LED, graphiques ASCII, boutons tactiles"),
        ("", ""),
        ("t", "Pensée pour la Côte d'Ivoire et l'Afrique de l'Ouest : FCFA, usage en boutique, français."),
    ],
    "DEV": [
        ("h", "Diomandé Abou Johan"),
        ("t", "Fondateur d'AbouDev Labs, architecte de systèmes, développeur solo autodidacte."),
        ("", ""),
        ("s", "Parcours"),
        ("l", "Basé à Abidjan, Côte d'Ivoire"),
        ("l", "Construit ses outils directement sur téléphone Android avec Termux"),
        ("", ""),
        ("s", "Technologies"),
        ("l", "Python · Node.js · React Native / Expo · Firebase"),
        ("l", "Paiements Mobile Money et interfaces en français pour le marché ouest-africain"),
    ],
    "TECH": [
        ("h", "Sous le capot"),
        ("l", "Python 3 + curses pour l'interface plein écran"),
        ("l", "Chiffrement : OpenSSL AES-256, PIN protégé par PBKDF2"),
        ("l", "Position GPS via Termux:API pour les mesures entre deux téléphones"),
        ("l", "Aperçu en direct : le coin « machine » montre ce qui se passe pendant la frappe"),
        ("l", "{lignes} lignes de Python, écrites sur téléphone"),
    ],
    "AUTRES": [
        ("h", "Autres projets AbouDev Labs"),
        ("l", "TermChat : messagerie chiffrée"),
        ("l", "VITE API : API de paiement Mobile Money (sandbox) pour développeurs ivoiriens"),
        ("l", "KlassGuard : détection de présence en classe (WiFi / BLE)"),
        ("l", "Carnet Secret : journal quotidien chiffré"),
        ("l", "Serveur ROI : serveur Rust construit sur le téléphone"),
        ("l", "Jeu Baobab : jeu vidéo inspiré du baobab"),
    ],
    "CONTACT": [
        ("h", "Parlons-en"),
        ("l", "E-mail : daboujohan@gmail.com"),
        ("l", "TikTok : Aboujohan.dev"),
        ("l", "GitHub : daboujohan-hub"),
        ("l", "Portfolio : daboujohan-hub.github.io"),
        ("", ""),
        ("t", "by AbouDev Labs · Abidjan"),
    ],
}

def _nb_lignes():
    try:
        d = os.path.join(os.path.dirname(os.path.realpath(__file__)), "parts")
        if os.path.isdir(d):
            fs = [os.path.join(d, n) for n in sorted(os.listdir(d)) if n.endswith(".py")]
        else:
            fs = [os.path.realpath(__file__)]
        t = 0
        for f in fs:
            with open(f, encoding="utf-8") as h:
                t += sum(1 for _ in h)
        return str(t)
    except Exception:
        return "?"

def _about_flat(tab, w):
    out = []
    for kind, text in ABOUT[tab]:
        text = text.replace("{lignes}", _nb_lignes())
        if not text:
            out.append(("", ""))
            continue
        if kind == "l":
            pre1, pre2 = "› ", "  "
        elif kind == "h":
            pre1, pre2 = "◆ ", "  "
        else:
            pre1 = pre2 = ""
        for j, ln in enumerate(textwrap.wrap(text, max(10, w - 2 - len(pre1))) or [""]):
            out.append((kind, (pre1 if j == 0 else pre2) + ln))
    return out

def _about_draw(stdscr, tabs, tab, flat, top, page, budget):
    stdscr.erase()
    my, mx = stdscr.getmaxyx()
    zones = []
    A1 = curses.color_pair(1) | curses.A_BOLD
    A3 = curses.color_pair(3)
    A4 = curses.color_pair(4)
    try:
        stdscr.addstr(0, 1, "╭─ À PROPOS ─ AbouDev Labs"[:mx - 2], A1)
        x = 1
        for i, t in enumerate(tabs):
            lab = " %s " % t
            if x + len(lab) >= mx:
                break
            attr = (A1 | curses.A_REVERSE) if i == tab else A4
            stdscr.addstr(2, x, lab, attr)
            zones.append((1, 3, x, x + len(lab) + 1, str(i + 1)))
            x += len(lab) + 1
        stdscr.addstr(3, 1, "─" * max(0, mx - 3), A3)
        left = budget
        styles = {"h": A1, "s": A3 | curses.A_BOLD, "l": A4, "t": A4}
        for i, (kind, text) in enumerate(flat[top:top + page]):
            if left is not None:
                if left <= 0:
                    break
                text = text[:left]
                left -= len(text)
            stdscr.addstr(5 + i, 2, text[:mx - 3], styles.get(kind, A4))
        if top > 0:
            stdscr.addstr(4, mx - 3, "▲", A3)
        if top + page < len(flat):
            stdscr.addstr(my - 4, mx - 3, "▼", A3)
        lab = " ✕ Fermer "
        bx = max(0, (mx - len(lab)) // 2)
        stdscr.addstr(my - 3, bx, lab, A4 | curses.A_REVERSE | curses.A_BOLD)
        zones.append((my - 4, my - 2, bx, bx + len(lab), "q"))
        stdscr.addstr(my - 1, 1, "←→ rubrique · ↑↓ défiler · Esc retour"[:mx - 2], A3)
    except curses.error:
        pass
    return zones

def apropos_screen(stdscr):
    hot = globals().get("_hot")
    saved = (hot.get("row", -1), list(hot.get("zones", []))) if hot is not None else None
    tabs = list(ABOUT)
    tab, top = 0, 0
    seen = set()
    try:
        curses.curs_set(0)
    except curses.error:
        pass

    def show(flat, page, budget):
        z = _about_draw(stdscr, tabs, tab, flat, top, page, budget)
        if hot is not None:
            hot["zones"] = z
            hot["row"] = -10
        stdscr.refresh()

    try:
        while True:
            my, mx = stdscr.getmaxyx()
            flat = _about_flat(tabs[tab], mx - 4)
            page = max(3, my - 9)
            if tab not in seen:
                seen.add(tab)
                total = sum(len(t) for _, t in flat[top:top + page])
                stdscr.nodelay(True)
                try:
                    b = 0
                    while b < total:
                        show(flat, page, b)
                        time.sleep(0.012)
                        if stdscr.getch() != -1:
                            break
                        b += 3
                finally:
                    stdscr.nodelay(False)
            show(flat, page, None)
            k = stdscr.get_wch()
            top_max = max(0, len(flat) - page)
            if k in (27, "\x1b", "q", "Q", "\n", "\r", curses.KEY_ENTER):
                return
            if k in (curses.KEY_RIGHT, "\t"):
                tab = (tab + 1) % len(tabs); top = 0
            elif k == curses.KEY_LEFT:
                tab = (tab - 1) % len(tabs); top = 0
            elif isinstance(k, str) and k.isdigit() and 1 <= int(k) <= len(tabs):
                tab = int(k) - 1; top = 0
            elif k == curses.KEY_DOWN:
                top = min(top_max, top + 1)
            elif k == curses.KEY_UP:
                top = max(0, top - 1)
    finally:
        if hot is not None and saved is not None:
            hot["row"], hot["zones"] = saved
        try:
            curses.curs_set(1)
        except curses.error:
            pass
        stdscr.erase()
        stdscr.refresh()

def brand_bar(stdscr):
    try:
        my, mx = stdscr.getmaxyx()
        a, b = "by AbouDev Labs", " · TikTok : Aboujohan.dev"
        if len(a) + len(b) > mx - 2:
            b = ""
        x = max(0, (mx - len(a) - len(b)) // 2)
        stdscr.addstr(0, x, a, curses.color_pair(1) | curses.A_BOLD)
        if b:
            stdscr.addstr(0, x + len(a), b, curses.color_pair(4) | curses.A_DIM)
    except Exception:
        pass

def trace_bar(stdscr, expr):
    import re, ast
    try:
        my, mx = stdscr.getmaxyx()
        spin = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"[len(expr) % 10]
        e = expr.strip()
        if not e:
            msg = spin + " j'attends"
        else:
            toks = re.findall(r"\d+(?:[.,]\d+)?|[A-Za-z_]+|\S", e)
            n = len(toks)
            low = e.lower()
            first = low.split()[0]
            if first in CMDS:
                msg = "%s commande « %s » · %d jetons" % (spin, first, n)
            elif re.search(r"\s(to|en)\s", low):
                msg = "%s conversion · %d jetons → table d'unités" % (spin, n)
            elif "%" in e:
                msg = "%s pourcentage · %d jetons" % (spin, n)
            else:
                try:
                    tree = ast.parse(e.replace("^", "**"), mode="eval")
                    ops = sum(isinstance(x, (ast.BinOp, ast.UnaryOp, ast.Call))
                              for x in ast.walk(tree))
                    msg = "%s %d jetons → arbre %d op → prêt" % (spin, n, ops)
                except SyntaxError:
                    msg = "%s %d jetons · incomplet, j'attends la suite" % (spin, n)
        msg = msg[:max(10, mx // 2 + 6)]
        x = max(0, mx - len(msg) - 2)
        stdscr.addstr(my - 1, x, msg, curses.color_pair(4) | curses.A_DIM)
    except Exception:
        pass

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
    lot = try_lot1(expr)
    if lot:
        return lot
    lot2 = try_lot2(expr)
    if lot2:
        return lot2
    lot3 = try_lot3(expr)
    if lot3:
        return lot3
    lot4 = try_lot4(expr)
    if lot4:
        return lot4
    lot5 = try_lot5(expr)
    if lot5:
        return lot5
    if expr.strip().lower() in APROPOS_CMDS:
        return "Entrée pour la présentation"
    if expr.strip().lower() in ("aide", "help", "?"):
        return "Entrée pour ouvrir l'aide"
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

