import json
import sys
from pathlib import Path

def infer_variable_type(var_name):
    """Infers IEC 61131-3 variable types based on naming conventions."""
    v_upper = var_name.upper()
    
    if "TIME" in v_upper or v_upper.startswith("T_"):
        return "TIME"
    elif v_upper in ["IN", "SENS"]:
        return "BYTE"
    elif "CODE" in v_upper or "COUNT" in v_upper:
        return "UINT"
    
    # Default everything else (like INPUT_VALID, flags, etc.) to BOOL
    return "BOOL"

def generate_sfc_text(sfc_data, program_name):
    lines = []
    
    steps = sfc_data.get("steps", [])
    transitions = sfc_data.get("transitions", [])
    variables = sfc_data.get("variables", [])
    initial_step = sfc_data.get("initial_step", "")

    # 1. Program Header & Variables
    lines.append(f"PROGRAM {program_name}")
    lines.append("  VAR")
    for var in variables:
        var_type = infer_variable_type(var)
        lines.append(f"    {var} : {var_type};")
    lines.append("  END_VAR")
    lines.append("")

    # 2. Steps
    for step in steps:
        initial_marker = " INITIAL" if step["name"] == initial_step else ""
        lines.append(f"  STEP {step['name']}{initial_marker} ACTION {step['function']};")
    lines.append("")

    # 3. Transitions
    for tran in transitions:
        guard = tran["guard"]
        guard = guard.replace("==", "=")
        guard = guard.replace("True", "TRUE")
        guard = guard.replace("False", "FALSE")

        lines.append(f"  TRANSITION FROM {tran['src']} TO {tran['tgt']} CONDITION")
        lines.append(f"    {guard};")
        lines.append("")

    lines.append("END_PROGRAM")
    return "\n".join(lines)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python json_to_xml.py <input_file.json>")
        sys.exit(1)

    input_path = Path(sys.argv[1])
    if not input_path.exists():
        print(f"Error: File '{input_path}' not found.")
        sys.exit(1)

    # Derive program name from filename (e.g., ACTUATOR_2P_sfc_iter_01)
    program_name = input_path.stem.replace("-", "_").replace(".", "_")

    with open(input_path, "r") as f:
        data = json.load(f)

    # Pull the upgraded SFC from your triplet format
    if "sfc_upgraded" in data:
        sfc_target = data["sfc_upgraded"]
    else:
        sfc_target = data

    output_text = generate_sfc_text(sfc_target, program_name)
    
    # Save as .xml as requested
    output_path = input_path.with_suffix(".xml")
    
    with open(output_path, "w") as f:
        f.write(output_text)

    print(f"✅ Successfully converted '{input_path.name}' -> '{output_path.name}'")