"""V-plotter (iki ipli duvar çizim robotu) kinematiği ve G-code benzeri yol üretimi."""
import math

D = 800.0          # iki motor arası mesafe (mm)
MAKARA_CEVRE = 40.0  # mm/tur
ADIM_TUR = 200 * 8


def ip_boylari(x: float, y: float) -> tuple[float, float]:
    """Kalem (x, y) -> sol ve sağ ip uzunlukları. Orijin sol motor, y aşağı doğru."""
    return math.hypot(x, y), math.hypot(D - x, y)


def konum(l1: float, l2: float) -> tuple[float, float]:
    """İp boylarından kalem konumu (iki çember kesişimi)."""
    x = (l1**2 - l2**2 + D**2) / (2 * D)
    return x, math.sqrt(max(l1**2 - x**2, 0.0))


def cizgi(p0, p1, adim_mm=1.0):
    """Doğruyu küçük parçalara böler (ipler doğrusal olmadığından şart)."""
    n = max(1, int(math.dist(p0, p1) / adim_mm))
    for i in range(n + 1):
        t = i / n
        yield p0[0] + (p1[0] - p0[0]) * t, p0[1] + (p1[1] - p0[1]) * t


def kare_ciz(merkez=(400, 400), kenar=200):
    cx, cy, h = *merkez, kenar / 2
    koseler = [(cx - h, cy - h), (cx + h, cy - h), (cx + h, cy + h), (cx - h, cy + h), (cx - h, cy - h)]
    onceki = ip_boylari(*koseler[0])
    for p0, p1 in zip(koseler, koseler[1:]):
        for x, y in cizgi(p0, p1, 5):
            l1, l2 = ip_boylari(x, y)
            d1 = round((l1 - onceki[0]) / MAKARA_CEVRE * ADIM_TUR)
            d2 = round((l2 - onceki[1]) / MAKARA_CEVRE * ADIM_TUR)
            onceki = (onceki[0] + d1 * MAKARA_CEVRE / ADIM_TUR, onceki[1] + d2 * MAKARA_CEVRE / ADIM_TUR)
            yield d1, d2


if __name__ == "__main__":
    l1, l2 = ip_boylari(300, 500)
    print(f"(300,500) -> L1={l1:.1f} L2={l2:.1f} -> geri: {konum(l1, l2)}")
    adimlar = list(kare_ciz())
    print(f"Kare için {len(adimlar)} segment, ilk 5: {adimlar[:5]}")
