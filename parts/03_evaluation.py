# ─── Évaluation ────────────────────────────────────────────────────────────
def try_conversion(expr):
    """Détecte ex: '100 km to miles' ou '37 c to f'"""
    expr = expr.strip().lower()
    patterns = [
        (r"([\d.]+)\s*km\s*(to|en|->)\s*miles?",   "km_miles"),
        (r"([\d.]+)\s*miles?\s*(to|en|->)\s*km",    "miles_km"),
        (r"([\d.]+)\s*m\s*(to|en|->)\s*ft",         "m_ft"),
        (r"([\d.]+)\s*ft\s*(to|en|->)\s*m",         "ft_m"),
        (r"([\d.]+)\s*cm\s*(to|en|->)\s*inch",      "cm_inch"),
        (r"([\d.]+)\s*inch\s*(to|en|->)\s*cm",      "inch_cm"),
        (r"([\d.]+)\s*°?c\s*(to|en|->)\s*°?f",      "c_f"),
        (r"([\d.]+)\s*°?f\s*(to|en|->)\s*°?c",      "f_c"),
        (r"([\d.]+)\s*°?c\s*(to|en|->)\s*k",        "c_k"),
        (r"([\d.]+)\s*kg\s*(to|en|->)\s*lbs?",      "kg_lbs"),
        (r"([\d.]+)\s*lbs?\s*(to|en|->)\s*kg",      "lbs_kg"),
        (r"([\d.]+)\s*g\s*(to|en|->)\s*oz",         "g_oz"),
        (r"([\d.]+)\s*km/?h\s*(to|en|->)\s*mph",    "kmh_mph"),
        (r"([\d.]+)\s*mph\s*(to|en|->)\s*km/?h",    "mph_kmh"),
        (r"([\d.]+)\s*l\s*(to|en|->)\s*gal",        "l_gal"),
        (r"([\d.]+)\s*gal\s*(to|en|->)\s*l",        "gal_l"),
    ]
    for pattern, key in patterns:
        m = re.match(pattern, expr)
        if m:
            val = float(m.group(1))
            c = CONVERSIONS[key]
            result = c[2](val)
            return f"{val} {c[0]}  =  {smart_format(result)} {c[1]}"
    return None

def smart_format(n):
    """Formate intelligemment un nombre."""
    if isinstance(n, complex):
        return str(n)
    if isinstance(n, float) and (math.isinf(n) or math.isnan(n)):
        return str(n)
    if n == int(n) and abs(n) < 1e15:
        return str(int(n))
    # Arrondi propre
    formatted = f"{n:.10g}"
    return formatted

