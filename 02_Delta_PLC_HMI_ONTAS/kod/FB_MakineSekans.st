(* ==========================================================================
   FB_MakineSekans - Adım (step) tabanlı otomatik makine çevrimi
   Besleme -> Sıkma -> İşlem -> Açma -> Boşaltma -> Başa dön
   ========================================================================== *)
FUNCTION_BLOCK FB_MakineSekans
VAR_INPUT
    Start, Stop, Reset   : BOOL;
    UrunVar              : BOOL;   (* Besleme sensörü *)
    SikmaIleri, SikmaGeri: BOOL;   (* Silindir manyetik sensörleri *)
    IslemSuresi          : TIME := T#3s;
    AdimZamanAsimi       : TIME := T#10s;
END_VAR
VAR_OUTPUT
    Y_Besleme, Y_Sikma, M_Islem, Y_Bosalt : BOOL;
    Adim     : INT;     (* HMI'da gösterilir *)
    Alarm    : BOOL;
    Sayac    : DINT;    (* Üretim sayacı *)
END_VAR
VAR
    Calisiyor : BOOL;
    tIslem    : TON;
    tAsim     : TON;
    OncekiAdim: INT;
END_VAR

IF Reset THEN Alarm := FALSE; Adim := 0; END_IF;
IF Stop OR Alarm THEN Calisiyor := FALSE; END_IF;
IF Start AND NOT Alarm THEN Calisiyor := TRUE; END_IF;

(* Her adımın zaman aşımı denetimi: adım değişince sayaç sıfırlanır *)
tAsim(IN := Calisiyor AND (Adim = OncekiAdim) AND (Adim <> 0), PT := AdimZamanAsimi);
OncekiAdim := Adim;
IF tAsim.Q THEN Alarm := TRUE; END_IF;

IF Calisiyor THEN
    CASE Adim OF
    0:  IF NOT UrunVar THEN Adim := 10; END_IF;           (* Yuva boş mu? *)
    10: Y_Besleme := TRUE;                                 (* Ürünü besle *)
        IF UrunVar THEN Y_Besleme := FALSE; Adim := 20; END_IF;
    20: Y_Sikma := TRUE;                                   (* Sık *)
        IF SikmaIleri THEN Adim := 30; END_IF;
    30: M_Islem := TRUE;                                   (* İşlem *)
        tIslem(IN := TRUE, PT := IslemSuresi);
        IF tIslem.Q THEN
            M_Islem := FALSE; tIslem(IN := FALSE); Adim := 40;
        END_IF;
    40: Y_Sikma := FALSE;                                  (* Aç *)
        IF SikmaGeri THEN Adim := 50; END_IF;
    50: Y_Bosalt := TRUE;                                  (* Boşalt *)
        IF NOT UrunVar THEN
            Y_Bosalt := FALSE; Sayac := Sayac + 1; Adim := 0;
        END_IF;
    END_CASE;
ELSE
    Y_Besleme := FALSE; M_Islem := FALSE; Y_Bosalt := FALSE;
END_IF;

END_FUNCTION_BLOCK
