import re
import json

def parse_and_format_sfc(file_path):
    with open(file_path, "r") as f:
        sfc_text = f.read()

    # -----------------------------
    # 1. Parse Variables
    # -----------------------------
    var_block = re.search(r"VAR(.*?)END_VAR", sfc_text, re.S)
    variables = []
    if var_block:
        for line in var_block.group(1).splitlines():
            line = line.strip()
            if ":" in line:
                var_name = line.split(":")[0].strip()
                variables.append(var_name)

    # -----------------------------
    # 2. Parse Steps
    # -----------------------------
    # Modified Regex: [\w()]+ captures function names with parentheses like "DriveToFloor()"
    step_pattern = re.compile(
        r"STEP\s+(\w+)(\s+INITIAL)?\s+ACTION\s+([\w()]+);",
        re.S
    )

    steps = []
    initial_step = None

    for match in step_pattern.finditer(sfc_text):
        step_name = match.group(1)
        is_initial = match.group(2)
        action = match.group(3)

        steps.append({
            "name": step_name,
            "function": action
        })

        if is_initial:
            initial_step = step_name

    # -----------------------------
    # 3. Parse Transitions
    # -----------------------------
    transition_pattern = re.compile(
        r"TRANSITION\s+FROM\s+(\w+)\s+TO\s+(\w+)\s+CONDITION\s+(.*?);",
        re.S
    )

    transitions = []
    for match in transition_pattern.finditer(sfc_text):
        src = match.group(1)
        tgt = match.group(2)
        guard = match.group(3).strip()

        # Normalize guards
        guard = guard.replace("=", "==")
        guard = guard.replace("====", "==") # prevent double replace issues
        guard = guard.replace("TRUE", "True")   # Changed to Title Case "True"
        guard = guard.replace("FALSE", "False") # Changed to Title Case "False"

        transitions.append({
            "src": src,
            "tgt": tgt,
            "guard": guard
        })

    # -----------------------------
    # 4. Formatted Printing
    # -----------------------------
    
    # Print Steps
    print("steps = [")
    for i, step in enumerate(steps):
        comma = "," if i < len(steps) - 1 else ""
        # json.dumps ensures double quotes
        print(f"{json.dumps(step)}{comma}")
    print("]")

    # Print Transitions
    print("transitions = [")
    for i, tran in enumerate(transitions):
        comma = "," if i < len(transitions) - 1 else ""
        print(f"{json.dumps(tran)}{comma}")
    print("]")

    # Print Variables and Initial Step
    # json.dumps creates the ["var1", "var2"] format with double quotes
    print(f"variables = {json.dumps(variables)}")
    print(f"initial_step = \"{initial_step}\"")

# Run the parser
if __name__ == "__main__":
    parse_and_format_sfc("testST.xml")