# ─── Aboudev : animation d'ouverture (logo + discussion) ───────────────────
import time, curses

AB_W = 32
AB_TITRE = "A B O U D E V"
AB_DIALOGUE = [
    ("G", "Salut !"),
    ("D", "Je suis Aboudev"),
    ("G", "Code en français ?"),
    ("D", "affiche Bonjour !"),
]
AB_PAR_REPLIQUE = 5

def _ab_logo_rows(n):
    t = AB_TITRE[:n].ljust(len(AB_TITRE))
    i = AB_W - 2
    return ["╭" + "─" * i + "╮",
            "│" + t.center(i) + "│",
            "│" + "langage en français".center(i) + "│",
            "╰" + "─" * i + "╯"]

def _ab_bulle(qui, texte):
    w = len(texte) + 2
    bas = list("╰" + "─" * w + "╯")
    bas[4 if qui == "G" else w - 2] = "┬"
    rows = ["╭" + "─" * w + "╮", "│ " + texte + " │", "".join(bas)]
    off = 0 if qui == "G" else AB_W - len(rows[0])
    return [(" " * off + r).ljust(AB_W) for r in rows]

def _ab_scene(f, qui):
    mg = "o" if (qui == "G" and f % 2) else "_"
    md = "o" if (qui == "D" and f % 2) else "_"
    v1, v2 = ("~", " ") if (f // 2) % 2 else (" ", "~")
    bao = [" ,@@@@@, ", "@@@@@@@@@", f" \\(^{mg}^)/ ", "   |||   ", "  _|||_  ", " /_|||_\\ "]
    tab = ["              ", f"   {v1}      {v2}   ", "  (_)    (_)  ",
           ".------------.", "  ||      ||  ", "  ||      ||  "]
    boy = ["  _____  ", " /_____\\ ", f" ( ^{md}^ ) ", "[ABOUDEV]", "  /| |\\  ", "  _| |_  "]
    serp = (" " * 5 + ("~-" * 11)[f % 2:][:20] + "(o>").ljust(AB_W)
    return bao, tab, boy, serp

def ab_splash(stdscr):
    my, mx = stdscr.getmaxyx()
    if my < 17 or mx < AB_W + 2:
        return
    x0, y0 = (mx - AB_W) // 2, max(0, (my - 16) // 2)
    A1 = curses.color_pair(1) | curses.A_BOLD
    A2, A3, A4 = curses.color_pair(2), curses.color_pair(3), curses.color_pair(4)

    def put(y, x, t, a):
        try:
            stdscr.addstr(y0 + y, x0 + x, t, a)
        except curses.error:
            pass

    def attente(ms):
        stdscr.timeout(ms)
        try:
            stdscr.get_wch()
            return True
        except curses.error:
            return False

    try:
        curses.curs_set(0)
    except curses.error:
        pass
    try:
        etapes = [(None, n) for n in range(len(AB_TITRE) + 1)]
        etapes += [(f, len(AB_TITRE)) for f in range(AB_PAR_REPLIQUE * len(AB_DIALOGUE))]
        for f, n in etapes:
            stdscr.erase()
            for i, r in enumerate(_ab_logo_rows(n)):
                put(i, 0, r, A1)
            if f is not None:
                qui, txt = AB_DIALOGUE[f // AB_PAR_REPLIQUE]
                for i, r in enumerate(_ab_bulle(qui, txt)):
                    put(5 + i, 0, r, A4)
                bao, tab, boy, serp = _ab_scene(f, qui)
                for i in range(6):
                    put(8 + i, 0, bao[i], A2)
                    put(8 + i, 9, tab[i], A3)
                    put(8 + i, 23, boy[i], A1)
                put(14, 0, serp, A2)
                put(15, 0, "touche = passer"[:AB_W], A3 | curses.A_DIM)
            stdscr.refresh()
            if attente(90 if f is None else 300):
                break
    finally:
        stdscr.timeout(-1)
        stdscr.erase()
        try:
            curses.curs_set(1)
        except curses.error:
            pass
