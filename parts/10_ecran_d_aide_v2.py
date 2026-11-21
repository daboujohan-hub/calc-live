# ─── Écran d'aide v2 ───────────────────────────────────────────────────────
AIDE2 = [
    ("CALCUL", [
        ("sqrt sin cos tan", "maths"), ("log log2 log10 exp", "logs"),
        ("fact gcd lcm hypot", "entiers"), ("max min", "extrêmes"),
        ("pi  e  tau  x**n", "constantes"), ("mode deg | rad", "angles"),
        ("100 km to miles", "conversion"), ("37 c to f", "température"),
        ("5000 cfa to eur", "devises"), ("taux usd 600", "régler un taux")]),
    ("BOUTIQUE", [
        ("prix 5000 benefice 20%", "marge"), ("5000 + 20%", "ajout %"),
        ("20% de 5000", "part"), ("monnaie 10000 - 7500", "rendu"),
        ("vente riz 2500 x3", "ventes"), ("dette awa 5000", "dettes"),
        ("stock riz +10", "stock"), ("rappel 17h appeler", "rappels"),
        ("facture riz 2500x3, huile 1000x2", "facture")]),
    ("MESURE", [
        ("surface 5x4", "aire"), ("hauteur 10 angle 35", "trigo"),
        ("point | terrain", "relevés"), ("terrain efface", "reset"),
        ("mesure serveur", "partage"), ("mesure connecte IP CODE", "lien"),
        ("mesure enregistre nom", "sauver"), ("mesures", "liste")]),
    ("INFO", [("apropos", "présentation"), ("aide", "commandes"), ("tactile on | off", "boutons tactiles")]),
    ("SÉCURITÉ", [
        ("pin | pin off", "verrou"), ("theme clair | sombre", "look"),
        ("sauvegarde", "copie"), ("export", "fichier"),
        ("restaure", "retour")]),
]

def aide_screen(stdscr):
    tab = 0
    top = 0
    BOLD = curses.A_BOLD
    while True:
        stdscr.erase()
        my, mx = stdscr.getmaxyx()
        items = AIDE2[tab][1]
        page = max(1, my - 7)
        try:
            stdscr.addstr(0, 1, "╭─ CALC·LIVE ─ aide"[:mx - 2], curses.color_pair(1) | BOLD)
            x = 1
            for i, (t, _) in enumerate(AIDE2):
                lab = " " + t + " "
                attr = (curses.color_pair(1) | curses.A_REVERSE | BOLD) if i == tab else curses.color_pair(4)
                if x + len(lab) < mx - 1:
                    stdscr.addstr(2, x, lab, attr)
                x += len(lab) + 1
            stdscr.addstr(3, 1, "─" * max(0, mx - 3), curses.color_pair(3))
            for i, (cmd, desc) in enumerate(items[top:top + page]):
                y = 5 + i
                stdscr.addstr(y, 1, "›", curses.color_pair(3))
                stdscr.addstr(y, 3, cmd[:mx - 4], curses.color_pair(1) | BOLD)
                col = 3 + len(cmd) + 2
                if desc and col + len(desc) < mx - 1:
                    stdscr.addstr(y, col, desc, curses.color_pair(4) | curses.A_DIM)
            foot = "←→ rubrique · ↑↓ défiler · Esc retour  %d/%d" % (tab + 1, len(AIDE2))
            stdscr.addstr(my - 1, 1, foot[:mx - 2], curses.color_pair(3))
        except curses.error:
            pass
        stdscr.refresh()
        k = stdscr.get_wch()
        top_max = max(0, len(items) - page)
        if k in (27, "\x1b", "q", "\n", "\r"):
            return
        if k == curses.KEY_RIGHT:
            tab = (tab + 1) % len(AIDE2); top = 0
        elif k == curses.KEY_LEFT:
            tab = (tab - 1) % len(AIDE2); top = 0
        elif k == curses.KEY_DOWN:
            top = min(top_max, top + 1)
        elif k == curses.KEY_UP:
            top = max(0, top - 1)

