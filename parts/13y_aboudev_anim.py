# ─── Aboudev : animation d'ouverture (logo + discussion à trois) ───────────
import time, curses

AB_W = 36
AB_TITRE = "A B O U D E V"
AB_DIALOGUE = [
    ("D", "Salut, moi c'est Abou !"),
    ("M", "Je suis Python, le chef."),
    ("G", "Et moi Baobab, l'arbre !"),
    ("D", "Quel langage, pour qui ?"),
    ("M", "Moi : pro, IA, web, partout."),
    ("D", "Aboudev : coder en français"),
    ("G", "Ensemble on code mieux !"),
    ("D", "Tape : ab affiche Salut"),
]
AB_PAR_REPLIQUE = 5
AB_QUEUE = {"G": 4, "M": 17, "D": 31}

def _ab_logo_rows(n):
    t = AB_TITRE[:n].ljust(len(AB_TITRE))
    i = AB_W - 2
    return ["╭" + "─" * i + "╮",
            "│" + t.center(i) + "│",
            "│" + "langage de programmation".center(i) + "│",
            "╰" + "─" * i + "╯"]

def _ab_bulle(qui, texte):
    w = len(texte) + 2
    n = w + 2
    if qui == "G":
        off = 0
    elif qui == "D":
        off = AB_W - n
    else:
        off = max(0, min(AB_W - n, AB_QUEUE["M"] - n // 2))
    idx = min(max(AB_QUEUE[qui] - off, 1), n - 2)
    bas = list("╰" + "─" * w + "╯")
    bas[idx] = "┬"
    rows = ["╭" + "─" * w + "╮", "│ " + texte + " │", "".join(bas)]
    return [(" " * off + r).ljust(AB_W) for r in rows]

def _ab_scene(f, qui):
    mg = "o" if (qui == "G" and f % 2) else "_"
    mm = "o" if (qui == "M" and f % 2) else "_"
    md = "o" if (qui == "D" and f % 2) else "_"
    lang = "~" if f % 3 == 0 else " "
    v1, v2 = ("~", " ") if (f // 2) % 2 else (" ", "~")
    feu = "," if (f // 2) % 2 else "."
    bao = [f" {feu}@@@@@{feu} ", "@@@@@@@@@", f" \\(^{mg}^)/ ", "   |||   ", "  _|||_  ", " /_|||_\\ "]
    cou = ["  \\^^/  ", f" (O{mm}O){lang} ", "  | |   "]
    tab = ["     " + cou[0] + "     ",
           f"  {v1}  " + cou[1] + f"  {v2}  ",
           " (_) " + cou[2] + " (_) ",
           ".----------------.",
           "  ||          ||  ", "  ||          ||  "]
    boy = ["  _____  ", " /_____\\ ", f" ( ^{md}^ ) ", "[ABOUDEV]", "  /| |\\  ", "  _| |_  "]
    corps = ("  " + ("~-" * 16)[f % 2:][:26]).ljust(AB_W)
    return bao, tab, boy, corps

def ab_splash(stdscr):
    if os.path.exists(os.path.expanduser("~/.calc_noanim")):
        return
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
                bao, tab, boy, corps = _ab_scene(f, qui)
                for i in range(6):
                    put(8 + i, 0, bao[i], A2)
                    put(8 + i, 9, tab[i], A3)
                    put(8 + i, 27, boy[i], A1)
                put(14, 0, corps, A2)
                put(15, 0, "touche = passer"[:AB_W], A3 | curses.A_DIM)
            stdscr.refresh()
            if attente(90 if f is None else 280):
                break
    finally:
        stdscr.timeout(-1)
        stdscr.erase()
        try:
            curses.curs_set(1)
        except curses.error:
            pass
