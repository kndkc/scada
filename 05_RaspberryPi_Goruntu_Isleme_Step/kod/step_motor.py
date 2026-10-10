"""Raspberry Pi STEP/DIR step motor sürücüsü (A4988 / DRV8825 / TB6600)."""
import time

try:
    import RPi.GPIO as GPIO
except ImportError:  # PC'de test için sahte GPIO
    class _SahteGPIO:
        BCM = OUT = IN = HIGH = LOW = PUD_UP = 0
        def __getattr__(self, _):
            return lambda *a, **k: 0
    GPIO = _SahteGPIO()


class StepMotor:
    def __init__(self, step_pin=20, dir_pin=21, en_pin=16, limit_pin=26,
                 adim_tur=200, mikro_adim=16, mm_tur=8.0):
        self.step_pin, self.dir_pin, self.en_pin, self.limit_pin = step_pin, dir_pin, en_pin, limit_pin
        self.adim_mm = adim_tur * mikro_adim / mm_tur   # T8 trapez mil: 8 mm/tur
        self.konum_adim = 0

        GPIO.setmode(GPIO.BCM)
        GPIO.setup([step_pin, dir_pin, en_pin], GPIO.OUT)
        GPIO.setup(limit_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        self.etkinlestir(True)

    def etkinlestir(self, durum: bool):
        GPIO.output(self.en_pin, GPIO.LOW if durum else GPIO.HIGH)

    def adim_at(self, adim: int, hiz=4000, ivme=8000):
        """adim > 0 ileri, < 0 geri. hiz: adım/s, ivme: adım/s² (trapez profil)."""
        if adim == 0:
            return
        GPIO.output(self.dir_pin, GPIO.HIGH if adim > 0 else GPIO.LOW)
        n = abs(adim)
        rampa = min(int(hiz * hiz / (2 * ivme)), n // 2)
        for i in range(n):
            # hızlanma / sabit / yavaşlama bölgesindeki anlık hız
            k = min(i, n - 1 - i)
            v = hiz if k >= rampa else max(200.0, (2 * ivme * (k + 1)) ** 0.5)
            yarim = 0.5 / v
            GPIO.output(self.step_pin, GPIO.HIGH)
            time.sleep(yarim)
            GPIO.output(self.step_pin, GPIO.LOW)
            time.sleep(yarim)
        self.konum_adim += adim

    def git_mm(self, hedef_mm: float, **kw):
        self.adim_at(round(hedef_mm * self.adim_mm) - self.konum_adim, **kw)

    def homing(self, hiz=1500, maks_adim=200_000):
        GPIO.output(self.dir_pin, GPIO.LOW)
        for _ in range(maks_adim):
            if GPIO.input(self.limit_pin) == GPIO.LOW:   # switch'e basıldı
                break
            self.adim_at(-1, hiz=hiz)
        else:
            raise RuntimeError("Homing başarısız: limit switch bulunamadı")
        self.adim_at(int(2 * self.adim_mm), hiz=hiz)    # 2 mm geri çık
        self.konum_adim = 0

    @property
    def konum_mm(self):
        return self.konum_adim / self.adim_mm

    def kapat(self):
        self.etkinlestir(False)
        GPIO.cleanup()
