# ─── Aboudev : écran d'aide (titre LED, état, guide) ───────────────────────
import textwrap

def _ab_aide_lines(mx):
    L = []
    if mx >= 31 and "FONT" in globals():
        rows = [""] * 5
        for ch in "ABOUDEV":
            g = FONT.get(ch, FONT[" "])
            for i in range(5):
                rows[i] += g[i] + " "
        L += [("led", r) for r in rows]
    else:
        L.append(("h", "ABOUDEV"))
    L.append(("", ""))
    if _ab_cmd() is not None:
        L.append(("ok", "● Aboudev est installé"))
    else:
        L.append(("ko", "○ Aboudev introuvable : il faut une commande aboudev ou le fichier ~/aboudev/aboudev.py"))
    L.append(("", ""))
    L.append(("s", "Commandes"))
    for c, d in (("ab affiche Bonjour", "exécute une ligne"),
                 ("ab prog.a", "lance un programme"),
                 ("ab edite prog", "écrit avec nano, puis lance"),
                 ("ab liste", "tes programmes .a"),
                 ("ab anim", "revoir l'animation")):
        L += [("c", c), ("d", d)]
    L.append(("", ""))
    L.append(("s", "Premiers pas"))
    L += [("t", "1. Tape  ab affiche Bonjour le monde !  puis Entrée."),
          ("t", "2. Tape  ab hello.a  : lance l'exemple de ~/aboudev."),
          ("t", "3. Tape  ab edite salut  : nano s'ouvre. Écris  affiche Salut !  puis enregistre (Ctrl+O, Entrée) et quitte (Ctrl+X) : le programme se lance tout seul."),
          ("t", "4. Retrouve tes programmes avec  ab liste.")]
    L.append(("", ""))
    L.append(("s", "Mémo du langage"))
    for c, d in (("affiche TEXTE", "écrit du texte"),
                 ("$nom", "valeur d'une variable"),
                 ("calculer _carre = $n * $n", "faire un calcul"),
                 ("fonction nom(n) ... fin_fonction", "définir une fonction"),
                 ("importer_module utils", "charger utils.a")):
        L += [("c", c), ("d", d)]
    L.append(("t", "Documentation complète : aboudev --aide (dans Termux)."))
    L.append(("", ""))
    L += [("t", "Chaque programme est arrêté au bout de 20 secondes."),
          ("w", "Attention : Aboudev peut exécuter des commandes.")]
    return L

def ab_aide_screen(stdscr):
    hot = globals().get("_hot")
    saved = (hot.get("row", -1), list(hot.get("zones", []))) if hot is not None else None
    top = 0
    try:
        curses.curs_set(0)
    except curses.error:
        pass
    stdscr.timeout(-1)
    try:
        while True:
            stdscr.erase()
            my, mx = stdscr.getmaxyx()
            lines = []
            for kind, text in _ab_aide_lines(mx):
                if kind in ("t", "ko", "w", "d", "ok") and text:
                    pre = "  " if kind == "d" else ""
                    for ln in textwrap.wrap(text, max(10, mx - 5 - len(pre))) or [""]:
                        lines.append((kind, pre + ln))
                else:
                    lines.append((kind, text))
            page = max(3, my - 6)
            top = max(0, min(top, max(0, len(lines) - page)))
            A1 = curses.color_pair(1) | curses.A_BOLD
            A3 = curses.color_pair(3)
            A4 = curses.color_pair(4)
            zones = []
            try:
                stdscr.addstr(0, 1, "╭─ AbouDev Labs ─ langage Aboudev"[:mx - 2], A1)
                for i, (kind, text) in enumerate(lines[top:top + page]):
                    y = 2 + i
                    if kind == "led":
                        stdscr.addstr(y, max(1, (mx - len(text)) // 2), text[:mx - 2], A1)
                    elif kind in ("h", "ok"):
                        stdscr.addstr(y, 2, text[:mx - 3], A1)
                    elif kind == "s":
                        stdscr.addstr(y, 2, "◆ " + text, A3 | curses.A_BOLD)
                    elif kind == "c":
                        stdscr.addstr(y, 2, "› ", A3)
                        stdscr.addstr(y, 4, text[:mx - 5], A1)
                    elif kind == "d":
                        stdscr.addstr(y, 2, text[:mx - 3], A4 | curses.A_DIM)
                    elif kind in ("ko", "w"):
                        stdscr.addstr(y, 2, text[:mx - 3], curses.A_BOLD)
                    elif text:
                        stdscr.addstr(y, 2, text[:mx - 3], A4)
                if top > 0:
                    stdscr.addstr(1, mx - 3, "▲", A3)
                if top + page < len(lines):
                    stdscr.addstr(my - 4, mx - 3, "▼", A3)
                lab = " ✕ Fermer "
                bx = max(0, (mx - len(lab)) // 2)
                stdscr.addstr(my - 3, bx, lab, A4 | curses.A_REVERSE | curses.A_BOLD)
                zones.append((my - 4, my - 2, bx, bx + len(lab), "q"))
                stdscr.addstr(my - 1, 1, "↑↓ défiler · Esc retour"[:mx - 2], A3)
            except curses.error:
                pass
            if hot is not None:
                hot["zones"] = zones
                hot["row"] = -10
            stdscr.refresh()
            k = stdscr.get_wch()
            if k in (27, "\x1b", "q", "Q", "\n", "\r", curses.KEY_ENTER):
                return
            if k == curses.KEY_DOWN:
                top += 1
            elif k == curses.KEY_UP:
                top -= 1
            elif k == curses.KEY_NPAGE:
                top += page
            elif k == curses.KEY_PPAGE:
                top -= page
    finally:
        if hot is not None and saved is not None:
            hot["row"], hot["zones"] = saved
        try:
            curses.curs_set(1)
        except curses.error:
            pass
        stdscr.erase()
        stdscr.refresh()
