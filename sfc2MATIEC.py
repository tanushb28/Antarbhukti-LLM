"""
SFC to MATIEC Batch Converter (Dependency-Free, Upgraded JSON Only)
Processes multiple JSON SFC files, extracts 'sfc_upgraded', 
checks MATIEC compilation, and exports results to a TXT report.
"""

import re
import subprocess
import sys
import os
import datetime
import json

# ======================================================================== #
# JSON-based SFC Converter - processes ONLY sfc_upgraded                   #
# ======================================================================== #

# FIX: known IEC scalar/elementary types. Anything inferred that is NOT in
# this set is treated as a function-block instance (no ":= init" allowed).
SCALAR_TYPES = {
    'BOOL', 'BYTE', 'WORD', 'DWORD', 'LWORD',
    'SINT', 'INT', 'DINT', 'LINT',
    'USINT', 'UINT', 'UDINT', 'ULINT',
    'REAL', 'LREAL', 'TIME', 'STRING'
}

# FIX: if your ../matiec/lib defines custom FB types whose names don't
# match "uppercase(variable name)", put the mapping here, e.g.
# {"timer": "MY_TIMER_FB"}. Left empty means: a variable invoked like
# `name(...)` or accessed like `name.member` is assumed to be an instance
# of a custom FB literally named UPPER(name) in your library. This
# replaces the old hard-coded TIMER->TON / PWGEN->TP mapping, which was
# wrong: your calls use members (trun, toff, Test, ARE, arx, ARX, ARO /
# PTL, PTH) that don't exist on the IEC-standard TON/TP blocks.
CUSTOM_FB_TYPE_OVERRIDES = {
    # "timer": "TIMER",
    # "pwgen": "PWGEN",
}

# FIX: parameter names that, when used as a named FB call argument
# (`name := ...` inside a `fb(...)` call), are strong evidence the
# variable passed in is a TIME value.
TIME_PARAM_NAMES = {'trun', 'toff', 'pt', 'ptl', 'pth', 'et'}


class SFCJSONConverter:
    def __init__(self, json_file):
        self.json_file = json_file
        self.upgraded_sfc = None
        self.upgraded_st_lines = []
    
    def parse(self):
        print(f"\n  [STEP 1] Parsing JSON file: {self.json_file}")
        try:
            with open(self.json_file, 'r') as f:
                data = json.load(f)
            self.upgraded_sfc = data.get('sfc_upgraded', {})
            
            print("    Upgraded SFC:")
            print(f"      Steps       : {len(self.upgraded_sfc.get('steps', []))}")
            print(f"      Transitions : {len(self.upgraded_sfc.get('transitions', []))}")
            print(f"      Variables   : {len(self.upgraded_sfc.get('variables', []))}")
            return True
        except Exception as e:
            print(f"    Parse ERROR: {e}")
            return False
    
    # FIX: usage-based evidence gathering. Instead of guessing a variable's
    # type purely from its name, scan every step action and transition
    # guard for how the variable is actually used, and let that evidence
    # override the name-heuristic fallback.
    def _build_usage_corpus(self, sfc_data):
        parts = []
        for s in sfc_data.get('steps', []):
            if isinstance(s, dict):
                parts.append(s.get('function', '') or '')
        for t in sfc_data.get('transitions', []):
            parts.append(str(t.get('guard', '') or ''))
        return "\n".join(parts)

    def _split_statements(self, corpus):
        chunks = []
        for line in corpus.split('\n'):
            chunks.extend(line.split(';'))
        return [stmt.strip() for stmt in chunks if stmt.strip()]

    def _var_is_fb_instance(self, var_name, corpus):
        call_pat = re.compile(rf'\b{re.escape(var_name)}\s*\(', re.IGNORECASE)
        member_pat = re.compile(rf'\b{re.escape(var_name)}\s*\.\s*\w+', re.IGNORECASE)
        return bool(call_pat.search(corpus) or member_pat.search(corpus))

    def _var_has_bool_evidence(self, var_name, statements):
        # accepts raw "==" (pre-translation) as well as IEC "="/"<>"
        op = r'(?::=|==|=|<>|!=)'
        pat = re.compile(
            rf'\b{re.escape(var_name)}\b\s*{op}\s*(TRUE|FALSE)\b'
            rf'|\b(TRUE|FALSE)\b\s*{op}\s*\b{re.escape(var_name)}\b',
            re.IGNORECASE
        )
        return any(pat.search(stmt) for stmt in statements)

    def _var_has_time_evidence(self, var_name, statements, corpus):
        lhs_pat = re.compile(rf'^\s*{re.escape(var_name)}\s*:=', re.IGNORECASE)
        for stmt in statements:
            if lhs_pat.search(stmt) and re.search(r'T#|_TO_TIME\s*\(', stmt, re.IGNORECASE):
                return True
        for pname in TIME_PARAM_NAMES:
            pat = re.compile(rf'\b{pname}\s*:=\s*{re.escape(var_name)}\b', re.IGNORECASE)
            if pat.search(corpus):
                return True
        return False

    def _var_literal_evidence(self, var_name, statements):
        lit_pat = re.compile(
            rf'\b{re.escape(var_name)}\b\s*:=\s*(BYTE|UINT|USINT|SINT|DINT|WORD|DWORD)#',
            re.IGNORECASE
        )
        for stmt in statements:
            m = lit_pat.search(stmt)
            if m:
                return m.group(1).upper()
        return None

    def _infer_variable_type(self, variable_dict, var_name="", corpus="", statements=None):
        if statements is None:
            statements = []

        # 1. Explicit type in the dict always wins
        if isinstance(variable_dict, dict):
            if 'type' in variable_dict and variable_dict['type']:
                return variable_dict['type']

        # 2. FB-instance detection (FIX: replaces hard-coded TIMER->TON /
        #    PWGEN->TP mapping)
        if var_name and self._var_is_fb_instance(var_name, corpus):
            v_upper = var_name.upper()
            return CUSTOM_FB_TYPE_OVERRIDES.get(var_name.lower(), v_upper)

        # 3. Init/value fields from the dict
        if isinstance(variable_dict, dict):
            if 'init' in variable_dict:
                init_val = variable_dict['init']
                if isinstance(init_val, bool): return 'BOOL'
                if isinstance(init_val, str) and init_val.upper() in ('TRUE', 'FALSE'): return 'BOOL'
                if isinstance(init_val, float): return 'REAL'
                if isinstance(init_val, int) and not isinstance(init_val, bool): return 'INT'
            if 'value' in variable_dict:
                val = variable_dict['value']
                if isinstance(val, bool): return 'BOOL'
                if isinstance(val, str) and val.upper() in ('TRUE', 'FALSE'): return 'BOOL'
                if isinstance(val, float): return 'REAL'
                if isinstance(val, int) and not isinstance(val, bool): return 'INT'

        # 4. FIX: usage-based evidence, checked in order of specificity
        if var_name:
            lit = self._var_literal_evidence(var_name, statements)
            if lit:
                return lit
            if self._var_has_bool_evidence(var_name, statements):
                return 'BOOL'
            if self._var_has_time_evidence(var_name, statements, corpus):
                return 'TIME'

        # 5. Name-pattern fallback (FIX: 'TIME' pulled OUT of the REAL
        #    bucket into its own case)
        if var_name:
            v_upper = var_name.upper()
            if any(pattern in v_upper for pattern in ['ENABLED', 'ACTIVE', 'FLAG', 'IS_', 'HAS_', 'VALID']):
                return 'BOOL'
            if v_upper.endswith('_CODE') or v_upper.endswith('_ID'):
                return 'UINT'
            if 'TIME' in v_upper:
                return 'TIME'
            if any(pattern in v_upper for pattern in ['TEMPERATURE', 'PRESSURE', 'VOLTAGE', 'CURRENT', 'FLOW', 'SPEED', 'POSITION', 'DISTANCE', 'WEIGHT', 'VALUE']):
                return 'REAL'
            if 'ERROR' in v_upper or 'STATUS' in v_upper:
                return 'BOOL'

        # Default fallback
        return 'INT'

    def _get_variable_init_value(self, variable_dict, var_type):
        # FIX: FB instances (anything not a scalar type) never get an
        # initializer.
        if var_type not in SCALAR_TYPES:
            return None
        if isinstance(variable_dict, dict):
            if 'init' in variable_dict:
                init_val = variable_dict['init']
                if var_type == 'BOOL':
                    if isinstance(init_val, bool): return 'TRUE' if init_val else 'FALSE'
                    elif isinstance(init_val, str) and init_val.upper() in ('TRUE', 'FALSE'): return init_val.upper()
                    else: return 'FALSE'
                else: return str(init_val)
            if 'value' in variable_dict:
                val = variable_dict['value']
                if var_type == 'BOOL':
                    if isinstance(val, bool): return 'TRUE' if val else 'FALSE'
                    elif isinstance(val, str) and val.upper() in ('TRUE', 'FALSE'): return val.upper()
                    else: return 'FALSE'
                else: return str(val)
        
        if var_type == 'BOOL': return 'FALSE'
        elif var_type in ('INT', 'DINT', 'UINT', 'USINT', 'SINT', 'BYTE', 'WORD', 'DWORD'): return '0'
        elif var_type in ('REAL', 'LREAL'): return '0.0'
        elif var_type == 'TIME': return 'T#0s'
        else: return '0'

    def _translate_guard(self, guard):
        expr = str(guard).strip() if guard is not None else ""
        if not expr: return "TRUE"
        expr = expr.replace("&&", " AND ").replace("||", " OR ")
        expr = expr.replace("!=", "<>")
        expr = expr.replace("==", "=")
        expr = re.sub(r"\bnot\b", "NOT", expr, flags=re.IGNORECASE)
        expr = re.sub(r"\band\b", "AND", expr, flags=re.IGNORECASE)
        expr = re.sub(r"\bor\b", "OR", expr, flags=re.IGNORECASE)
        expr = re.sub(r"\btrue\b", "TRUE", expr, flags=re.IGNORECASE)
        expr = re.sub(r"\bfalse\b", "FALSE", expr, flags=re.IGNORECASE)
        return expr
    
    def _generate_st(self, sfc_data, output_lines):
        L = output_lines
        steps = sfc_data.get('steps', [])
        transitions = sfc_data.get('transitions', [])
        variables = sfc_data.get('variables', [])
        initial_step = sfc_data.get('initial_step', None)

        # FIX: build the usage corpus once, up front, for type inference
        corpus = self._build_usage_corpus(sfc_data)
        statements = self._split_statements(corpus)
        
        L.append("PROGRAM SFC_Program")
        L.append("(* Auto-generated by SFCJSONConverter *)")
        L.append("")
        L.append("VAR")
        for s in steps:
            step_name = s.get('name', 'UNKNOWN') if isinstance(s, dict) else str(s)
            L.append(f"  {step_name}_active : BOOL := FALSE;")
        
        for v in variables:
            if isinstance(v, dict):
                vname = v.get('name', str(v))
                vtype = self._infer_variable_type(v, vname, corpus, statements)
            else:
                vname = str(v)
                vtype = self._infer_variable_type(None, vname, corpus, statements)
            init = self._get_variable_init_value(v, vtype)
            # FIX: only emit ":= init" for scalar types; FB instances get
            # a bare declaration (illegal otherwise: "invalid
            # initialization in function block declaration")
            if init is None:
                L.append(f"  {vname} : {vtype};")
            else:
                L.append(f"  {vname} : {vtype} := {init};")
        
        L.append("END_VAR")
        L.append("")
        L.append("(* --- Initialize initial step --- *)")
        L.append(f"IF NOT {initial_step}_active THEN")
        L.append(f"  {initial_step}_active := TRUE;")
        L.append("END_IF;")
        L.append("")
        L.append("(* --- Step actions --- *)")
        for s in steps:
            if isinstance(s, dict):
                step_name = s.get('name', 'UNKNOWN')
                step_func = s.get('function', '').strip()
            else:
                step_name = str(s)
                step_func = ''
            if step_func:
                # FIX: strip a pre-existing trailing ';' before adding our
                # own, to avoid "out := FALSE;;" double-semicolon errors
                if step_func.endswith(';'):
                    step_func = step_func[:-1].rstrip()
                L.append(f"IF {step_name}_active THEN")
                L.append(f"  {step_func};")
                L.append("END_IF;")
        
        L.append("")
        L.append("(* --- Transitions --- *)")
        for t in transitions:
            src = t.get('src', 'UNKNOWN')
            tgt = t.get('tgt', 'UNKNOWN')
            guard = self._translate_guard(t.get('guard', 'TRUE'))
            L.append(f"IF {src}_active AND ({guard}) THEN")
            L.append(f"  {src}_active := FALSE;")
            L.append(f"  {tgt}_active := TRUE;")
            L.append("END_IF;")
        
        L.append("")
        L.append("END_PROGRAM")
    
    def generate(self):
        print("\n  [STEP 2] Generating ST code for upgraded SFC ...")
        self.upgraded_st_lines.clear()
        self._generate_st(self.upgraded_sfc, self.upgraded_st_lines)
        print(f"    Upgraded ST : {len(self.upgraded_st_lines)} lines generated.")
    
    def save(self, upgraded_out):
        print(f"\n  [STEP 3] Saving : {upgraded_out}")
        try:
            with open(upgraded_out, 'w') as f:
                f.write("\n".join(self.upgraded_st_lines))
            return True
        except Exception as e:
            print(f"    Failed to save file: {e}")
            return False
    
    def compile(self, upgraded_st_file):
        print(f"\n  [STEP 4] Compiling upgraded ST file with iec2iec ...")
        result = subprocess.run(
            ["../matiec/iec2c", "-I", "../matiec/lib", upgraded_st_file],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            return True, "Compilation successful."
        else:
            err = result.stderr.strip() or result.stdout.strip()
            return False, err
        
    def run(self, upgraded_out=None):
        result = {
            "json_file"   : self.json_file,
            "steps"       : 0,
            "transitions" : 0,
            "variables"   : 0,
            "st_file"     : "",
            "compiler"    : "MATIEC",
            "status"      : "",
            "message"     : "",
            "timestamp"   : datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        
        parse_ok = self.parse()
        if not parse_ok:
            result.update(status="FAILED", message="Parse error")
            return result
        
        result["steps"]       = len(self.upgraded_sfc.get('steps', []))
        result["transitions"] = len(self.upgraded_sfc.get('transitions', []))
        result["variables"]   = len(self.upgraded_sfc.get('variables', []))
        
        self.generate()
        
        if upgraded_out is None:
            base = os.path.splitext(self.json_file)[0]
            upgraded_out = base + "_upgraded.st"
        
        result["st_file"] = upgraded_out
        
        if not self.save(upgraded_out):
            result.update(status="FAILED", message="Save error")
            return result
        
        u_ok, u_msg = self.compile(upgraded_out)
        
        result["status"] = "SUCCESS" if u_ok else "FAILED"
        result["message"] = u_msg
        
        if not u_ok:
            print(f"  DETAILS  :\n{result['message']}")
        
        return result

# ======================================================================== #
# Batch runner and Report Generator                                        #
# ======================================================================== #

def generate_txt_report(results, report_path):
    W = 65  
    lines = []

    def rule(char="="): return char * W
    def center(text): return text.center(W)
    def row(label, value): return f"  {label:<22} {value}"
  
    lines.append(rule("="))
    lines.append(center("SFC  ->  MATIEC  Compilation Batch Report"))
    lines.append(center(f"Generated : {datetime.datetime.now().strftime('%Y-%m-%d  %H:%M:%S')}"))
    lines.append(rule("="))
    lines.append("")
   
    for idx, r in enumerate(results, start=1):
        lines.append(rule("-"))
        lines.append(f"  FILE #{idx} of {len(results)}")
        lines.append(rule("-"))
        lines.append(row("SFC File    :", os.path.basename(r.get("json_file", ""))))
        lines.append(row("ST File     :", os.path.basename(r.get("st_file", "N/A"))))
        lines.append(row("Steps       :", r["steps"]))
        lines.append(row("Transitions :", r["transitions"]))
        lines.append(row("Variables   :", r["variables"]))
        lines.append(row("Compiler    :", r.get("compiler", "MATIEC")))
        lines.append(row("Status      :", f"[ {r['status']} ]"))
        lines.append(row("Timestamp   :", r["timestamp"]))
        if r["message"]:
            lines.append("")
            lines.append("  Message / Details:")
            for mline in r["message"].splitlines():
                lines.append(f"    {mline}")
        lines.append("")
   
    total     = len(results)
    successes = sum(1 for r in results if r["status"] == "SUCCESS")
    failures  = total - successes

    lines.append(rule("="))
    lines.append(center("BATCH  SUMMARY"))
    lines.append(rule("="))
    lines.append(row("Total Files :", total))
    lines.append(row("Succeeded   :", successes))
    lines.append(row("Failed      :", failures))
    lines.append("")
    lines.append(rule("-"))
    lines.append(f"  {'#':<5} {'File':<35} {'Compiler':<15} Status")
    lines.append(rule("-"))
    for idx, r in enumerate(results, start=1):
        icon = "[OK]  " if r["status"] == "SUCCESS" else "[FAIL]"
        name = os.path.basename(r.get("json_file", ""))[:34]
        lines.append(f"  {idx:<5} {name:<35} {r.get('compiler', 'MATIEC'):<15} {icon}")
    lines.append(rule("="))
    lines.append("")
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(lines))
    print(f"\n[REPORT] TXT report saved : {report_path}")

def main():
    if len(sys.argv) < 2:
        print("""
Usage (multiple files):
  python sfc_converter.py file1.json file2.json
Usage (folder):
  python sfc_converter.py --folder /path/to/json_files/
""")
        sys.exit(1)

    args = sys.argv[1:]
    txt_name = "json_batch_report.txt"
    json_files = []

    if "--report" in args:
        idx = args.index("--report")
        txt_name = args[idx + 1]
        args = [a for i, a in enumerate(args) if i not in (idx, idx+1)]

    if "--folder" in args:
        idx = args.index("--folder")
        folder = args[idx + 1]
        if not os.path.isdir(folder):
            print(f"[ERROR] Folder not found: {folder}")
            sys.exit(1)
        # Replaced custom codegenutil reader with standard python os.listdir
        json_files = [os.path.join(folder, f) for f in sorted(os.listdir(folder)) if f.endswith(".json")]
        if not json_files:
            print(f"[ERROR] No .json SFC files found in: {folder}")
            sys.exit(1)
    else:
        json_files = [f for f in args if f.endswith(".json")]

    if not json_files:
        print("[ERROR] No JSON files specified.")
        sys.exit(1)

    all_results = []
    total = len(json_files)
    print("\n" + "="*58)
    print(f"{'JSON SFC MATIEC Batch Converter (Upgraded Only)':^58}")
    print(f"{'Total files : ' + str(total):^58}")
    print("="*58)

    for idx, json_file in enumerate(json_files, start=1):
        print("\n" + "="*60)
        print(f"  [{idx}/{total}]  {json_file}")
        print("="*60)

        converter = SFCJSONConverter(json_file)
        result    = converter.run()
        all_results.append(result)

    successes = sum(1 for r in all_results if r["status"] == "SUCCESS")
    failures  = len(all_results) - successes
    print("\n" + "="*58)
    print(f"{'BATCH  SUMMARY':^58}")
    print(" "*58)
    print(f"  {'Total Files :':<22} {total:>32}")
    print(f"  {'Succeeded   :':<22} {successes:>32}")
    print(f"  {'Failed      :':<22} {failures:>32}")
    print("="*58)
    
    generate_txt_report(all_results, txt_name)

if __name__ == "__main__":
    main()