# ─── Le Gardien ────────────────────────────────────────────────────────────
class Interdit(Exception):
    pass

BIN_OPS = {ast.Add: operator.add, ast.Sub: operator.sub, ast.Mult: operator.mul,
           ast.Div: operator.truediv, ast.FloorDiv: operator.floordiv,
           ast.Mod: operator.mod, ast.Pow: operator.pow}
UN_OPS = {ast.UAdd: operator.pos, ast.USub: operator.neg}

def gardien_eval(expr):
    """Évalue seulement ce qui est autorisé. Jamais de eval()."""
    if len(expr) > 200:
        raise Interdit("trop long")
    tree = ast.parse(expr, mode="eval")

    def walk(n):
        if isinstance(n, ast.Expression):
            return walk(n.body)
        if isinstance(n, ast.Constant) and type(n.value) in (int, float, complex):
            return n.value
        if isinstance(n, ast.Name):
            if n.id.startswith("_"):
                raise Interdit("interdit")
            if n.id in SAFE_MATH:
                return SAFE_MATH[n.id]
            raise ValueError("inconnu")
        if isinstance(n, ast.UnaryOp) and type(n.op) in UN_OPS:
            return UN_OPS[type(n.op)](walk(n.operand))
        if isinstance(n, ast.BinOp) and type(n.op) in BIN_OPS:
            a, b = walk(n.left), walk(n.right)
            if isinstance(n.op, ast.Pow) and abs(b) > 1000:
                raise Interdit("trop grand")
            return BIN_OPS[type(n.op)](a, b)
        if isinstance(n, ast.Call) and not n.keywords:
            f = walk(n.func)
            if not callable(f):
                raise ValueError("pas une fonction")
            args = [walk(a) for a in n.args]
            if f is SAFE_MATH.get("fact") and args and args[0] > 500:
                raise Interdit("trop grand")
            return f(*args)
        raise Interdit("interdit")

    return walk(tree)

