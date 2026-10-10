"""
Kameradaki renkli nesneyi tespit edip step motorla görüntü merkezine hizalar.
Basit P kontrol: sapma (piksel) -> mm -> motor hareketi.
"""
import argparse

import cv2
import numpy as np

from step_motor import StepMotor

RENKLER = {  # HSV alt / üst sınırlar
    "kirmizi": [((0, 120, 70), (10, 255, 255)), ((170, 120, 70), (180, 255, 255))],
    "mavi":    [((100, 150, 50), (130, 255, 255))],
    "yesil":   [((40, 70, 50), (80, 255, 255))],
}


def maske_olustur(hsv, renk):
    m = np.zeros(hsv.shape[:2], np.uint8)
    for alt, ust in RENKLER[renk]:
        m |= cv2.inRange(hsv, np.array(alt), np.array(ust))
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, np.ones((5, 5), np.uint8))
    return cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))


def nesne_bul(maske, min_alan=500):
    konturlar, _ = cv2.findContours(maske, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not konturlar:
        return None
    c = max(konturlar, key=cv2.contourArea)
    if cv2.contourArea(c) < min_alan:
        return None
    M = cv2.moments(c)
    return int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]), cv2.boundingRect(c)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--renk", choices=RENKLER, default="kirmizi")
    p.add_argument("--kamera", type=int, default=0)
    p.add_argument("--mm_piksel", type=float, default=0.25, help="kalibrasyon: 1 piksel kaç mm")
    p.add_argument("--kp", type=float, default=0.6)
    p.add_argument("--olu_bant", type=int, default=8, help="piksel")
    p.add_argument("--motorsuz", action="store_true")
    a = p.parse_args()

    motor = None if a.motorsuz else StepMotor()
    if motor:
        motor.homing()

    cap = cv2.VideoCapture(a.kamera)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    try:
        while True:
            ok, kare = cap.read()
            if not ok:
                break
            hsv = cv2.cvtColor(cv2.GaussianBlur(kare, (5, 5), 0), cv2.COLOR_BGR2HSV)
            sonuc = nesne_bul(maske_olustur(hsv, a.renk))
            merkez_x = kare.shape[1] // 2
            cv2.line(kare, (merkez_x, 0), (merkez_x, kare.shape[0]), (255, 255, 255), 1)

            if sonuc:
                cx, cy, (x, y, w, h) = sonuc
                sapma = cx - merkez_x
                cv2.rectangle(kare, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.circle(kare, (cx, cy), 4, (0, 0, 255), -1)
                cv2.putText(kare, f"sapma: {sapma}px", (10, 25),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
                if motor and abs(sapma) > a.olu_bant:
                    motor.git_mm(motor.konum_mm + a.kp * sapma * a.mm_piksel)

            cv2.imshow("Renk Takip", kare)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()
        if motor:
            motor.kapat()


if __name__ == "__main__":
    main()
