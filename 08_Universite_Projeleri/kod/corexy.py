"""CoreXY kinematiği: kartezyen (X, Y) <-> motor (A, B) dönüşümleri."""


def ters(x: float, y: float) -> tuple[float, float]:
    """Hedef XY'den motor konumları (mm cinsinden kayış hareketi)."""
    return x + y, x - y


def ileri(a: float, b: float) -> tuple[float, float]:
    """Motor konumlarından XY."""
    return (a + b) / 2, (a - b) / 2


def mm_to_adim(mm: float, adim_tur=200, mikro=16, dis=20, hatve=2.0) -> int:
    """GT2 kayış (2 mm hatve) + 20 dişli kasnak: 1 tur = 40 mm."""
    return round(mm * adim_tur * mikro / (dis * hatve))


if __name__ == "__main__":
    for hedef in [(0, 0), (100, 0), (0, 100), (50, 50)]:
        a, b = ters(*hedef)
        assert ileri(a, b) == hedef
        print(f"XY={hedef} -> A={a:6.1f} mm ({mm_to_adim(a)} adım), "
              f"B={b:6.1f} mm ({mm_to_adim(b)} adım)")
