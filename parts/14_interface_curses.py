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
    apply_theme(stdscr)
    if not pin_gate(stdscr):
        return

    history = deque(maxlen=8)   # derniers calculs
    expr = ""
    cursor_pos = len(expr)

    HELP_LINES = [
        "  Tape un calcul : 12*3, sqrt(144)",
        "  aide = toutes les commandes",
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
                          "  Entrée valider  Esc quitter  Ctrl+L effacer",
                          curses.color_pair(4))
        except curses.error:
            pass

        # ── Positionner le curseur dans la saisie ───────────────
        cursor_col = start_x + len(prompt) + cursor_pos
        try:
            stdscr.move(5, min(cursor_col, max_x - 1))
        except curses.error:
            pass

        _cy, _cx = stdscr.getyx()
        trace_bar(stdscr, expr)
        brand_bar(stdscr)
        extras_draw(stdscr, expr)
        try:
            stdscr.move(_cy, _cx)
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
        elif key in ("\n", "\r", 10, 13, curses.KEY_ENTER):              # Enter → sauvegarder dans historique
            _dbg("Entrée : reçue")
            if coffre_check(stdscr, expr.strip()):
                expr = ""
                cursor_pos = 0
                continue
            if expr.strip().lower() in ("tactile", "tactile on", "tactile off"):
                set_tactile(expr.strip().lower())
                expr = ""
                cursor_pos = 0
                continue
            if expr.strip().lower() in APROPOS_CMDS:
                apropos_screen(stdscr)
                expr = ""
                cursor_pos = 0
                continue
            if expr.strip().lower() in ("aide", "help", "?"):
                aide_screen(stdscr)
                expr = ""
                cursor_pos = 0
                continue
            _dbg("Entrée : avant commande")
            applied = try_lot1(expr, apply=True) or try_lot2(expr, apply=True) or try_lot3(expr, stdscr, apply=True) or try_lot4(expr, stdscr, apply=True) or try_lot5(expr, stdscr, apply=True)
            if applied:
                result = applied
            _dbg("Entrée : après commande")
            if expr.strip() and result and "⚠" not in result:
                history.append((expr.strip(), result))
                try:
                    with open(HIST_FILE, "a") as f:
                        f.write(f"{datetime.now():%Y-%m-%d %H:%M}  {expr.strip()}  =  {result}\n")
                except Exception:
                    pass
            expr = ""
            cursor_pos = 0
        elif isinstance(key, str) and key.isprintable():
            expr = expr[:cursor_pos] + key + expr[cursor_pos:]
            cursor_pos += 1


def main():
    try:
        curses.wrapper(lambda _s: (splash(_s) if _accueil_du_jour() else None, draw_ui(MouseProxy(_s)))[1])
    except KeyboardInterrupt:
        _dbg("sortie : Ctrl+C")
    except BaseException:
        import traceback
        _dbg("sortie : erreur\n" + traceback.format_exc())
        raise
    else:
        _dbg("sortie : fin normale")


if __name__ == "__main__":
    main()
