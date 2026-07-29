import re

with open("claude_raw_output.txt", "r", encoding="utf-8") as f:
    llm_output = f.read()

match = re.search(r"```(?:python)?\s*([\s\S]*?)```", llm_output)
if match:
    print("MATCHED:")
    print(repr(match.group(1)))
else:
    print("NO MATCH")
    
    # Let's test the fallback
    lines = llm_output.splitlines()
    extracted_code = []
    in_list = False
    for line in lines:
        stripped_line = line.strip()
        if stripped_line.startswith("steps2") or stripped_line.startswith("transitions2"):
            in_list = True
        
        if in_list:
            extracted_code.append(line)
            if stripped_line.endswith("]"):
                in_list = False

    print("FALLBACK:")
    print(repr("\n".join(extracted_code)))

