import re
import json

# -------- INPUT: OpenPLC Textual SFC --------
sfc_text = """
PROGRAM PLC_PRG
VAR
  temp : INT;
  humidity : INT;
  threshold : INT;
  timeout_counter : INT;
  timeout_limit : INT;
  fanOnTime : INT;
  maxFanOnTime : INT;
  sensorFresh : BOOL;
END_VAR

INITIAL_STEP MonitorTemperature:
  ReadSensor(temp);
END_STEP

STEP CheckSensorHealth:
  VerifySensorFreshness();
END_STEP

STEP AdjustVentilation:
  ControlFan(temp);
END_STEP

STEP LogData:
  Log(temp, humidity);
END_STEP

STEP TimeoutSafeStop:
  HaltActuatorsSafely();
END_STEP

TRANSITION T1 FROM MonitorTemperature TO CheckSensorHealth
  := TRUE;
END_TRANSITION

TRANSITION T2 FROM CheckSensorHealth TO AdjustVentilation
  := sensorFresh == TRUE;
END_TRANSITION

TRANSITION T3 FROM AdjustVentilation TO LogData
  := TRUE;
END_TRANSITION

TRANSITION T4 FROM LogData TO MonitorTemperature
  := TRUE;
END_TRANSITION

TRANSITION T5 FROM CheckSensorHealth TO TimeoutSafeStop
  := timeout_counter > timeout_limit;
END_TRANSITION

TRANSITION T6 FROM AdjustVentilation TO TimeoutSafeStop
  := fanOnTime > maxFanOnTime;
END_TRANSITION

"""

# -------- PARSE VARIABLES --------
var_block = re.search(r"VAR(.*?)END_VAR", sfc_text, re.S)
variables = []
if var_block:
    for line in var_block.group(1).splitlines():
        line = line.strip()
        if ":" in line:
            var_name = line.split(":")[0].strip()
            variables.append(var_name)

# -------- PARSE INITIAL STEP --------
init_match = re.search(
    r"INITIAL_STEP\s+(\w+):\s*(\w+\(.*?\));",
    sfc_text,
    re.S
)
initial_step = init_match.group(1)
steps = [{
    "name": init_match.group(1),
    "function": init_match.group(2)
}]

# -------- PARSE OTHER STEPS (exclude initial step) --------
for m in re.finditer(
    r"STEP\s+(\w+):\s*(\w+\(.*?\));\s*END_STEP",
    sfc_text,
    re.S
):
    step_name = m.group(1)
    if step_name != initial_step:  # avoid duplicates
        steps.append({
            "name": step_name,
            "function": m.group(2)
        })

# -------- PARSE TRANSITIONS --------
transitions = []
for m in re.finditer(
    r"TRANSITION\s+\w+\s+FROM\s+(\w+)\s+TO\s+(\w+)\s*:=\s*(.*?);",
    sfc_text,
    re.S
):
    # Convert IEC syntax to Python-like boolean
    guard = m.group(3).strip()
    guard = guard.replace("= TRUE", "== True")
    guard = guard.replace("= FALSE", "== False")
    guard = guard.replace("AND", "and").replace("OR", "or")  # normalize
    transitions.append({
        "src": m.group(1),
        "tgt": m.group(2),
        "guard": guard
    })

# -------- SAVE OUTPUT IN REQUESTED FORMAT --------
with open("test-llma.txt", "w") as f:
    f.write(f"steps = {json.dumps(steps, indent=2)}\n\n")
    f.write(f"transitions = {json.dumps(transitions, indent=2)}\n\n")
    f.write(f"variables = {json.dumps(variables, indent=2)}\n\n")
    f.write(f"initial_step = '{initial_step}'\n")

print("✅ Parsed SFC saved in 'test-llma.txt' in the correct format.")
