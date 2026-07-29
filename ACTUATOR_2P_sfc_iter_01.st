PROGRAM ACTUATOR_2P_sfc_iter_01
  VAR
    IN : BYTE;
    TEST : BOOL;
    ARE : BOOL;
    CYCLE_TIME : TIME;
    SENS : BYTE;
    SELF_ACT_TIME : TIME;
    SELF_ACT_PULSE : BOOL;
    SELF_ACT_CYCLES : BOOL;
    OUT : BOOL;
    ARO : BOOL;
    ARX : BOOL;
    timer : TIME;
    pwgen : TP;
    INPUT_VALID : BOOL;
    SAFETY_ERROR_FLAG : BOOL;
    SAFETY_ERROR_CODE : UINT;
    CUMULATIVE_CYCLE_TIME : TIME;
    MAX_SAFE_CYCLE_TIME : TIME;
    TIMEOUT_EXCEEDED : TIME;
    TIMEOUT_ERROR_FLAG : TIME;
    TIMEOUT_LOG_TIME : TIME;
    _ACTIVE_STEP : INT := 0;
  END_VAR

  CASE _ACTIVE_STEP OF
    0: (* Step: InitCycle *)
      timer(trun := MUL_T_AI(SELF_ACT_PULSE,2 * SELF_ACT_CYCLES), toff := SELF_ACT_TIME, Test := TEST, ARE := ARE, arx := ARX); ARX := timer.ARX; ARO := timer.ARO;
      
      IF TRUE THEN
        _ACTIVE_STEP := 1;
      END_IF;

    1: (* Step: SafetyCheckInput *)
      INPUT_VALID := (IN >= BYTE#0) AND (IN <= BYTE#255) AND (SENS > BYTE#0) AND (SENS <= BYTE#255); CUMULATIVE_CYCLE_TIME := CUMULATIVE_CYCLE_TIME + CYCLE_TIME;
      
      IF INPUT_VALID = FALSE THEN
        _ACTIVE_STEP := 2;
      ELSIF INPUT_VALID = TRUE AND aro = TRUE THEN
        _ACTIVE_STEP := 3;
      ELSIF INPUT_VALID = TRUE AND aro = FALSE AND in<sens THEN
        _ACTIVE_STEP := 4;
      ELSIF INPUT_VALID = TRUE AND aro = FALSE AND NOT (in<sens) AND BYTE_TO_USINT(in)>USINT#255-BYTE_TO_USINT(sens) THEN
        _ACTIVE_STEP := 5;
      ELSIF INPUT_VALID = TRUE AND aro = FALSE AND NOT (in<sens) AND NOT (BYTE_TO_USINT(in)>USINT#255-BYTE_TO_USINT(sens)) THEN
        _ACTIVE_STEP := 6;
      END_IF;

    2: (* Step: SafetyError *)
      out := FALSE; SAFETY_ERROR_FLAG := TRUE; SAFETY_ERROR_CODE := UINT#1001;
      
      IF TRUE THEN
        _ACTIVE_STEP := 2;
      END_IF;

    3: (* Step: Branch_0 *)
      pwgen(PTL := SELF_ACT_PULSE, PTH := SELF_ACT_PULSE); out := pwgen.Q;
      
      IF TRUE THEN
        _ACTIVE_STEP := 7;
      END_IF;

    4: (* Step: Branch_1 *)
      out := FALSE;
      
      IF TRUE THEN
        _ACTIVE_STEP := 7;
      END_IF;

    5: (* Step: Branch_2 *)
      out := TRUE;
      
      IF TRUE THEN
        _ACTIVE_STEP := 7;
      END_IF;

    6: (* Step: Step_255 *)
      pwgen.PTH := (CYCLE_TIME * BYTE_TO_TIME(BAND_B(IN,SENS)) ) / BYTE_TO_TIME(BYTE#255); pwgen.PTL := CYCLE_TIME - pwgen.PTH; pwgen(); out := pwgen.Q;
      
      IF TRUE THEN
        _ACTIVE_STEP := 7;
      END_IF;

    7: (* Step: ApplyOutput *)
      TIMEOUT_EXCEEDED := CUMULATIVE_CYCLE_TIME > MAX_SAFE_CYCLE_TIME;
      
      IF TIMEOUT_EXCEEDED = TRUE THEN
        _ACTIVE_STEP := 8;
      ELSIF TIMEOUT_EXCEEDED = FALSE THEN
        _ACTIVE_STEP := 0;
      END_IF;

    8: (* Step: TimeoutSafeStop *)
      out := FALSE; TIMEOUT_ERROR_FLAG := TRUE; TIMEOUT_LOG_TIME := CUMULATIVE_CYCLE_TIME; CUMULATIVE_CYCLE_TIME := T#0s;
      
      IF TRUE THEN
        _ACTIVE_STEP := 0;
      END_IF;

  END_CASE;
END_PROGRAM