"""2 eksenli SCARA robot kol: ileri / ters kinematik ve çalışma alanı çizimi."""
import math

L1, L2 = 200.0, 150.0                      # kol boyları (mm)
T1_LIM = (-120, 120)                        # eklem limitleri (derece)
T2_LIM = (-145, 145)


def ileri(t1_deg: float, t2_deg: float) -> tuple[float, float]:
    t1, t2 = math.radians(t1_deg), math.radians(t2_deg)
    x = L1 * math.cos(t1) + L2 * math.cos(t1 + t2)
    y = L1 * math.sin(t1) + L2 * math.sin(t1 + t2)
    return x, y


def ters(x: float, y: float, dirsek_yukari=True) -> tuple[float, float]:
    c2 = (x * x + y * y - L1 * L1 - L2 * L2) / (2 * L1 * L2)
    if abs(c2) > 1:
        raise ValueError(f"({x:.1f}, {y:.1f}) çalışma alanı dışında")
    s2 = math.sqrt(1 - c2 * c2) * (1 if dirsek_yukari else -1)
    t2 = math.atan2(s2, c2)
    t1 = math.atan2(y, x) - math.atan2(L2 * s2, L1 + L2 * c2)
    return math.degrees(t1), math.degrees(t2)


def calisma_alani_ciz(dosya="../gorseller/scara_calisma_alani.png"):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np

    t1 = np.radians(np.linspace(*T1_LIM, 241))
    t2 = np.radians(np.linspace(*T2_LIM, 291))
    T1, T2 = np.meshgrid(t1, t2)
    X = L1 * np.cos(T1) + L2 * np.cos(T1 + T2)
    Y = L1 * np.sin(T1) + L2 * np.sin(T1 + T2)

    fig, ax = plt.subplots(figsize=(7, 6), dpi=110)
    ax.scatter(X, Y, s=0.3, c="#1f6feb", alpha=0.25, label="erişilebilir noktalar")
    ornek = (180, 120)
    for yukari, renk in [(True, "#c4302b"), (False, "#2da44e")]:
        a1, a2 = ters(*ornek, yukari)
        dx, dy = L1 * math.cos(math.radians(a1)), L1 * math.sin(math.radians(a1))  # dirsek
        ax.plot([0, dx, ornek[0]], [0, dy, ornek[1]], "-o", color=renk, lw=3,
                label=f"çözüm {'θ2 > 0' if yukari else 'θ2 < 0'}: θ1={a1:.0f}°, θ2={a2:.0f}°")
    ax.plot(*ornek, "k*", ms=14)
    ax.set_aspect("equal")
    ax.grid(alpha=0.3)
    ax.set_xlabel("x (mm)")
    ax.set_ylabel("y (mm)")
    ax.set_title(f"SCARA çalışma alanı (L1={L1:.0f} mm, L2={L2:.0f} mm)")
    ax.legend(loc="lower left", fontsize=8, markerscale=1)
    fig.tight_layout()
    fig.savefig(dosya)
    print("kaydedildi:", dosya)


if __name__ == "__main__":
    for nokta in [(250, 100), (100, 250), (300, 0)]:
        a1, a2 = ters(*nokta)
        x, y = ileri(a1, a2)
        print(f"{nokta} -> θ1={a1:7.2f}°, θ2={a2:7.2f}° -> kontrol ({x:.1f}, {y:.1f})")
    calisma_alani_ciz()
