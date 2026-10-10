# IO-Link Sensör Entegrasyonu: Kontrol Listesi

1. **Donanım:** IO-Link master (PROFINET / EtherNet/IP / EtherCAT), port tipi (Class A/B), M12 4 pinli kablo.
2. **IODD dosyası:** Sensör üreticisinin IODD dosyası master'ın konfigürasyon aracına (ör. TIA Portal + S7-PCT) yüklenir.
3. **Process data:** Ölçüm değeri, durum bitleri ve sinyal kalitesi bayt sırasıyla PLC adres alanına eşlenir (big-endian'a dikkat).
4. **Parametreleme:** Anahtarlama noktaları, filtre ve birim gibi ayarlar ISDU (acyclic) üzerinden yazılır. "Data Storage" açılırsa sensör değiştirildiğinde parametreler otomatik yüklenir.
5. **Teşhis:** Event'ler (kirlenme, sıcaklık aşımı vb.) PLC'de alarm olarak gösterilir.
6. **Avantaj:** Analog sinyale göre gürültüye dayanıklıdır, kablolaması standarttır, uzaktan parametre verilebilir ve kestirimci bakım verisi sağlar.
