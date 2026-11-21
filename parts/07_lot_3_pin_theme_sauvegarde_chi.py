# ─── Lot 3 : PIN, thème, sauvegarde chiffrée, export ───────────────────────
import hashlib, hmac, secrets, shutil, subprocess
PIN_FILE = os.path.expanduser("~/.calc_pin.json")
CONF_FILE = os.path.expanduser("~/.calc_config.json")
BACKUP_DIR = os.path.expanduser("~/calc_sauvegardes")
SHARE_DIR = os.path.expanduser("~/storage/shared/Download")

def _conf_load():
    try:
        with open(CONF_FILE) as f:
            return json.load(f)
    except Exception:
        return {}

def _conf_save(c):
    with open(CONF_FILE, "w") as f:
        json.dump(c, f)

def apply_theme(stdscr):
    if _conf_load().get("theme") == "clair":
        pairs = [(1, curses.COLOR_BLUE, curses.COLOR_WHITE),
                 (2, curses.COLOR_GREEN, curses.COLOR_WHITE),
                 (3, curses.COLOR_MAGENTA, curses.COLOR_WHITE),
                 (4, curses.COLOR_BLACK, curses.COLOR_WHITE),
                 (5, curses.COLOR_RED, curses.COLOR_WHITE),
                 (6, curses.COLOR_WHITE, curses.COLOR_BLUE)]
    else:
        pairs = [(1, curses.COLOR_CYAN, -1), (2, curses.COLOR_GREEN, -1),
                 (3, curses.COLOR_YELLOW, -1), (4, curses.COLOR_WHITE, -1),
                 (5, curses.COLOR_RED, -1),
                 (6, curses.COLOR_BLACK, curses.COLOR_CYAN)]
    for n, fg, bg in pairs:
        curses.init_pair(n, fg, bg)
    stdscr.bkgd(" ", curses.color_pair(4))

def ask_secret(stdscr, prompt):
    hot = globals().get("_hot")
    saved = (hot.get("row", -1), list(hot.get("zones", []))) if hot is not None else None
    buf = ""
    m = re.search(r"\((\d+) essais?\)", prompt)
    left = max(0, min(3, int(m.group(1)))) if m else None
    label = re.sub(r"\s*\(\d+ essais?\)", "", prompt).rstrip(" :")
    try:
        curses.curs_set(0)
    except curses.error:
        pass
    try:
        stdscr.timeout(-1)
        while True:
            stdscr.erase()
            my, mx = stdscr.getmaxyx()
            pad = mx >= 30 and my >= 16 and bool(globals().get("_st", {}).get("mouse"))
            pitch = 3 if my >= 28 else 2
            total = 10 + (4 * pitch if pad else 0)
            y = max(0, (my - total) // 2)
            fw = max(20, min(mx - 2, 34))
            x0 = max(0, (mx - fw) // 2)
            A1 = curses.color_pair(1) | curses.A_BOLD
            A3 = curses.color_pair(3)
            A4 = curses.color_pair(4)
            zones = []
            try:
                stdscr.addstr(y, x0, "╭" + "─" * (fw - 2) + "╮", A3)
                for r in range(1, total - 1):
                    stdscr.addstr(y + r, x0, "│", A3)
                    stdscr.addstr(y + r, x0 + fw - 1, "│", A3)
                stdscr.addstr(y + total - 1, x0, "╰" + "─" * (fw - 2) + "╯", A3)

                def c(row, text, attr):
                    stdscr.addstr(y + row, x0 + max(1, (fw - len(text)) // 2), text[:fw - 2], attr)

                c(1, "◆ ABOUDEV LABS ◆", A1)
                c(2, label, A4)
                shown = buf[-((fw - 6) // 2):]
                slots = max(4, len(shown))
                c(4, " ".join(["●"] * len(shown) + ["○"] * (slots - len(shown))), A1)
                if left is not None:
                    c(5, " ".join(["♥"] * left + ["♡"] * (3 - left)), A3)
                    if left < 3:
                        c(6, "✗ PIN incorrect", curses.A_BOLD)
                if pad:
                    px0 = x0 + (fw - 24) // 2
                    keys = (("1", "2", "3"), ("4", "5", "6"), ("7", "8", "9"),
                            ("⌫", "0", "OK"))
                    for ri, row in enumerate(keys):
                        for ci, lab in enumerate(row):
                            bx = px0 + ci * 8
                            by = y + 8 + ri * pitch
                            a = A4 | curses.A_REVERSE
                            if pitch == 3:
                                stdscr.addstr(by, bx, " " * 7, a)
                                stdscr.addstr(by + 1, bx, lab.center(7), a | curses.A_BOLD)
                            else:
                                stdscr.addstr(by, bx, lab.center(7), a | curses.A_BOLD)
                            v = curses.KEY_BACKSPACE if lab == "⌫" else ("\n" if lab == "OK" else lab)
                            zones.append((by, by + pitch - 1, bx, bx + 8, v))
                c(total - 2, "Entrée valider · Esc annuler", A3 | curses.A_DIM)
            except curses.error:
                pass
            if hot is not None:
                hot["zones"] = zones
                hot["row"] = -10
            stdscr.refresh()
            k = stdscr.get_wch()
            if k in (27, "\x1b"):
                return None
            if k in ("\n", "\r", curses.KEY_ENTER):
                return buf
            if k in (curses.KEY_BACKSPACE, "\x7f", "\b", 127, 8):
                buf = buf[:-1]
            elif isinstance(k, str) and k.isprintable() and len(buf) < 64:
                buf += k
    finally:
        if hot is not None and saved is not None:
            hot["row"], hot["zones"] = saved
        try:
            curses.curs_set(1)
        except curses.error:
            pass
        stdscr.erase()
        stdscr.refresh()

def _pin_hash(pin, salt):
    return hashlib.pbkdf2_hmac("sha256", pin.encode(), salt, 200000).hex()

def _pin_load():
    try:
        with open(PIN_FILE) as f:
            c = json.load(f)
        return c if c.get("salt") and c.get("hash") else None
    except Exception:
        return None

def _pin_ok(pin, cfg):
    return hmac.compare_digest(_pin_hash(pin, bytes.fromhex(cfg["salt"])), cfg["hash"])

def _pin_save(pin):
    salt = secrets.token_bytes(16)
    with open(PIN_FILE, "w") as f:
        json.dump({"salt": salt.hex(), "hash": _pin_hash(pin, salt)}, f)
    os.chmod(PIN_FILE, 0o600)

def pin_gate(stdscr):
    cfg = _pin_load()
    if not cfg:
        return True
    for essai in range(3):
        pin = ask_secret(stdscr, f"PIN ({3 - essai} essais) :")
        if pin is None:
            return False
        if _pin_ok(pin, cfg):
            return True
    return False

def _openssl(data, pw, decrypt=False):
    r, w = os.pipe()
    os.write(w, pw.encode() + b"\n")
    os.close(w)
    cmd = ["openssl", "enc", "-aes-256-cbc", "-salt", "-pbkdf2",
           "-iter", "200000", "-pass", f"fd:{r}"]
    if decrypt:
        cmd.insert(2, "-d")
    try:
        out = subprocess.run(cmd, input=data, capture_output=True,
                             pass_fds=(r,), timeout=30)
    finally:
        os.close(r)
    if out.returncode != 0:
        raise ValueError("openssl")
    return out.stdout

def _backup(stdscr, share):
    if not shutil.which("openssl"):
        return "⚠  pkg install openssl-tool"
    p1 = ask_secret(stdscr, "Mot de passe (6+ car.) :")
    if p1 is None:
        return "annulé"
    if len(p1) < 6:
        return "⚠  mot de passe trop court"
    if ask_secret(stdscr, "Confirme le mot de passe :") != p1:
        return "⚠  mots de passe différents"
    payload = json.dumps({"calc": 1, "data": _load(), "taux": TAUX},
                         ensure_ascii=False).encode()
    try:
        blob = _openssl(payload, p1)
    except Exception:
        return "⚠  échec du chiffrement"
    os.makedirs(BACKUP_DIR, exist_ok=True)
    name = f"calc_{datetime.now():%y%m%d_%H%M%S}.enc"
    path = os.path.join(BACKUP_DIR, name)
    with open(path, "wb") as f:
        f.write(blob)
    if os.path.isdir(SHARE_DIR):
        try:
            shutil.copy(path, os.path.join(SHARE_DIR, name))
        except OSError:
            pass
    if share and shutil.which("termux-share"):
        try:
            subprocess.run(["termux-share", "-a", "send", path],
                           capture_output=True, timeout=15)
            return f"partagée : {name}"
        except Exception:
            pass
    return f"chiffrée : {name}"

def _restore(stdscr, name):
    if not shutil.which("openssl"):
        return "⚠  pkg install openssl-tool"
    if name:
        n = os.path.basename(name)
        cands = [os.path.join(d, n) for d in (BACKUP_DIR, SHARE_DIR)]
    else:
        fs = []
        for d in (BACKUP_DIR, SHARE_DIR):
            if os.path.isdir(d):
                fs += [os.path.join(d, f) for f in os.listdir(d)
                       if f.startswith("calc_") and f.endswith(".enc")]
        cands = sorted(fs, key=os.path.getmtime, reverse=True)[:1]
    path = next((c for c in cands if os.path.isfile(c)), None)
    if not path:
        return "⚠  fichier introuvable"
    pw = ask_secret(stdscr, "Mot de passe :")
    if pw is None:
        return "annulé"
    try:
        with open(path, "rb") as f:
            blob = f.read()
        obj = json.loads(_openssl(blob, pw, decrypt=True).decode())
        if obj.get("calc") != 1 or not isinstance(obj["data"], dict):
            raise ValueError("format")
        data = obj["data"]
        taux = {k: float(v) for k, v in obj["taux"].items() if k in TAUX}
    except Exception:
        return "⚠  mot de passe ou fichier invalide"
    try:
        if os.path.exists(DATA_FILE):
            shutil.copy(DATA_FILE, DATA_FILE + ".avant_restauration")
    except OSError:
        pass
    _save(data)
    TAUX.update(taux)
    with open(TAUX_FILE, "w") as f:
        json.dump(TAUX, f)
    return f"restauré : {os.path.basename(path)}"

def _lot3(expr, stdscr=None, apply=False):
    e = expr.strip()
    low = e.lower()
    m = re.fullmatch(r"theme\s+(sombre|clair)", low)
    if m:
        t = m.group(1)
        if not apply:
            return f"Entrée pour le thème {t}"
        c = _conf_load()
        c["theme"] = t
        _conf_save(c)
        apply_theme(stdscr)
        return f"thème {t} activé"
    if low in ("pin", "pin off"):
        off = low == "pin off"
        if not apply:
            return "Entrée pour " + ("retirer le PIN" if off else "définir un PIN")
        cfg = _pin_load()
        if cfg:
            cur = ask_secret(stdscr, "PIN actuel :")
            if cur is None or not _pin_ok(cur, cfg):
                return "⚠  PIN incorrect"
        if off:
            try:
                os.remove(PIN_FILE)
            except OSError:
                pass
            return "PIN retiré"
        p1 = ask_secret(stdscr, "Nouveau PIN (4-8 chiffres) :")
        if p1 is None:
            return "annulé"
        if not re.fullmatch(r"\d{4,8}", p1):
            return "⚠  PIN : 4 à 8 chiffres"
        if ask_secret(stdscr, "Confirme le PIN :") != p1:
            return "⚠  les PIN diffèrent"
        _pin_save(p1)
        return "PIN enregistré"
    if low in ("sauvegarde", "export"):
        share = low == "export"
        if not apply:
            return "Entrée : sauvegarde chiffrée" + (" + partage" if share else "")
        return _backup(stdscr, share)
    m = re.fullmatch(r"restaure(?:\s+([\w.\-]+))?", e, re.I)
    if m:
        if not apply:
            return "Entrée : restaurer (remplace tout)"
        return _restore(stdscr, m.group(1))
    return None

def try_lot3(expr, stdscr=None, apply=False):
    if apply and stdscr is None:
        return None
    try:
        return _lot3(expr, stdscr, apply)
    except Exception:
        return "⚠  erreur" if apply else None

