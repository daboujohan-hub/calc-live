# ─── Conversions disponibles ───────────────────────────────────────────────
CONVERSIONS = {
    # Distance
    "km_miles":   ("km",   "miles",  lambda x: x * 0.621371),
    "miles_km":   ("miles","km",     lambda x: x * 1.60934),
    "m_ft":       ("m",    "ft",     lambda x: x * 3.28084),
    "ft_m":       ("ft",   "m",      lambda x: x / 3.28084),
    "cm_inch":    ("cm",   "inch",   lambda x: x / 2.54),
    "inch_cm":    ("inch", "cm",     lambda x: x * 2.54),
    # Température
    "c_f":        ("°C",   "°F",     lambda x: x * 9/5 + 32),
    "f_c":        ("°F",   "°C",     lambda x: (x - 32) * 5/9),
    "c_k":        ("°C",   "K",      lambda x: x + 273.15),
    # Poids
    "kg_lbs":     ("kg",   "lbs",    lambda x: x * 2.20462),
    "lbs_kg":     ("lbs",  "kg",     lambda x: x / 2.20462),
    "g_oz":       ("g",    "oz",     lambda x: x / 28.3495),
    # Vitesse
    "kmh_mph":    ("km/h", "mph",    lambda x: x * 0.621371),
    "mph_kmh":    ("mph",  "km/h",   lambda x: x * 1.60934),
    # Volume
    "l_gal":      ("L",    "gal",    lambda x: x * 0.264172),
    "gal_l":      ("gal",  "L",      lambda x: x / 0.264172),
}

