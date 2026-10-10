(* ==========================================================================
   FB_EksenKontrol - TwinCAT 3 / Tc2_MC2 tek eksen kontrol bloğu
   ========================================================================== *)
FUNCTION_BLOCK FB_EksenKontrol
VAR_INPUT
    bEnable      : BOOL;
    bHome        : BOOL;
    bHareket     : BOOL;          (* Mutlak pozisyona git (yükselen kenar) *)
    bJogIleri    : BOOL;
    bJogGeri     : BOOL;
    bReset       : BOOL;
    fHedefPoz    : LREAL;         (* mm *)
    fHiz         : LREAL := 100;  (* mm/s *)
END_VAR
VAR_OUTPUT
    bHazir       : BOOL;
    bHomeTamam   : BOOL;
    bPozda      : BOOL;
    bHata        : BOOL;
    nHataKodu    : UDINT;
    fAktuelPoz   : LREAL;
END_VAR
VAR_IN_OUT
    Eksen        : AXIS_REF;
END_VAR
VAR
    fbPower      : MC_Power;
    fbHome       : MC_Home;
    fbMoveAbs    : MC_MoveAbsolute;
    fbJog        : MC_Jog;
    fbReset      : MC_Reset;
END_VAR

Eksen.ReadStatus();
fAktuelPoz := Eksen.NcToPlc.ActPos;

fbPower(Axis := Eksen, Enable := bEnable,
        Enable_Positive := TRUE, Enable_Negative := TRUE, Override := 100.0);
bHazir := fbPower.Status;

fbReset(Axis := Eksen, Execute := bReset);

fbHome(Axis := Eksen, Execute := bHome AND bHazir,
       Position := 0.0, HomingMode := MC_DefaultHoming);
IF fbHome.Done THEN bHomeTamam := TRUE; END_IF;

fbMoveAbs(Axis := Eksen,
          Execute  := bHareket AND bHazir AND bHomeTamam,
          Position := fHedefPoz, Velocity := fHiz,
          Acceleration := fHiz * 5, Deceleration := fHiz * 5);
bPozda := fbMoveAbs.Done;

fbJog(Axis := Eksen, JogForward := bJogIleri AND bHazir,
      JogBackwards := bJogGeri AND bHazir, Mode := MC_JOGMODE_CONTINOUS,
      Velocity := fHiz * 0.2, Acceleration := fHiz, Deceleration := fHiz);

bHata := Eksen.Status.Error OR fbPower.Error OR fbMoveAbs.Error OR fbHome.Error;
nHataKodu := Eksen.Status.ErrorID;
