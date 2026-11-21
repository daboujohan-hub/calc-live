# ─── Lot 4 : coffre caché ──────────────────────────────────────────────────
import time
COFFRE_CONF = os.path.expanduser("~/.calc_coffre.json")
COFFRE_DIRS = {"vrai": os.path.expanduser("~/.calc_coffre"),
               "faux": os.path.expanduser("~/.calc_coffre_faux")}
COFFRE_TMP = os.path.expanduser("~/.calc_coffre_tmp")
SHARED = os.path.expanduser("~/storage/shared")
IDLE_LOCK = 60

def _cf_load():
    try:
        with open(COFFRE_CONF) as f:
            return json.load(f)
    except Exception:
        return {}

def _cf_save(c):
    with open(COFFRE_CONF, "w") as f:
        json.dump(c, f)
    os.chmod(COFFRE_CONF, 0o600)

def _cf_hash(code, salt):
    return hashlib.pbkdf2_hmac("sha256", code.encode(), salt, 50000).hex()

def _cf_set(c, which, code):
    salt = secrets.token_bytes(16)
    c[which] = {"salt": salt.hex(), "hash": _cf_hash(code, salt)}

def _cf_match(c, which, code):
    e = c.get(which)
    if not e:
        return False
    return hmac.compare_digest(_cf_hash(code, bytes.fromhex(e["salt"])), e["hash"])

def _ssl_file(src, dst, pw, decrypt=False):
    r, w = os.pipe()
    os.write(w, pw.encode() + b"\n")
    os.close(w)
    cmd = ["openssl", "enc", "-aes-256-cbc", "-salt", "-pbkdf2", "-iter", "200000",
           "-pass", f"fd:{r}", "-in", src, "-out", dst]
    if decrypt:
        cmd.insert(2, "-d")
    try:
        res = subprocess.run(cmd, capture_output=True, pass_fds=(r,), timeout=900)
    finally:
        os.close(r)
    if res.returncode != 0:
        try:
            os.remove(dst)
        except OSError:
            pass
        raise ValueError("openssl")

def _idx_load(d, pw):
    p = os.path.join(d, "index.enc")
    if not os.path.isfile(p):
        return {}
    with open(p, "rb") as f:
        return json.loads(_openssl(f.read(), pw, decrypt=True).decode())

def _idx_save(d, pw, idx):
    os.makedirs(d, exist_ok=True)
    os.chmod(d, 0o700)
    with open(os.path.join(d, "index.enc"), "wb") as f:
        f.write(_openssl(json.dumps(idx, ensure_ascii=False).encode(), pw))

def _h(n):
    for u in ("o", "Ko", "Mo", "Go"):
        if n < 1024:
            return f"{n:.0f}{u}"
        n /= 1024
    return f"{n:.1f}To"

def _resolve(path):
    p = os.path.expanduser(path.strip().strip("'\""))
    for c in (p, os.path.join(SHARED, p)):
        if os.path.isfile(c):
            return c
    return None

def _unique(path):
    base, ext = os.path.splitext(path)
    n, p = 1, path
    while os.path.exists(p):
        n += 1
        p = f"{base}_{n}{ext}"
    return p

def _vault_cmd(cmd, d, pw, idx):
    ids = sorted(idx, key=lambda k: idx[k]["t"])
    m = re.fullmatch(r"ajoute\s+(.+)", cmd, re.I)
    if m:
        src = _resolve(m.group(1))
        if not src:
            return "⚠  fichier introuvable"
        fid = secrets.token_hex(8)
        os.makedirs(d, exist_ok=True)
        os.chmod(d, 0o700)
        dst = os.path.join(d, fid + ".enc")
        try:
            _ssl_file(src, dst, pw)
            if os.path.getsize(dst) == 0:
                raise ValueError("vide")
        except Exception:
            return "⚠  échec du chiffrement"
        idx[fid] = {"nom": os.path.basename(src), "t": time.time(),
                    "taille": os.path.getsize(src)}
        _idx_save(d, pw, idx)
        try:
            os.remove(src)
            return "ajouté, original supprimé"
        except OSError:
            return "ajouté (⚠ original non supprimé)"
    m = re.fullmatch(r"(voir|rend|supprime)\s+(\d+)(\s+oui)?", cmd.lower())
    if m:
        n = int(m.group(2))
        if not 1 <= n <= len(ids):
            return "⚠  numéro inconnu"
        fid = ids[n - 1]
        safe = os.path.basename(idx[fid]["nom"]) or "fichier"
        enc = os.path.join(d, fid + ".enc")
        if m.group(1) == "supprime":
            if not m.group(3):
                return f"confirme : supprime {n} oui"
            try:
                os.remove(enc)
            except OSError:
                pass
            del idx[fid]
            _idx_save(d, pw, idx)
            return "supprimé"
        if m.group(1) == "voir":
            os.makedirs(COFFRE_TMP, mode=0o700, exist_ok=True)
            out = os.path.join(COFFRE_TMP, safe)
            _ssl_file(enc, out, pw, decrypt=True)
            if shutil.which("termux-open"):
                subprocess.Popen(["termux-open", out], stdout=subprocess.DEVNULL,
                                 stderr=subprocess.DEVNULL)
                return "ouverture… (effacé à la fermeture)"
            return "⚠  termux-open absent, utilise rend"
        dest = SHARE_DIR if os.path.isdir(SHARE_DIR) else os.path.expanduser("~/coffre_sortie")
        os.makedirs(dest, exist_ok=True)
        out = _unique(os.path.join(dest, safe))
        _ssl_file(enc, out, pw, decrypt=True)
        os.remove(enc)
        del idx[fid]
        _idx_save(d, pw, idx)
        return "rendu : " + out.replace(os.path.expanduser("~"), "~")
    return "ajoute CHEMIN | voir N | rend N | supprime N oui"

def vault_screen(stdscr, which, pw):
    d = COFFRE_DIRS[which]
    try:
        idx = _idx_load(d, pw)
    except Exception:
        idx = {}
    msg = "ajoute CHEMIN | voir N | rend N | supprime N"
    buf, last = "", time.time()
    curses.curs_set(1)
    stdscr.timeout(1000)
    try:
        while True:
            ids = sorted(idx, key=lambda k: idx[k]["t"])
            stdscr.erase()
            my, mx = stdscr.getmaxyx()
            try:
                stdscr.addstr(1, 1, "COFFRE", curses.color_pair(1) | curses.A_BOLD)
                if not ids:
                    stdscr.addstr(3, 1, "(vide)", curses.color_pair(4))
                for i, fid in enumerate(ids[:max(0, my - 9)]):
                    e = idx[fid]
                    line = f"{i + 1}. {e['nom']} ({_h(e['taille'])})"
                    stdscr.addstr(3 + i, 1, line[:mx - 2], curses.color_pair(3))
                stdscr.addstr(my - 5, 1, msg[:mx - 2], curses.color_pair(2))
                stdscr.addstr(my - 3, 1, ("› " + buf)[-(mx - 2):],
                              curses.color_pair(4) | curses.A_BOLD)
                stdscr.addstr(my - 2, 1, "Esc = fermer"[:mx - 2], curses.color_pair(4))
                stdscr.move(my - 3, min(mx - 2, 3 + len(buf)))
            except curses.error:
                pass
            stdscr.refresh()
            try:
                k = stdscr.get_wch()
            except curses.error:
                if time.time() - last > IDLE_LOCK:
                    break
                continue
            last = time.time()
            if k in (27, "\x1b"):
                break
            if k in ("\n", "\r"):
                cmd, buf = buf.strip(), ""
                if cmd.lower() in ("fermer", "quitter", "q"):
                    break
                try:
                    msg = _vault_cmd(cmd, d, pw, idx)
                except Exception:
                    msg = "⚠  erreur"
            elif k in (curses.KEY_BACKSPACE, "\x7f", "\b"):
                buf = buf[:-1]
            elif isinstance(k, str) and k.isprintable():
                buf += k
    finally:
        stdscr.timeout(-1)
        shutil.rmtree(COFFRE_TMP, ignore_errors=True)

def coffre_check(stdscr, code):
    """Appelé à chaque Entrée : le code ouvre le coffre (ou efface si panique)."""
    if len(code) < 6:
        return False
    c = _cf_load()
    if not c:
        return False
    if _cf_match(c, "panique", code):
        shutil.rmtree(COFFRE_DIRS["vrai"], ignore_errors=True)
        shutil.rmtree(COFFRE_TMP, ignore_errors=True)
        return True
    for which in ("vrai", "faux"):
        if _cf_match(c, which, code):
            try:
                vault_screen(stdscr, which, code)
            except Exception:
                pass
            curses.curs_set(1)
            return True
    return False

def _lot4(expr, stdscr=None, apply=False):
    m = re.fullmatch(r"coffre(?:\s+(code|faux|panique))?", expr.strip().lower())
    if not m:
        return None
    nom = m.group(1)
    c = _cf_load()
    if nom is None:
        return "coffre : " + ", ".join(
            f"{n} {'oui' if k in c else 'non'}"
            for n, k in (("code", "vrai"), ("faux", "faux"), ("panique", "panique")))
    which = {"code": "vrai", "faux": "faux", "panique": "panique"}[nom]
    if not apply:
        return f"Entrée pour définir le code {nom}"
    if not shutil.which("openssl"):
        return "⚠  pkg install openssl-tool"
    if which in c:
        cur = ask_secret(stdscr, "Code actuel :")
        if cur is None or not _cf_match(c, which, cur):
            return "⚠  code incorrect"
    if which != "panique":
        d = COFFRE_DIRS[which]
        if os.path.isdir(d) and any(f.endswith(".enc") and f != "index.enc"
                                    for f in os.listdir(d)):
            return "⚠  vide d'abord le coffre"
    p1 = ask_secret(stdscr, "Nouveau code (6+ caractères) :")
    if p1 is None:
        return "annulé"
    if len(p1) < 6:
        return "⚠  6 caractères minimum"
    if which == "panique" and evaluate(p1):
        return "⚠  ajoute une lettre (pas un calcul)"
    if any(k != which and _cf_match(c, k, p1) for k in ("vrai", "faux", "panique")):
        return "⚠  code déjà utilisé"
    if ask_secret(stdscr, "Confirme le code :") != p1:
        return "⚠  les codes diffèrent"
    _cf_set(c, which, p1)
    _cf_save(c)
    return "code enregistré"

def try_lot4(expr, stdscr=None, apply=False):
    if apply and stdscr is None:
        return None
    try:
        return _lot4(expr, stdscr, apply)
    except Exception:
        return "⚠  erreur" if apply else None

