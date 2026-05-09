"""
aqi_calculator.py
─────────────────
EPA AQI calculation from OpenWeatherMap component concentrations.

Unit notes (OWM API units → EPA breakpoint units):
  PM2.5  : µg/m³   → µg/m³   (no conversion needed)
  PM10   : µg/m³   → µg/m³   (no conversion needed)
  O3     : µg/m³   → ppb      divide by 1.9957  (MW 48 g/mol, 25°C)
  CO     : µg/m³   → ppm      divide by 1145.0  (MW 28 g/mol, 25°C)
  SO2    : µg/m³   → ppb      divide by 2.6178  (MW 64 g/mol, 25°C)
  NO2    : µg/m³   → ppb      divide by 1.8816  (MW 46 g/mol, 25°C)
"""
import logging

logger = logging.getLogger(__name__)

# ── EPA AQI Breakpoints ───────────────────────────────────────────────────────
# All concentrations in the units EPA uses (see header above).

BREAKPOINTS = {
    "pm2_5": [          # µg/m³
        (0.0,  12.0,   0,  50),
        (12.1, 35.4,  51, 100),
        (35.5, 55.4, 101, 150),
        (55.5,150.4, 151, 200),
        (150.5,250.4,201, 300),
        (250.5,500.4,301, 500),
    ],
    "pm10": [           # µg/m³
        (0,   54,   0,  50),
        (55,  154,  51, 100),
        (155, 254, 101, 150),
        (255, 354, 151, 200),
        (355, 424, 201, 300),
        (425, 604, 301, 500),
    ],
    "o3": [             # ppb  (convert from µg/m³ before lookup)
        (0,   54,   0,  50),
        (55,  70,  51, 100),
        (71,  85, 101, 150),
        (86, 105, 151, 200),
        (106,200, 201, 300),
    ],
    "co": [             # ppm  (convert from µg/m³ before lookup)
        (0.0,  4.4,   0,  50),
        (4.5,  9.4,  51, 100),
        (9.5, 12.4, 101, 150),
        (12.5,15.4, 151, 200),
        (15.5,30.4, 201, 300),
        (30.5,50.4, 301, 500),
    ],
    "so2": [            # ppb  (convert from µg/m³ before lookup)
        (0,   35,   0,  50),
        (36,  75,  51, 100),
        (76, 185, 101, 150),
        (186,304, 151, 200),
        (305,604, 201, 300),
        (605,1004,301, 500),
    ],
    "no2": [            # ppb  (convert from µg/m³ before lookup)
        (0,   53,   0,  50),
        (54,  100,  51, 100),
        (101, 360, 101, 150),
        (361, 649, 151, 200),
        (650,1249, 201, 300),
        (1250,2049,301, 500),
    ],
}

# Conversion factors: OWM µg/m³ → EPA unit
_CONV = {
    "pm2_5": 1.0,        # already µg/m³
    "pm10":  1.0,        # already µg/m³
    "o3":    1 / 1.9957, # µg/m³ → ppb
    "co":    1 / 1145.0, # µg/m³ → ppm
    "so2":   1 / 2.6178, # µg/m³ → ppb
    "no2":   1 / 1.8816, # µg/m³ → ppb
}


def _pollutant_aqi(concentration: float, pollutant: str) -> int | None:
    """Calculate sub-index AQI for one pollutant (EPA linear interpolation)."""
    if concentration is None or concentration < 0:
        return 0

    # Convert to EPA units
    conc = concentration * _CONV.get(pollutant, 1.0)

    table = BREAKPOINTS.get(pollutant)
    if not table:
        return None

    for (c_lo, c_hi, i_lo, i_hi) in table:
        if c_lo <= conc <= c_hi:
            aqi = (i_hi - i_lo) / (c_hi - c_lo) * (conc - c_lo) + i_lo
            return int(round(aqi))

    # Above highest breakpoint
    if conc > table[-1][1]:
        return 500
    return 0


def calculate_aqi(pollutants: dict) -> dict | None:
    """
    Calculate overall EPA AQI from a dict of OWM concentrations.

    Args:
        pollutants: dict with keys pm2_5, pm10, o3, co, so2, no2
                    values in µg/m³  (as returned by process_air_quality_data)

    Returns:
        {'aqi': int, 'dominant_pollutant': str, 'pollutant_aqi': dict}
        or None on failure.
    """
    try:
        sub_indices: dict[str, int] = {}
        for pollutant, conc in pollutants.items():
            if pollutant not in BREAKPOINTS:
                continue
            idx = _pollutant_aqi(conc, pollutant)
            if idx is not None:
                sub_indices[pollutant] = idx

        if not sub_indices:
            logger.warning("No valid pollutant concentrations for AQI.")
            return None

        dominant = max(sub_indices, key=sub_indices.get)
        overall  = sub_indices[dominant]

        return {
            "aqi":               overall,
            "dominant_pollutant": dominant,
            "pollutant_aqi":     sub_indices,
        }

    except Exception as exc:
        logger.error("AQI calculation error: %s", exc)
        return None