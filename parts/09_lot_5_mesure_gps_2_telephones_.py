# ─── Lot 5 : mesure (GPS, 2 téléphones, terrain, hauteur) ──────────────────
import socket, ipaddress
PORT = 48765
R_TERRE = 6371000.0

def _status(stdscr, lignes):
    stdscr.erase()
    for i, t in enumerate(lignes):
        try:
            stdscr.addstr(2 + i, 2, t[:stdscr.getmaxyx()[1] - 4], curses.color_pair(1))
        except curses.error:
            pass
    stdscr.refresh()

def _gps(stdscr, label):
    """Position via Termux:API : (lat, lon, précision en m) ou None."""
    if not shutil.which("termux-location"):
        return None
    _status(stdscr, [label, "(quelques secondes, dehors c'est mieux)"])
    for prov in ("gps", "network"):
        try:
            out = subprocess.run(["termux-location", "-p", prov, "-r", "once"],
                                 capture_output=True, timeout=30)
            d = json.loads(out.stdout.decode())
            return float(d["latitude"]), float(d["longitude"]), float(d.get("accuracy", 0))
        except Exception:
            continue
    return None

def _dist(a, b):
    p1, p2 = math.radians(a[0]), math.radians(b[0])
    dp, dl = p2 - p1, math.radians(b[1] - a[1])
    h = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * R_TERRE * math.asin(math.sqrt(h))

def _aire(pts):
    lat0 = sum(q[0] for q in pts) / len(pts)
    lon0 = sum(q[1] for q in pts) / len(pts)
    xy = [(R_TERRE * math.radians(q[1] - lon0) * math.cos(math.radians(lat0)),
           R_TERRE * math.radians(q[0] - lat0)) for q in pts]
    a = per = 0.0
    for i in range(len(xy)):
        x1, y1 = xy[i]
        x2, y2 = xy[(i + 1) % len(xy)]
        a += x1 * y2 - x2 * y1
        per += math.hypot(x2 - x1, y2 - y1)
    return abs(a) / 2, per

def _mon_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("10.255.255.255", 1))
        return s.getsockname()[0]
    except OSError:
        return "?"
    finally:
        s.close()

def _set_derniere(txt):
    d = _load()
    d["derniere"] = txt
    _save(d)

def _mesure_serveur(stdscr):
    pos = _gps(stdscr, "Position de ce téléphone (point B)…")
    if not pos:
        return "⚠  position indisponible (Termux:API ?)"
    code = f"{secrets.randbelow(10000):04d}"
    ip = _mon_ip()
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        srv.bind(("", PORT))
        srv.listen(1)
        srv.settimeout(1.0)
    except OSError:
        srv.close()
        return "⚠  port occupé"
    t0, essais = time.time(), 0
    stdscr.nodelay(True)
    try:
        while time.time() - t0 < 120 and essais < 3:
            _status(stdscr, ["Point B : en attente de l'autre téléphone",
                             f"IP   : {ip}", f"CODE : {code}", "",
                             "Sur l'autre téléphone :",
                             f"mesure connecte {ip} {code}", "", "Esc = annuler"])
            try:
                k = stdscr.get_wch()
                if k in (27, "\x1b"):
                    return "annulé"
            except curses.error:
                pass
            try:
                conn, _ = srv.accept()
            except socket.timeout:
                continue
            with conn:
                conn.settimeout(5)
                try:
                    data = conn.recv(64).decode(errors="ignore").strip()
                except Exception:
                    continue
                if hmac.compare_digest(data.encode(), ("calc1 " + code).encode()):
                    conn.sendall((json.dumps({"lat": pos[0], "lon": pos[1],
                                              "acc": pos[2]}) + "\n").encode())
                    return "position envoyée à l'autre téléphone"
                conn.sendall(b"NO\n")
                essais += 1
        return "⚠  délai dépassé ou trop d'essais"
    finally:
        srv.close()
        stdscr.timeout(-1)

def _mesure_client(stdscr, ip, code):
    try:
        if not ipaddress.ip_address(ip).is_private:
            return "⚠  adresse locale seulement"
    except ValueError:
        return "⚠  IP invalide"
    mine = _gps(stdscr, "Position de ce téléphone (point A)…")
    if not mine:
        return "⚠  position indisponible (Termux:API ?)"
    _status(stdscr, ["Connexion à l'autre téléphone…"])
    try:
        with socket.create_connection((ip, PORT), timeout=8) as sk:
            sk.settimeout(8)
            sk.sendall(f"calc1 {code}".encode())
            data = sk.recv(512).decode(errors="ignore").strip()
    except Exception:
        return "⚠  connexion impossible (même Wi-Fi ?)"
    try:
        o = json.loads(data)
        other = (float(o["lat"]), float(o["lon"]), float(o.get("acc", 0)))
    except Exception:
        return "⚠  code incorrect"
    dist = _dist(mine, other)
    err = math.hypot(mine[2], other[2])
    txt = f"{smart_format(round(dist, 1))} m"
    _set_derniere("distance " + txt)
    return f"distance {txt} (± {smart_format(round(err))} m)"

def _lot5(expr, stdscr=None, apply=False):
    low = expr.strip().lower().replace(",", ".")
    if not low or low.split()[0] not in ("mesure", "mesures", "point", "terrain", "hauteur"):
        return None
    num = r"(\d+(?:\.\d+)?)"
    if low == "mesure serveur":
        if not apply:
            return "Entrée : ce téléphone attend l'autre (B)"
        return _mesure_serveur(stdscr)
    m = re.fullmatch(r"mesure\s+connecte\s+(\d{1,3}(?:\.\d{1,3}){3})\s+(\d{4})", low)
    if m:
        if not apply:
            return f"Entrée pour se connecter à {m.group(1)}"
        return _mesure_client(stdscr, m.group(1), m.group(2))
    if low == "point":
        d = _load()
        pts = d.setdefault("points", [])
        if not apply:
            return f"Entrée : ajouter ma position ({len(pts)} points)"
        pos = _gps(stdscr, "Position du point…")
        if not pos:
            return "⚠  position indisponible (Termux:API ?)"
        pts.append(list(pos))
        _save(d)
        return f"point {len(pts)} noté (± {smart_format(round(pos[2]))} m)"
    if low == "terrain efface":
        n = len(_load().get("points", []))
        if not apply:
            return f"Entrée pour effacer {n} points"
        d = _load()
        d["points"] = []
        _save(d)
        return "points effacés"
    if low == "terrain":
        pts = _load().get("points", [])
        if len(pts) < 3:
            return f"⚠  {len(pts)} point(s), il en faut 3 ou plus"
        aire, per = _aire(pts)
        acc = sum(q[2] for q in pts) / len(pts)
        txt = f"{smart_format(round(aire, 1))} m²  périm. {smart_format(round(per))} m"
        if apply:
            _set_derniere(txt)
        return txt + f"  GPS±{smart_format(round(acc))}m"
    m = re.fullmatch(rf"hauteur\s+{num}\s+angle\s+{num}\s*°?(?:\s+oeil\s+{num})?", low)
    if m:
        dist, ang = float(m.group(1)), float(m.group(2))
        oeil = float(m.group(3)) if m.group(3) else 0.0
        if not 0 < ang < 90:
            return "⚠  angle entre 0 et 90"
        txt = f"hauteur {smart_format(round(dist * math.tan(math.radians(ang)) + oeil, 2))} m"
        if apply:
            _set_derniere(txt)
        return txt
    m = re.fullmatch(r"mesure\s+enregistre\s+(\w[\w-]*)", low)
    if m:
        d = _load()
        der = d.get("derniere")
        if not der:
            return "⚠  rien à enregistrer"
        if not apply:
            return f"Entrée : enregistrer {m.group(1)} = {der}"
        d.setdefault("mesures", []).append(
            {"d": f"{datetime.now():%Y-%m-%d}", "nom": m.group(1), "v": der})
        _save(d)
        return f"mesure {m.group(1)} enregistrée"
    if low == "mesures":
        ms = _load().get("mesures", [])
        return " ; ".join(f"{x['nom']} {x['v']}" for x in ms[-5:]) or "aucune mesure"
    return None

def try_lot5(expr, stdscr=None, apply=False):
    if apply and stdscr is None:
        return None
    try:
        return _lot5(expr, stdscr, apply)
    except Exception:
        return "⚠  erreur" if apply else None

