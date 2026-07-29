import json
import sys
from pathlib import Path

def infer_variable_type(var_name, data_text):
    v_upper = var_name.upper()
    if "TIME" in v_upper or v_upper.startswith("T_"): return "TIME"
    if v_upper in ["IN", "SENS"]: return "BYTE"
    if "CODE" in v_upper or "COUNT" in v_upper: return "UINT"
    
    # If the variable is used like a Function Block (has parentheses/dots)
    if f"{v_upper}(" in data_text or f"{v_upper}." in data_text:
        if v_upper == "TIMER": return "TON" # Standard generic timer
        if v_upper == "PWGEN": return "TP"  # Standard generic pulse
        return "TON"
        
    return "BOOL"

def generate_pure_st(sfc_data, program_name):
    lines = []
    steps = sfc_data.get("steps", [])
    transitions = sfc_data.get("transitions", [])
    variables = sfc_data.get("variables", [])
    initial_step = sfc_data.get("initial_step", "")

    data_text = str(sfc_data).upper()

    # Map step names to integers for the CASE statement
    step_map = {step["name"]: i for i, step in enumerate(steps)}
    init_id = step_map.get(initial_step, 0)

    # Build standard ST Program
    lines.append(f"PROGRAM {program_name}")
    lines.append("  VAR")
    for var in variables:
        var_type = infer_variable_type(var, data_text)
        lines.append(f"    {var} : {var_type};")
    lines.append(f"    _ACTIVE_STEP : INT := {init_id};")
    lines.append("  END_VAR")
    lines.append("")
    
    lines.append("  CASE _ACTIVE_STEP OF")
    
    for step in steps:
        s_name = step["name"]
        s_id = step_map[s_name]
        s_func = step["function"].strip()
        
        lines.append(f"    {s_id}: (* Step: {s_name} *)")
        if s_func:
            lines.append(f"      {s_func}")
        
        # Build standard IF/ELSIF for outgoing transitions
        step_trans = [t for t in transitions if t["src"] == s_name]
        if step_trans:
            lines.append("      ")
            for i, tran in enumerate(step_trans):
                tgt_id = step_map[tran["tgt"]]
                guard = tran["guard"].replace("==", "=").replace("True", "TRUE").replace("False", "FALSE")
                if i == 0:
                    lines.append(f"      IF {guard} THEN")
                else:
                    lines.append(f"      ELSIF {guard} THEN")
                lines.append(f"        _ACTIVE_STEP := {tgt_id};")
            lines.append("      END_IF;")
        lines.append("")
        
    lines.append("  END_CASE;")
    lines.append("END_PROGRAM")
    return "\n".join(lines)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python json_to_st_compiler.py <input_file.json>")
        sys.exit(1)

    input_path = Path(sys.argv[1])
    program_name = input_path.stem.replace("-", "_").replace(".", "_")

    with open(input_path, "r") as f:
        data = json.load(f)

    sfc_target = data.get("sfc_upgraded", data)
    output_text = generate_pure_st(sfc_target, program_name)
    
    # Output as standard .st file
    output_path = input_path.with_suffix(".st")
    with open(output_path, "w") as f:
        f.write(output_text)

    print(f"✅ Created Pure ST File: {output_path.name}")