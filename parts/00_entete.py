#!/usr/bin/env python3
"""
calc.py — Calculatrice live pour Termux
Ctrl+K pour ouvrir depuis .bashrc
"""

import ast
import curses
import operator
import math
import re
from collections import deque
import os
os.environ.setdefault("ESCDELAY", "25")

