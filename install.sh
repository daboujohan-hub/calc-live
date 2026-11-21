#!/usr/bin/env bash
# Installeur de CALC (calc-live) · by AbouDev Labs
set -e
NOM="calc-live"
SRC="$(cd "$(dirname "$0")" && pwd)"

if echo "${PREFIX:-}" | grep -q termux && [ -d "$PREFIX/bin" ]; then
    BIN="$PREFIX/bin"; DATA="$PREFIX/share/$NOM"; TERMUX=1
else
    BIN="$HOME/.local/bin"; DATA="$HOME/.local/share/$NOM"; TERMUX=0
fi

if [ "${1:-}" = "--remove" ]; then
    rm -rf "$DATA" "$BIN/$NOM"
    echo "✅ $NOM désinstallé (tes données personnelles sont conservées)"
    exit 0
fi

[ -f "$SRC/calc.py" ] || { echo "⚠  calc.py introuvable à côté de install.sh"; exit 1; }

if ! command -v python3 >/dev/null 2>&1 && ! command -v python >/dev/null 2>&1; then
    if [ "$TERMUX" = 1 ]; then pkg install -y python
    else echo "⚠  Installe Python 3.9 ou plus"; exit 1; fi
fi
PY="$(command -v python3 || command -v python)"
"$PY" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)' \
    || { echo "⚠  Python 3.9 ou plus requis"; exit 1; }
"$PY" -c 'import curses' 2>/dev/null \
    || { echo "⚠  module curses manquant"; exit 1; }

if ! command -v openssl >/dev/null 2>&1; then
    if [ "$TERMUX" = 1 ]; then pkg install -y openssl-tool
    else echo "ℹ  openssl absent : la sauvegarde chiffrée sera indisponible"; fi
fi
if [ "$TERMUX" = 1 ] && ! command -v termux-location >/dev/null 2>&1; then
    echo "ℹ  Facultatif (mesures GPS) : pkg install termux-api + app Termux:API"
fi

mkdir -p "$DATA" "$BIN"
cp "$SRC/calc.py" "$DATA/calc.py"
cat > "$BIN/$NOM" <<EOF2
#!/bin/sh
exec "$PY" "$DATA/calc.py" "\$@"
EOF2
chmod +x "$BIN/$NOM"

echo "✅ Installé : tape  $NOM"
case ":$PATH:" in *":$BIN:"*) ;; *) echo "ℹ  Ajoute $BIN à ton PATH" ;; esac
