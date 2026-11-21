#!/usr/bin/env python3
"""calc.py - chargeur : assemble parts/*.py dans un seul espace de noms."""
import os
_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), "parts")
for _name in sorted(os.listdir(_DIR)):
    if _name.endswith(".py"):
        _path = os.path.join(_DIR, _name)
        with open(_path, encoding="utf-8") as _f:
            exec(compile(_f.read(), _path, "exec"), globals())
