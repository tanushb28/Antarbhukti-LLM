#!/usr/bin/env python3
"""
PLCopen XML → SFC IR extractor
Compatible with multi-line STEP / TRANSITION / END_TRANSITION
Outputs result to output_llma.txt
"""

import xml.etree.ElementTree as ET
import re
import os
import sys

PLCOPEN_NS = {
    "plc": "http://www.plcopen.org/xml/tc6_0200",
    "xhtml": "http://www.w3.org/1999/xhtml"
}

# ======================================================
# XML loading
# ======================================================

def load_xml(xml_input):
    if os.path.isfile(xml_input):
        if os.path.getsize(xml_input) == 0:
            raise RuntimeError(f"XML file is empty → {xml_input}")
        return ET.parse(xml_input).getroot()

    if xml_input.strip().startswith("<"):
        return ET.fromstring(xml_input)

    raise RuntimeError(f"Invalid XML input: {xml_input}")


# ======================================================
# ST extraction
# ======================================================

def extract_st(root):
    st = root.find(".//plc:ST/xhtml:xhtml", PLCOPEN_NS)
    if st is None or st.text is None:
        raise RuntimeError("No ST code found")
    return st.text


# ======================================================
# ST parsing
# ======================================================

def parse_variables(st):
    m = re.search(r"VAR(.*?)END_VAR", st, re.DOTALL | re.IGNORECASE)
    if not m:
        return []

    variables = []
    for line in m.group(1).split(";"):
        line = line.strip()
        if ":" in line:
            variables.append(line.split(":")[0].strip())
    return variables


def parse_initial_step(st):
    m = re.search(r"INITIAL_STEP\s+(\w+)\s*:", st, re.IGNORECASE)
    return m.group(1) if m else None


def parse_steps(st):
    steps = []
    pattern = re.compile(
        r"(INITIAL_STEP|STEP)\s+(\w+)\s*:\s*(.*?)\s*END_STEP",
        re.DOTALL | re.IGNORECASE
    )

    for _, name, body in pattern.findall(st):
        steps.append({
            "name": name,
            "function": body.strip().rstrip(";")
        })

    return steps


def parse_transitions(st):
    transitions = []

    pattern = re.compile(
        r"TRANSITION\s+\w+\s+FROM\s+(\w+)\s+TO\s+(\w+)\s*"
        r":=\s*(.*?)\s*END_TRANSITION",
        re.DOTALL | re.IGNORECASE
    )

    for src, tgt, guard in pattern.findall(st):
        transitions.append({
            "src": src,
            "tgt": tgt,
            "guard": guard.strip().rstrip(";")
        })

    return transitions


# ======================================================
# Main API
# ======================================================

def parse_sfc_from_xml(xml_input):
    root = load_xml(xml_input)
    st = extract_st(root)

    steps = parse_steps(st)
    transitions = parse_transitions(st)
    variables = parse_variables(st)
    initial_step = parse_initial_step(st)

    return steps, transitions, variables, initial_step


# ======================================================
# CLI
# ======================================================

def main():
    if len(sys.argv) != 2:
        print("Usage: python openplcxml2llma.py <plc.xml>")
        sys.exit(1)

    try:
        steps, transitions, variables, initial = parse_sfc_from_xml(sys.argv[1])
    except Exception as e:
        print("ERROR:", e)
        sys.exit(2)

    output_file = "output_llma.txt"

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("steps = [\n")
        for s in steps:
            f.write(f"  {s},\n")
        f.write("]\n\n")

        f.write("transitions = [\n")
        for t in transitions:
            f.write(f"  {t},\n")
        f.write("]\n\n")

        f.write("variables = ")
        f.write(str(variables))
        f.write("\n\n")

        f.write("initial_step = ")
        f.write(f"\"{initial}\"")
        f.write("\n")

    print(f"✔ Output written to {output_file}")


if __name__ == "__main__":
    main()







#########################################################################

# #!/usr/bin/env python3
# """
# PLCopen XML → SFC IR extractor
# Compatible with multi-line STEP / TRANSITION / END_TRANSITION
# """

# import xml.etree.ElementTree as ET
# import re
# import os
# import sys

# PLCOPEN_NS = {
#     "plc": "http://www.plcopen.org/xml/tc6_0200",
#     "xhtml": "http://www.w3.org/1999/xhtml"
# }

# # ======================================================
# # XML loading
# # ======================================================

# def load_xml(xml_input):
#     if os.path.isfile(xml_input):
#         if os.path.getsize(xml_input) == 0:
#             raise RuntimeError(f"XML file is empty → {xml_input}")
#         return ET.parse(xml_input).getroot()

#     if xml_input.strip().startswith("<"):
#         return ET.fromstring(xml_input)

#     raise RuntimeError(f"Invalid XML input: {xml_input}")


# # ======================================================
# # ST extraction
# # ======================================================

# def extract_st(root):
#     st = root.find(".//plc:ST/xhtml:xhtml", PLCOPEN_NS)
#     if st is None or st.text is None:
#         raise RuntimeError("No ST code found")
#     return st.text


# # ======================================================
# # ST parsing
# # ======================================================

# def parse_variables(st):
#     m = re.search(r"VAR(.*?)END_VAR", st, re.DOTALL | re.IGNORECASE)
#     if not m:
#         return []

#     variables = []
#     for line in m.group(1).split(";"):
#         line = line.strip()
#         if ":" in line:
#             variables.append(line.split(":")[0].strip())
#     return variables


# def parse_initial_step(st):
#     m = re.search(r"INITIAL_STEP\s+(\w+)\s*:", st, re.IGNORECASE)
#     return m.group(1) if m else None


# def parse_steps(st):
#     steps = []
#     pattern = re.compile(
#         r"(INITIAL_STEP|STEP)\s+(\w+)\s*:\s*(.*?)\s*END_STEP",
#         re.DOTALL | re.IGNORECASE
#     )

#     for _, name, body in pattern.findall(st):
#         steps.append({
#             "name": name,
#             "function": body.strip().rstrip(";")
#         })

#     return steps


# def parse_transitions(st):
#     transitions = []

#     pattern = re.compile(
#         r"TRANSITION\s+\w+\s+FROM\s+(\w+)\s+TO\s+(\w+)\s*"
#         r":=\s*(.*?)\s*END_TRANSITION",
#         re.DOTALL | re.IGNORECASE
#     )

#     for src, tgt, guard in pattern.findall(st):
#         transitions.append({
#             "src": src,
#             "tgt": tgt,
#             "guard": guard.strip().rstrip(";")
#         })

#     return transitions


# # ======================================================
# # Main API
# # ======================================================

# def parse_sfc_from_xml(xml_input):
#     root = load_xml(xml_input)
#     st = extract_st(root)

#     steps = parse_steps(st)
#     transitions = parse_transitions(st)
#     variables = parse_variables(st)
#     initial_step = parse_initial_step(st)

#     return steps, transitions, variables, initial_step


# # ======================================================
# # CLI
# # ======================================================

# def main():
#     if len(sys.argv) != 2:
#         print("Usage: python openplcxml2llma.py <plc.xml>")
#         sys.exit(1)

#     try:
#         steps, transitions, variables, initial = parse_sfc_from_xml(sys.argv[1])
#     except Exception as e:
#         print("ERROR:", e)
#         sys.exit(2)

#     print("\nsteps =")
#     for s in steps:
#         print(" ", s)

#     print("\ntransitions =")
#     for t in transitions:
#         print(" ", t)

#     print("\nvariables =")
#     print(" ", variables)

#     print("\ninitial_step =")
#     print(" ", initial)


# if __name__ == "__main__":
#     main()


