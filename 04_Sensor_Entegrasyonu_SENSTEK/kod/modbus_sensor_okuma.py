"""
Modbus sensör okuyucu: bir veya birden fazla Modbus RTU/TCP sensörden
holding register'ları periyodik olarak okur, ölçekler ve CSV'ye yazar.

Kullanım:
    pip install "pymodbus==3.6.9" pyserial
    python modbus_sensor_okuma.py --tcp 192.168.0.50
    python modbus_sensor_okuma.py --rtu COM3 --baud 19200
"""
import argparse
import csv
import time
from dataclasses import dataclass
from datetime import datetime

from pymodbus.client import ModbusSerialClient, ModbusTcpClient


@dataclass
class Kanal:
    ad: str
    slave: int
    adres: int       # holding register adresi (0 tabanlı)
    carpan: float    # ham değer * çarpan = mühendislik birimi
    birim: str


# Sensörün datasheet'ine göre düzenlenir
KANALLAR = [
    Kanal("Radar_Seviye", slave=1, adres=0, carpan=0.001, birim="m"),
    Kanal("Lazer_Mesafe", slave=2, adres=0, carpan=0.1, birim="mm"),
    Kanal("Sicaklik", slave=3, adres=1, carpan=0.1, birim="°C"),
]


def istemci_olustur(args):
    if args.tcp:
        return ModbusTcpClient(args.tcp, port=args.port)
    return ModbusSerialClient(port=args.rtu, baudrate=args.baud,
                              parity="E", stopbits=1, bytesize=8, timeout=1)


def oku(client, k: Kanal):
    r = client.read_holding_registers(k.adres, count=1, slave=k.slave)
    if r.isError():
        return None
    ham = r.registers[0]
    if ham > 32767:          # işaretli 16 bit
        ham -= 65536
    return ham * k.carpan


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--tcp")
    p.add_argument("--port", type=int, default=502)
    p.add_argument("--rtu")
    p.add_argument("--baud", type=int, default=19200)
    p.add_argument("--periyot", type=float, default=1.0, help="saniye")
    p.add_argument("--csv", default="olcumler.csv")
    args = p.parse_args()
    if not (args.tcp or args.rtu):
        p.error("--tcp veya --rtu verilmeli")

    client = istemci_olustur(args)
    if not client.connect():
        raise SystemExit("Bağlantı kurulamadı")

    with open(args.csv, "a", newline="", encoding="utf-8") as f:
        w = csv.writer(f, delimiter=";")
        if f.tell() == 0:
            w.writerow(["zaman"] + [f"{k.ad} [{k.birim}]" for k in KANALLAR])
        try:
            while True:
                degerler = [oku(client, k) for k in KANALLAR]
                satir = [datetime.now().isoformat(timespec="seconds")] + [
                    "HATA" if v is None else f"{v:.3f}" for v in degerler]
                w.writerow(satir)
                f.flush()
                print("  ".join(satir))
                time.sleep(args.periyot)
        except KeyboardInterrupt:
            pass
        finally:
            client.close()


if __name__ == "__main__":
    main()
