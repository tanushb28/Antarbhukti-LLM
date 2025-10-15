import re
import sys

def parse_sfc1(sfc_text):
    steps_match = re.search(r"steps\s*=\s*\[(.*?)\]", sfc_text, re.DOTALL)
    transitions_match = re.search(r"transitions\s*=\s*\[(.*?)\]", sfc_text, re.DOTALL)
    variables_match = re.search(r"variables\s*=\s*\[(.*?)\]", sfc_text, re.DOTALL)
    init_match = re.search(r"initial_step\s*=\s*(\w+)", sfc_text)

    steps = steps_match.group(1).strip() if steps_match else ""
    transitions = transitions_match.group(1).strip() if transitions_match else ""
    variables = variables_match.group(1).strip() if variables_match else ""
    initial_step = init_match.group(1) if init_match else "StepName1"

    return steps, transitions, variables, initial_step


def generate_sfc_prompt(original_sfc):
    print("=== IEC 61131-3 SFC Prompt Generator (modular) ===\n")

    # Parse SFC1
    steps, transitions, variables, initial_step = parse_sfc1(original_sfc)

    # Step 2: Choose qualities
    quality_options = ["Reliability", "Safety", "Performance", "Fault Tolerance"]
    print("\nSelect qualities to improve (comma-separated, e.g., 1,2):")
    for i, q in enumerate(quality_options, 1):
        print(f"{i}. {q}")
    choices = input("Enter choice(s): ").split(",")
    qualities = [quality_options[int(c.strip()) - 1] for c in choices if c.strip().isdigit()]
    qualities_str = " and ".join(qualities)

    # Step 3: Build modular quality blocks
    quality_blocks = []
    for q in qualities:
        print(f"\nEnter specific requirements for {q}:")
        req = input("Type here: ")
        block = f"---\n**{q}**\n{req}\n"
        quality_blocks.append(block)

    quality_block = "\n".join(quality_blocks)

    # Structured Format auto-filled (SFC2 template)
    sfc2_steps = steps if steps else '{ "name": StepName1, "function": FunctionName1 }'
    sfc2_transitions = transitions if transitions else '{ "src": StepNameX, "tgt": StepNameY, "guard": GuardCondition1 }'
    sfc2_vars = variables if variables else "var1, var2, ..., additionalVarsIfNeeded"

    sec_structure = f"""**Structured Format to generate the upgraded SFC (SFC2)**
steps = [
    {sfc2_steps}  # Upgrade functions as needed
]
transitions = [
    {sfc2_transitions}  # Upgrade guards as needed
]
variables = [ {sfc2_vars}, ... ]
initial_step = {initial_step}
"""

    # Compliance rules
    compliance = """**Compliance with IEC-61131-3 SFC**
1. *SFC Semantics Compliance*
   - Follow IEC 61131-3 execution semantics: steps hold active states; transitions must be evaluated between cycles.
   - Transitions should only occur when all preceding steps are active and the guard condition evaluates to true.

2. *Determinism and Safety*
   - Ensure transitions are deterministic and do not cause ambiguous behavior (i.e., one enabled transition per active step set).
   - Avoid conflicting parallel branches unless explicitly required, and model them using AND/OR semantics with care.

3. *Guard Conditions*
   - Guards must be side-effect-free and should not modify variable states. Use separate action blocks for updates.
"""

    # Prompt segments
    role = "Act as a control software designer for IEC 61131-3 Sequential Function Charts (SFCs)."
    task = " Given an SFC (SFC1) representing a control process, your task is to generate an upgraded SFC (SFC2)."
    context = " The upgraded version must preserve the original behavior under nominal conditions and preserve compliance with IEC-61131-3."
    upgrade_spec = " Use the Structured Format to generate the upgraded SFC (SFC2)."
    quality_list = f" The upgrade must improve {qualities_str}."
    constraint_clause = " Ensure determinism, safety, and IEC compliance as outlined below."

    # Final prompt string
    prompt = (
        f"{role}"
        f"{task}"
        f"{context}"
        f"{upgrade_spec}"
        f"{quality_list}"
        f"{constraint_clause}\n\n"
        f"---\n**SFC1: Original Control Logic**\n{original_sfc.strip()}\n\n"
        f"{quality_block}\n"
        f"{sec_structure}\n"
        f"{compliance}"
    )

    print("\n=== Generated Prompt ===\n")
    print(prompt)
    print("\n========================")


# Run
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python promptgen.py <sfc_input_file>")
        sys.exit(1)
    sfc_file_path = sys.argv[1]
    try:
        with open(sfc_file_path, 'r') as f:
            original_sfc = f.read()
    except Exception as e:
        print(f"Error reading file {sfc_file_path}: {e}")
        sys.exit(1)
    generate_sfc_prompt(original_sfc)