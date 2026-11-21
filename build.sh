#!/data/data/com.termux/files/usr/bin/bash
cd "$(dirname "$0")" || exit 1
cat parts/*.py > "$TMPDIR/calc_build.py" || exit 1
python -m py_compile "$TMPDIR/calc_build.py" || { echo "❌ erreur de syntaxe"; exit 1; }
rm -f ~/.local/bin/calc.py
cp "$TMPDIR/calc_build.py" ~/.local/bin/calc.py
chmod +x ~/.local/bin/calc.py
echo "✅ calc autonome : $(wc -l < ~/.local/bin/calc.py) lignes"
