# ─── Contexte mathématique sécurisé ────────────────────────────────────────
SAFE_MATH = {
    "sqrt": math.sqrt, "cbrt": lambda x: x**(1/3),
    "sin":  math.sin,  "cos":  math.cos,  "tan": math.tan,
    "asin": math.asin, "acos": math.acos, "atan": math.atan,
    "log":  math.log,  "log2": math.log2, "log10": math.log10,
    "exp":  math.exp,  "abs":  abs,       "round": round,
    "floor":math.floor,"ceil": math.ceil, "pow":   pow,
    "pi":   math.pi,   "e":    math.e,    "tau":   math.tau,
    "inf":  math.inf,
}

