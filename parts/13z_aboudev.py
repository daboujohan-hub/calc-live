# ─── Aboudev : exécuter du code Aboudev depuis la calculatrice ─────────────
import os, re, sys, shutil, subprocess, tempfile, curses

AB_HOME = os.path.expanduser("~/aboudev")
AB_AIDE = [
    "ab affiche Bonjour   une ligne Aboudev",
    "ab prog.a            lance un programme .a",
    "ab edite prog        écrire (nano) puis lancer",
    "ab liste             tes programmes .a",
    "ab anim              revoir l'animation",
    "",
    "Dossier : ~/aboudev",
    "Attention : Aboudev peut exécuter des commandes.",
]

def _ab_cmd():
    p = shutil.which("aboudev")
    if p:
        return [p]
    f = os.path.join(AB_HOME, "aboudev.py")
    return [sys.executable, f] if os.path.isfile(f) else None

def _ab_exec(path):
    cmd = _ab_cmd()
    if not cmd:
        return ["⚠  Aboudev introuvable (dossier ~/aboudev)"]
    try:
        r = subprocess.run(cmd + [path], capture_output=True, text=True,
                           errors="replace", timeout=20, stdin=subprocess.DEVNULL,
                           cwd=os.path.dirname(os.path.abspath(path)))
    except subprocess.TimeoutExpired:
        return ["⚠  trop long (20 s), arrêté"]
    except Exception:
        return ["⚠  impossible de lancer Aboudev"]
    txt = re.sub(r"\x1b\[[0-9;]*[A-Za-z]", "", (r.stdout or "") + (r.stderr or ""))
    return txt.splitlines()[:500] or ["(aucune sortie)"]

def _ab_line(code):
    if not _ab_cmd():
        return ["⚠  Aboudev introuvable (dossier ~/aboudev)"]
    os.makedirs(AB_HOME, exist_ok=True)
    fd, path = tempfile.mkstemp(suffix=".a", dir=AB_HOME)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(code.strip() + "\n")
        return _ab_exec(path)
    finally:
        try:
            os.remove(path)
        except OSError:
            pass

def _ab_path(name):
    name = name.strip()
    for c in (os.path.join(AB_HOME, name), os.path.expanduser(name)):
        if os.path.isfile(c):
            return c
    return None

def _ab_edit(stdscr, path):
    ed = (os.environ.get("EDITOR") or "nano").split()
    if not shutil.which(ed[0]):
        return False
    os.makedirs(os.path.dirname(path), exist_ok=True)
    curses.def_prog_mode()
    curses.endwin()
    try:
        subprocess.run(ed + [path])
    finally:
        curses.reset_prog_mode()
        stdscr.refresh()
    return True

def _ab_show(stdscr, titre, lines):
    top = 0
    try:
        curses.curs_set(0)
    except curses.error:
        pass
    stdscr.timeout(-1)
    while True:
        stdscr.erase()
        my, mx = stdscr.getmaxyx()
        page = max(1, my - 4)
        top = max(0, min(top, max(0, len(lines) - page)))
        try:
            stdscr.addstr(0, 1, titre[:mx - 2], curses.color_pair(1) | curses.A_BOLD)
            for i, t in enumerate(lines[top:top + page]):
                stdscr.addstr(2 + i, 1, t[:mx - 2], curses.color_pair(4))
            stdscr.addstr(my - 1, 1, "↑ ↓ défiler · Esc retour"[:mx - 2], curses.color_pair(3))
        except curses.error:
            pass
        stdscr.refresh()
        k = stdscr.get_wch()
        if k in (27, "\x1b", "q", "\n", "\r", curses.KEY_ENTER):
            break
        if k == curses.KEY_DOWN:
            top += 1
        elif k == curses.KEY_UP:
            top -= 1
        elif k == curses.KEY_NPAGE:
            top += page
        elif k == curses.KEY_PPAGE:
            top -= page
    try:
        curses.curs_set(1)
    except curses.error:
        pass

def try_ab(expr, stdscr=None, apply=False):
    m = re.fullmatch(r"ab(?:\s+(.*))?", expr.strip(), re.S)
    if not m:
        return None
    if apply and stdscr is None:
        return None
    arg = (m.group(1) or "").strip()
    try:
        if not arg or arg in ("aide", "anim"):
            if apply:
                ab_splash(stdscr)
                if arg != "anim":
                    ab_aide_screen(stdscr)
                return "Aboudev"
            return "Entrée pour ouvrir Aboudev"
        if arg == "liste":
            fs = sorted(f for f in os.listdir(AB_HOME) if f.endswith(".a")) \
                if os.path.isdir(AB_HOME) else []
            return " ".join(fs) or "aucun programme .a dans ~/aboudev"
        m = re.fullmatch(r"edite\s+([\w-]+)(?:\.a)?", arg)
        if m:
            path = os.path.join(AB_HOME, m.group(1) + ".a")
            if not apply:
                return f"Entrée : écrire puis lancer {m.group(1)}.a"
            if not _ab_edit(stdscr, path):
                return "⚠  éditeur absent : pkg install nano"
            if not os.path.isfile(path):
                return "annulé"
            lines, titre = _ab_exec(path), m.group(1) + ".a"
        elif re.fullmatch(r"[\w./~-]+\.a", arg):
            path = _ab_path(arg)
            if not path:
                return "⚠  programme introuvable"
            if not apply:
                return f"Entrée pour lancer {arg}"
            lines, titre = _ab_exec(path), arg
        else:
            if not apply:
                return "Entrée pour exécuter : " + arg[:40]
            lines, titre = _ab_line(arg), "ab " + arg[:30]
        _ab_show(stdscr, titre, [l.expandtabs(4) for l in lines])
        return f"Aboudev : {len(lines)} ligne(s) de sortie"
    except Exception:
        return "⚠  erreur Aboudev" if apply else None

# Accroche : ab passe par la chaîne de commandes existante (via try_lot5).
_try_lot5_sans_ab = try_lot5

def try_lot5(expr, stdscr=None, apply=False):
    return _try_lot5_sans_ab(expr, stdscr, apply) or try_ab(expr, stdscr, apply)
