# TouchDesigner Script SOP - cook fonksiyonu
# Girdi: table_quakes (Table DAT, quakes_td.csv okunmus)
# Cikti: her deprem = 2 noktali dikey cubuk (taban + tepe)
# Attribute: mag (float), src (0=historic 1=recent 2=live)

# ===== OLCEK KATSAYILARI (tek yerden ayarla) =====
Y_MAX      = 20.0     # bina toplam yuksekligi
X_RANGE    = (-5.0, 5.0)
Z_RANGE    = (-3.0, 3.0)
LON_MIN, LON_MAX = 26.5, 30.2
LAT_MIN, LAT_MAX = 40.3, 41.2
BAR_K1     = 0.05     # cubuk boyu: BAR_K1 * 10^(mag*BAR_K2)
BAR_K2     = 0.30
# kalinlik attribute olarak gider, MAT/SOP tarafinda kullanilir
# ================================================

SRC_MAP = {"historic": 0, "recent": 1, "live": 2}


def remap(v, a, b, c, d):
    if b - a == 0:
        return c
    return c + (d - c) * (v - a) / (b - a)


def cook(scriptOp):
    scriptOp.clear()
    tbl = op('table_quakes')
    n = tbl.numRows - 1  # baslik haric
    if n <= 0:
        return

    # attribute tanimlari
    scriptOp.appendPointAttrib('mag', 0.0)
    scriptOp.appendPointAttrib('src', 0)
    scriptOp.appendPointAttrib('thick', 0.0)

    for i in range(1, tbl.numRows):
        try:
            idx   = float(tbl[i, 'idx'].val)
            lon   = float(tbl[i, 'lon'].val)
            lat   = float(tbl[i, 'lat'].val)
            mag   = float(tbl[i, 'mag'].val)
            src_s = tbl[i, 'source'].val
        except (ValueError, AttributeError):
            continue

        src = SRC_MAP.get(src_s, 0)

        x = remap(lon, LON_MIN, LON_MAX, X_RANGE[0], X_RANGE[1])
        z = remap(lat, LAT_MIN, LAT_MAX, Z_RANGE[0], Z_RANGE[1])
        y_base = remap(idx, 0, n - 1, 0.0, Y_MAX)

        bar = BAR_K1 * (10.0 ** (mag * BAR_K2))
        y_top = y_base + bar
        thick = 0.01 + mag * 0.012

        # iki nokta + bir cizgi (poly)
        p0 = scriptOp.appendPoint()
        p0.x, p0.y, p0.z = x, y_base, z
        p0.mag, p0.src, p0.thick = mag, src, thick

        p1 = scriptOp.appendPoint()
        p1.x, p1.y, p1.z = x, y_top, z
        p1.mag, p1.src, p1.thick = mag, src, thick

        poly = scriptOp.appendPoly(2, closed=False, addPoints=False)
        poly[0].point = p0
        poly[1].point = p1

    return
