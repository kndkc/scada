(* ==========================================================================
   FB_AnalogOlcek - Analog giriş ölçekleme + filtre + kopuk kablo tespiti
   Delta AS/DVP analog modülü: 4-20 mA -> ham 0..32000 (modüle göre ayarlanır)
   ========================================================================== *)
FUNCTION_BLOCK FB_AnalogOlcek
VAR_INPUT
    HamDeger   : INT;            (* Modülden okunan ham değer *)
    HamMin     : INT  := 0;      (* 4 mA karşılığı *)
    HamMax     : INT  := 32000;  (* 20 mA karşılığı *)
    MuhMin     : REAL := 0.0;    (* Örn. 0 bar *)
    MuhMax     : REAL := 10.0;   (* Örn. 10 bar *)
    KopukLimit : INT  := -500;   (* 4 mA altı: kablo kopuk *)
END_VAR
VAR_OUTPUT
    Deger      : REAL;           (* Filtrelenmiş mühendislik değeri *)
    KopukAlarm : BOOL;
END_VAR
VAR
    Tampon     : ARRAY[0..9] OF REAL;
    Indeks     : INT;
    Toplam     : REAL;
    i          : INT;
    Anlik      : REAL;
END_VAR

KopukAlarm := HamDeger < KopukLimit;

(* Doğrusal ölçekleme: y = (x - x1) * (y2 - y1) / (x2 - x1) + y1 *)
Anlik := INT_TO_REAL(HamDeger - HamMin) * (MuhMax - MuhMin)
         / INT_TO_REAL(HamMax - HamMin) + MuhMin;

(* Sınırla *)
IF Anlik < MuhMin THEN Anlik := MuhMin; END_IF;
IF Anlik > MuhMax THEN Anlik := MuhMax; END_IF;

(* 10 örnekli hareketli ortalama *)
Tampon[Indeks] := Anlik;
Indeks := (Indeks + 1) MOD 10;
Toplam := 0.0;
FOR i := 0 TO 9 DO
    Toplam := Toplam + Tampon[i];
END_FOR;
Deger := Toplam / 10.0;

END_FUNCTION_BLOCK
