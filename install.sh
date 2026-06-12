#!/data/data/com.termux/files/usr/bin/bash
# ─────────────────────────────────────────────────────────────
#  install.sh — Installation de la calculatrice live pour Termux
# ─────────────────────────────────────────────────────────────

echo ""
echo "⚡  Installation de calc — Calculatrice Live"
echo "────────────────────────────────────────────"

# 1. Copier le script dans un dossier accessible
mkdir -p ~/.local/bin
cp calc.py ~/.local/bin/calc.py
chmod +x ~/.local/bin/calc.py

# 2. Créer la commande 'calc'
cat > ~/.local/bin/calc << 'EOF'
#!/data/data/com.termux/files/usr/bin/bash
python3 ~/.local/bin/calc.py
EOF
chmod +x ~/.local/bin/calc

# 3. Ajouter ~/.local/bin au PATH si pas déjà là
if ! grep -q 'local/bin' ~/.bashrc; then
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
fi

# 4. Ajouter le raccourci Ctrl+K dans .bashrc
if ! grep -q 'bind.*calc' ~/.bashrc; then
    cat >> ~/.bashrc << 'BASHRC'

# ── Calculatrice live : Ctrl+K ──────────────────────────────
_open_calc() {
    echo ""
    python3 ~/.local/bin/calc.py
    echo ""
}
export -f _open_calc
bind -x '"\C-k":"_open_calc"'
# ────────────────────────────────────────────────────────────
BASHRC
fi

echo ""
echo "✅  Installation terminée !"
echo ""
echo "  Pour activer maintenant :  source ~/.bashrc"
echo "  Puis utilise :             Ctrl+K  (n'importe quand dans Termux)"
echo "  Ou lance directement :     calc"
echo ""
