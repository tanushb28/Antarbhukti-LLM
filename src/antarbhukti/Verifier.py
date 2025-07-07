import subprocess
import base64
import os
import z3
import re
import ast

def infix_to_sexpr(expr):
    expr = expr.replace('&&', ' and ').replace('||', ' or ').replace('!', ' not ')
    expr = expr.replace('True', 'true').replace('False', 'false')
    expr = expr.replace('true', 'True').replace('false', 'False')
    expr = expr.replace('%', ' % ')
    expr = expr.replace('==', ' == ')
    expr = expr.replace('!=', ' != ')
    expr = expr.replace('>=', ' >= ')
    expr = expr.replace('<=', ' <= ')
    try:
        node = ast.parse(expr, mode='eval')
    except Exception:
        return expr
    def walk(node):
        if isinstance(node, ast.Expression):
            return walk(node.body)
        if isinstance(node, ast.BoolOp):
            op = {ast.And: 'and', ast.Or: 'or'}[type(node.op)]
            return f"({op} {' '.join([walk(v) for v in node.values])})"
        if isinstance(node, ast.UnaryOp):
            if isinstance(node.op, ast.Not):
                return f"(not {walk(node.operand)})"
        if isinstance(node, ast.BinOp):
            op = node.op
            left = walk(node.left)
            right = walk(node.right)
            if isinstance(op, ast.Mod):
                return f"(mod {left} {right})"
            if isinstance(op, ast.Add):
                return f"(+ {left} {right})"
            if isinstance(op, ast.Sub):
                return f"(- {left} {right})"
            if isinstance(op, ast.Mult):
                return f"(* {left} {right})"
            if isinstance(op, ast.Div):
                return f"(/ {left} {right})"
        if isinstance(node, ast.Compare):
            left = walk(node.left)
            if len(node.ops) == 1:
                op = node.ops[0]
                right = walk(node.comparators[0])
                if isinstance(op, ast.Eq):
                    return f"(= {left} {right})"
                if isinstance(op, ast.NotEq):
                    return f"(not (= {left} {right}))"
                if isinstance(op, ast.Lt):
                    return f"(< {left} {right})"
                if isinstance(op, ast.LtE):
                    return f"(<= {left} {right})"
                if isinstance(op, ast.Gt):
                    return f"(> {left} {right})"
                if isinstance(op, ast.GtE):
                    return f"(>= {left} {right})"
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Constant):
            return str(node.value).lower()
        return ""
    out = walk(node)
    return out

class SFC:
    def __init__(self, steps, variables, transitions, initial_step):
        self.steps = steps
        self.variables = variables
        self.transitions = transitions
        self.initial_step = initial_step
    def step_names(self):
        return [step["name"] for step in self.steps]
    def step_functions(self):
        return {step["name"]: step["function"] for step in self.steps}

def sfc_to_dot(sfc, dot_filename="sfc.dot"):
    with open(dot_filename, "w") as f:
        f.write("digraph SFC {\n")
        f.write('  rankdir=LR;\n')
        f.write('  node [fontname="Arial"];\n')
        fnmap = sfc.step_functions()
        for step in sfc.steps:
            fill = ' style=filled,fillcolor=lightblue' if step["name"] == sfc.initial_step else ""
            action = fnmap[step["name"]]
            f.write(f'  "{step["name"]}" [shape=box,label="{step["name"]}\\n{action}"{fill}];\n')
        for idx, t in enumerate(sfc.transitions):
            trans_name = f"TR_{idx+1}"
            guard = t.get("guard", "")
            label = guard if guard else ""
            f.write(f'  "{trans_name}" [shape=rect,style=bold,penwidth=3,width=0.2,height=0.5,label="{label}"];\n')
        for idx, t in enumerate(sfc.transitions):
            trans_name = f"TR_{idx+1}"
            srcs = t["src"] if isinstance(t["src"], list) else [t["src"]]
            tgts = t["tgt"] if isinstance(t["tgt"], list) else [t["tgt"]]
            for src in srcs:
                f.write(f'  "{src}" -> "{trans_name}";\n')
            for tgt in tgts:
                f.write(f'  "{trans_name}" -> "{tgt}";\n')
        f.write('  init [shape=point, width=0.2, color=black];\n')
        f.write(f'  init -> "{sfc.initial_step}" [arrowhead=normal];\n')
        f.write("}\n")

def sfc_to_petrinet(sfc: SFC):
    pn = {
        "places": sfc.step_names(),
        "functions": sfc.step_functions(),
        "transitions": [f"t_{i}" for i in range(len(sfc.transitions))],
        "transition_guards": {},
        "input_arcs": [],
        "output_arcs": [],
        "initial_marking": [sfc.initial_step]
    }
    for idx, t in enumerate(sfc.transitions):
        tid = f"t_{idx}"
        pn["transition_guards"][tid] = t.get("guard", "")
        srcs = t["src"] if isinstance(t["src"], list) else [t["src"]]
        tgts = t["tgt"] if isinstance(t["tgt"], list) else [t["tgt"]]
        for s in srcs:
            pn["input_arcs"].append((s, tid))
        for s in tgts:
            pn["output_arcs"].append((tid, s))
    return pn

def petrinet_to_dot(pn, dot_filename="pn.dot"):
    with open(dot_filename, "w") as f:
        f.write("digraph PN {\n")
        f.write('  rankdir=LR;\n')
        f.write('  node [fontname="Arial"];\n')
        for p in pn["places"]:
            func = pn["functions"].get(p, "")
            label = f"{p}\\n{func}" if func else p
            fill = ' style=filled,fillcolor=lightgray' if p in pn["initial_marking"] else ""
            f.write(f'  "{p}" [shape=circle,label="{label}"{fill}];\n')
        for t in pn["transitions"]:
            guard = pn["transition_guards"].get(t, "")
            label = t if not guard else f"{t}\\n[{guard}]"
            f.write(f'  "{t}" [shape=rect,width=0.3,height=0.7,label="{label}"];\n')
        for place, trans in pn["input_arcs"]:
            f.write(f'  "{place}" -> "{trans}";\n')
        for trans, place in pn["output_arcs"]:
            f.write(f'  "{trans}" -> "{place}";\n')
        f.write("}\n")

def dot_to_png(dot_filename, png_filename):
    try:
        subprocess.run(
            ["dot", "-Tpng", dot_filename, "-o", png_filename],
            check=True
        )
        print(f"{png_filename} generated.")
    except Exception as e:
        print(f"Error running Graphviz: {e}")

def find_cut_points(pn):
    out_transitions = {p: set() for p in pn["places"]}
    in_transitions = {p: set() for p in pn["places"]}
    trans_to_places = {t: set() for t in pn["transitions"]}
    for (p, t) in pn["input_arcs"]:
        if p in out_transitions:
            out_transitions[p].add(t)
    for (t, p) in pn["output_arcs"]:
        if p in in_transitions:
            in_transitions[p].add(t)
        if t in trans_to_places:
            trans_to_places[t].add(p)
    cut_points = set()
    for p in pn["initial_marking"]:
        cut_points.add(p)
    for p, outs in out_transitions.items():
        if len(outs) > 1:
            cut_points.add(p)
    for p in pn["places"]:
        if len(out_transitions[p]) == 0:
            cut_points.add(p)
    def has_back_edge(start_place):
        stack = []
        visited = set()
        for t in out_transitions[start_place]:
            for p2 in trans_to_places[t]:
                stack.append((p2, t))
        while stack:
            p, last_t = stack.pop()
            if p == start_place:
                return True
            for t2 in out_transitions.get(p, []):
                if (p, t2) not in visited:
                    visited.add((p, t2))
                    for p2 in trans_to_places[t2]:
                        stack.append((p2, t2))
        return False
    for p in pn["places"]:
        if has_back_edge(p):
            cut_points.add(p)
    return sorted(list(cut_points))

def cutpoint_to_cutpoint_paths_with_conditions(sfc, pn, cutpoints, allowed_variables=None):
    out_transitions = {p: set() for p in pn["places"]}
    trans_to_places = {t: set() for t in pn["transitions"]}
    for (p, t) in pn["input_arcs"]:
        out_transitions[p].add(t)
    for (t, p) in pn["output_arcs"]:
        if t in trans_to_places:
            trans_to_places[t].add(p)
    cutpoint_set = set(cutpoints)
    paths = []
    def to_z3_guard(guard):
        g = guard.strip()
        if g.lower() == "true" or g.lower() == "false":
            return g.lower()
        return infix_to_sexpr(g)
    def replace_whole_word(text, word, replacement):
        return re.sub(rf'\b{word}\b', replacement, text)
    def to_z3_assign(assign, subst):
        try:
            assigns = [a.strip() for a in assign.split(";") if a.strip()]
            out_pairs = []
            for a in assigns:
                if ':=' in a:
                    lhs, rhs = a.split(":=")
                    lhs = lhs.strip()
                    rhs = rhs.strip()
                    for var, val in subst.items():
                        rhs = replace_whole_word(rhs, var, val)
                    out_pairs.append((lhs, rhs))
            return out_pairs
        except Exception:
            return []
    def compute_condition_and_subst(path):
        guards = []
        subst = {v: v for v in sfc.variables}
        subst_history = []
        transitions = sfc.transitions
        step_functions = {step["name"]: step["function"] for step in sfc.steps}
        for t in path:
            idx = int(t.split('_')[1])
            guard = transitions[idx].get("guard", "")
            if guard and guard.lower() != "true":
                guards.append(to_z3_guard(guard))
            tgt = transitions[idx]["tgt"]
            if not isinstance(tgt, list):
                tgt = [tgt]
            for tgt_step in tgt:
                assign = step_functions.get(tgt_step, None)
                if assign:
                    pairs = to_z3_assign(assign, subst)
                    for lhs, rhs in pairs:
                        subst[lhs] = rhs
                        subst_history.append(f"(= {lhs} {infix_to_sexpr(rhs)})")
        z3_condition = "true" if not guards else f"(and {' '.join(guards)})" if len(guards) > 1 else guards[0]
        if allowed_variables is not None:
            filtered_subst = []
            for s in subst_history:
                m = re.match(r"\(= ([^ ]+)", s)
                if m and m.group(1) in allowed_variables:
                    filtered_subst.append(s)
            subst_history = filtered_subst
        z3_data_transform = (
            "true" if not subst_history else
            f"(and {' '.join(subst_history)})" if len(subst_history) > 1 else subst_history[0]
        )
        return z3_condition, z3_data_transform
    def dfs(current_place, current_path, visited, start_cut):
        if len(current_path) > 0 and current_place in cutpoint_set:
            if current_place != start_cut:
                cond, subst = compute_condition_and_subst(current_path)
                paths.append({
                    "from": start_cut,
                    "to": current_place,
                    "transitions": list(current_path),
                    "cond": cond,
                    "subst": subst
                })
            return
        for t in out_transitions.get(current_place, []):
            for p2 in trans_to_places[t]:
                if (p2, t) not in visited:
                    if p2 not in cutpoint_set or len(current_path) == 0:
                        visited.add((p2, t))
                        dfs(p2, current_path + [t], visited, start_cut)
                        visited.remove((p2, t))
    for cut in cutpoints:
        dfs(cut, [], set(), cut)
    return paths

def z3_vars(variable_names):
    return {v: z3.Int(v) for v in variable_names}

def preprocess_condition_for_equivalence(expr):
    expr = expr.strip()
    # Treat 'init' as 'true' for equivalence checking
    if expr == "init":
        return "true"
    return expr

def parse_z3_expr(expr, variables):
    def tokenize(s):
        s = s.replace('(', ' ( ').replace(')', ' ) ')
        return s.split()
    def parse(tokens):
        if not tokens:
            raise SyntaxError("Unexpected EOF")
        token = tokens.pop(0)
        if token == '(':
            L = []
            while tokens[0] != ')':
                L.append(parse(tokens))
                if not tokens:
                    raise SyntaxError("Missing ')'")
            tokens.pop(0)
            return L
        elif token == ')':
            raise SyntaxError("Unexpected ')'")
        else:
            return token
    def build(ast):
        if isinstance(ast, str):
            if ast in variables:
                return variables[ast]
            try:
                return int(ast)
            except ValueError:
                if ast.lower() == 'true':
                    return z3.BoolVal(True)
                if ast.lower() == 'false':
                    return z3.BoolVal(False)
                return ast
        if not isinstance(ast, list) or not ast:
            return ast
        head = ast[0]
        args = ast[1:]
        if head == 'and':
            return z3.And(*[build(a) for a in args])
        if head == 'or':
            return z3.Or(*[build(a) for a in args])
        if head == 'not':
            return z3.Not(build(args[0]))
        if head in ('=', '=='):
            return build(args[0]) == build(args[1])
        if head == '!=':
            return build(args[0]) != build(args[1])
        if head == '<':
            return build(args[0]) < build(args[1])
        if head == '<=':
            return build(args[0]) <= build(args[1])
        if head == '>':
            return build(args[0]) > build(args[1])
        if head == '>=':
            return build(args[0]) >= build(args[1])
        if head == '+':
            return build(args[0]) + build(args[1])
        if head == '-':
            return build(args[0]) - build(args[1])
        if head == '*':
            return build(args[0]) * build(args[1])
        if head == '/':
            return build(args[0]) / build(args[1])
        if head == 'mod':
            return build(args[0]) % build(args[1])
        return z3.BoolVal(True)
    expr = expr.strip()
    if expr == "true":
        return z3.BoolVal(True)
    if expr == "false":
        return z3.BoolVal(False)
    if expr in variables:
        return variables[expr]
    try:
        ast_parsed = parse(tokenize(expr))
        return build(ast_parsed)
    except Exception as e:
        print(f"Error parsing Z3 expr: {expr}, error: {e}")
        return None

def are_path_conditions_equivalent(cond1, cond2, variables):
    # Preprocess the conditions to treat 'init' as 'true'
    cond1 = preprocess_condition_for_equivalence(cond1)
    cond2 = preprocess_condition_for_equivalence(cond2)
    z3_vars_dict = z3_vars(variables)
    e1 = parse_z3_expr(cond1, z3_vars_dict)
    e2 = parse_z3_expr(cond2, z3_vars_dict)
    if e1 is None or e2 is None:
        return False
    if not (z3.is_expr(e1) and z3.is_expr(e2)):
        return False
    s = z3.Solver()
    s.add(e1 != e2)
    return s.check() == z3.unsat

def parse_z3_assignments(expr):
    expr = expr.strip()
    if expr == "true":
        return {}
    if expr.startswith("(and "):
        expr = expr[5:-1].strip()
    assignments = {}
    for m in re.finditer(r'\(\=\s*([^\s]+)\s+([^)]+)\)', expr):
        lhs = m.group(1)
        rhs = m.group(2).strip()
        assignments[lhs] = rhs
    return assignments

def are_data_transformations_equivalent(subst1, subst2, allowed_vars):
    d1 = parse_z3_assignments(subst1)
    d2 = parse_z3_assignments(subst2)
    for v in allowed_vars:
        v1 = d1.get(v, None)
        v2 = d2.get(v, None)
        if v1 != v2:
            return False
    return True

def html_escape(s):
    import html
    return html.escape(str(s))

def img_to_base64(path):
    if not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        data = f.read()
        return base64.b64encode(data).decode("ascii")

def check_pn_containment_html(sfc1, pn1, sfc2, pn2, img_paths={}):
    cutpoints1 = find_cut_points(pn1)
    cutpoints2 = find_cut_points(pn2)
    common_vars = list(sorted(set(sfc1.variables) & set(sfc2.variables)))
    paths1 = cutpoint_to_cutpoint_paths_with_conditions(sfc1, pn1, cutpoints1, allowed_variables=common_vars)
    paths2 = cutpoint_to_cutpoint_paths_with_conditions(sfc2, pn2, cutpoints2, allowed_variables=common_vars)
    unmatched1 = []
    matches1 = []
    for p1 in paths1:
        found = False
        for p2 in paths2:
            if are_path_conditions_equivalent(p1["cond"], p2["cond"], common_vars) \
               and are_data_transformations_equivalent(p1["subst"], p2["subst"], common_vars):
                found = True
                matches1.append((p1, p2))
                break
        if not found:
            unmatched1.append(p1)
    contained = not unmatched1
    html = ""
    html += "<html><head><title>Petri Net Model Containment Report</title>"
    html += """
    <style>
    body { font-family: Arial, sans-serif; }
    .contained { color: green; font-weight: bold; }
    .notcontained { color: red; font-weight: bold; }
    table { border-collapse: collapse; margin-bottom: 2em; }
    th, td { border: 1px solid #aaa; padding: 5px 10px; }
    th { background: #e4edfa; }
    .section { margin-top: 2em; }
    .path-table th, .path-table td { font-size: 13px; }
    pre { margin: 0; }
    .imgblock { margin: 1em 0; }
    </style></head><body>
    """
    html += "<h1>Petri Net Model Containment Report</h1>"
    html += "<div class='section'><h2>Model Diagrams</h2><table><tr>"
    for key, label in [
        ("sfc1", "SFC 1"), ("pn1", "PN 1"), ("sfc2", "SFC 2"), ("pn2", "PN 2")
    ]:
        html += f"<td style='text-align:center;'><b>{label}</b><br>"
        b64 = img_paths.get(key, None)
        if b64:
            html += f"<img class='imgblock' src='data:image/png;base64,{b64}' style='max-width:300px; max-height:300px;'/></td>"
        else:
            html += "<span style='color:red'>Image not found</span></td>"
    html += "</tr></table></div>"
    html += "<div class='section'><h2>Cut-Points</h2>"
    html += "<b>Model 1 Cut-Points:</b> " + ", ".join(html_escape(x) for x in cutpoints1) + "<br>"
    html += "<b>Model 2 Cut-Points:</b> " + ", ".join(html_escape(x) for x in cutpoints2) + "</div>"
    def path_table(paths, title):
        s = f"<div class='section'><h2>{title}</h2>"
        s += "<table class='path-table'><tr><th>From</th><th>To</th><th>Transitions</th><th>Z3 Condition</th><th>Z3 Data Transformation</th></tr>"
        for p in paths:
            s += "<tr>"
            s += "<td>%s</td><td>%s</td><td>%s</td><td><pre>%s</pre></td><td><pre>%s</pre></td>" % (
                html_escape(p['from']), html_escape(p['to']), html_escape(p['transitions']),
                html_escape(p['cond']), html_escape(p['subst'])
            )
            s += "</tr>"
        s += "</table></div>"
        return s
    html += path_table(paths1, "Model 1 Cut-Point Paths")
    html += path_table(paths2, "Model 2 Cut-Point Paths")
    html += "<div class='section'><h2>Path Mapping (Model 1 to Model 2)</h2>"
    if matches1:
        html += "<table class='path-table'><tr><th>Model 1 Path</th><th>Model 2 Path</th><th>Condition</th><th>Data Transformation</th></tr>"
        for p1, p2 in matches1:
            html += "<tr>"
            html += f"<td>{html_escape(p1['from'])}&rarr;{html_escape(p1['to'])} ({html_escape(p1['transitions'])})</td>"
            html += f"<td>{html_escape(p2['from'])}&rarr;{html_escape(p2['to'])} ({html_escape(p2['transitions'])})</td>"
            html += f"<td><pre>{html_escape(p1['cond'])}</pre></td>"
            html += f"<td><pre>{html_escape(p1['subst'])}</pre></td>"
            html += "</tr>"
        html += "</table>"
    else:
        html += "<div>No matched paths found.</div>"
    html += "</div>"
    if unmatched1:
        html += "<div class='section'><h2>Paths in Model 1 with NO equivalent path in Model 2</h2>"
        html += path_table(unmatched1, "")
    html += "<div class='section'><h2>Containment Result</h2>"
    if contained:
        html += "<span class='contained'>All paths of Model 1 are equivalent to some path of Model 2 (Model 1 is contained in Model 2).</span>"
    else:
        html += "<span class='notcontained'>There are paths in Model 1 that are not matched in Model 2 (Containment does NOT hold).</span>"
    html += "</div></body></html>"
    return html

if __name__ == "__main__":


    ######  Input  ####################################################################

    #######################  Trafic Light  ##########################################
    # steps1 = [
    #     {"name": "NormalOperation", "function": "GreenLight := True; YellowLight := False; RedLight := False"},
    #     {"name": "Pedestrian", "function": "GreenLight := False; YellowLight := True; RedLight := False"},
    #     {"name": "Emergency", "function": "GreenLight := False; YellowLight := False; RedLight := True"},
    #     {"name": "Cleanup", "function": "PedestrianRequest := False; EmergencyVehicle := False"},
    #     {"name": "End", "function": ""}
    # ]
  
    # transitions1 = [  
    #     {"src": "NormalOperation", "tgt": "Pedestrian", "guard": "PedestrianRequest==1"},  
    #     {"src": "NormalOperation", "tgt": "Emergency", "guard": "EmergencyVehicle==1"},  
    #     {"src": "Pedestrian", "tgt": "NormalOperation", "guard": "PedestrianRequest==0"},  
    #     {"src": "Emergency", "tgt": "NormalOperation", "guard": "EmergencyVehicle==0"},  
    #     {"src": "Cleanup", "tgt": "End", "guard": "True"}  
    # ]  
  
    # sfc1 = SFC(  
    #     steps=steps1,  
    #     variables=["GreenLight", "YellowLight", "RedLight", "PedestrianRequest", "EmergencyVehicle"],  
    #     transitions=transitions1,  
    #     initial_step="NormalOperation"  
    # )  
    ################################################################################


    # ###############   Factorial  ################################################
    # steps1 = [
    #     {"name": "Start", "function": "i := 1; fact := 1"},
    #     {"name": "Check", "function": ""},
    #     {"name": "Multiply", "function": "fact := fact * i"},
    #     {"name": "Increment", "function": "i := i + 1"},
    #     {"name": "End", "function": ""}
    # ]
    # transitions1 = [
    #     {"src": "Start", "tgt": "Check", "guard": "init"},
    #     {"src": "Check", "tgt": "Multiply", "guard": "i <= n"},
    #     {"src": "Multiply", "tgt": "Increment", "guard": "True"},
    #     {"src": "Increment", "tgt": "Check", "guard": "True"},
    #     {"src": "Check", "tgt": "End", "guard": "i > n"}
    # ]
    # sfc1 = SFC(
    #     steps=steps1, 
    #     variables=["i", "fact", "n", "init"],
    #     transitions=transitions1,
    #     initial_step="Start"
    # )
    #######################################################################################
   
   
###########################  DECTOHEX   #####################################################


    steps1 = [
        {"name": "Init", "function": "HexValue := ''; TempDecValue := DecValue; i := 9"},
        {"name": "CheckZero", "function": ""},
        {"name": "SetZero", "function": "HexValue := '0'; Convert := True"},
        {"name": "CheckRange", "function": ""},
        {"name": "SetError", "function": "HexValue := 'Error'; Convert := False"},
        {"name": "ConvertLoop", "function": ""},
        {"name": "BuildHex", "function": "TempHex := TempDecValue mod 16; HexValue := HexValue * 16 + TempHex; TempDecValue := TempDecValue / 16"},
        {"name": "CheckExit", "function": ""},
        {"name": "SetSuccess", "function": "Convert := True"},
        {"name": "End", "function": ""}
    ]

    transitions1 = [
        {"src": "Init", "tgt": "CheckZero", "guard": "init"},
        {"src": "CheckZero", "tgt": "SetZero", "guard": "DecValue = 0"},
        {"src": "SetZero", "tgt": "End", "guard": "True"},
        {"src": "CheckZero", "tgt": "CheckRange", "guard": "DecValue <> 0"},
        {"src": "CheckRange", "tgt": "SetError", "guard": "DecValue > 9999999999"},
        {"src": "SetError", "tgt": "End", "guard": "True"},
        {"src": "CheckRange", "tgt": "ConvertLoop", "guard": "DecValue <= 9999999999"},
        {"src": "ConvertLoop", "tgt": "BuildHex", "guard": "i >= 0"},
        {"src": "BuildHex", "tgt": "CheckExit", "guard": "True"},
        {"src": "CheckExit", "tgt": "SetSuccess", "guard": "TempDecValue = 0"},
        {"src": "SetSuccess", "tgt": "End", "guard": "True"},
        {"src": "CheckExit", "tgt": "ConvertLoop", "guard": "TempDecValue <> 0; i := i - 1"}
    ]

    sfc1 = SFC(
        steps=steps1,
        variables=["DecValue", "HexValue", "TempDecValue", "TempHex", "HexChars", "i", "Convert"],
        transitions=transitions1,
        initial_step="Init"
    )
  
    pn1 = sfc_to_petrinet(sfc1)

    # steps2 = [  
    #     {"name": "Start", "function": "i := 1; fact := 1; temp := 0"},  
    #     {"name": "Check", "function": ""},  
    #     {"name": "Multiply", "function": "fact := fact * i; temp := temp + 1"},  
    #     {"name": "Increment", "function": "i := i + 1"},  
    #     {"name": "Cleanup", "function": "temp := 0"},  
    #     {"name": "End", "function": ""}  
    # ]  
  
    # transitions2 = [  
    #     {"src": "Start", "tgt": "Check", "guard": "init"},  
    #     {"src": "Check", "tgt": "Multiply", "guard": "i <= n"},  
    #     {"src": "Multiply", "tgt": "Increment", "guard": "True"},  
    #     {"src": "Increment", "tgt": "Check", "guard": "True"},  
    #     {"src": "Check", "tgt": "Cleanup", "guard": "i > n"},  
    #     {"src": "Cleanup", "tgt": "End", "guard": "True"}  
    # ]  
  
    # sfc2 = SFC(  
    #     steps=steps2,  
    #     variables=["i", "fact", "n", "init", "temp"],  
    #     transitions=transitions2,  
    #     initial_step="Start"  
    # )  
    # 
    # 
    # ##### Factorial ######  First Prompt---> NOT Equivalent ##############################
   
   
    # steps2 = [  
    #         {"name": "Start", "function": "i := 1; fact := 1; temp := 0"},  
    #         {"name": "Check", "function": ""},  
    #         {"name": "Multiply", "function": "fact := fact * i"},  
    #         {"name": "Increment", "function": "i := i + 1; temp := temp + 1"},  
    #         {"name": "Cleanup", "function": "temp := 0"},  
    #         {"name": "End", "function": ""}  
    # ]  
  
    # transitions2 = [  
    #     {"src": "Start", "tgt": "Check", "guard": "init"},  
    #     {"src": "Check", "tgt": "Multiply", "guard": "i <= n"},  
    #     {"src": "Multiply", "tgt": "Increment", "guard": "True"},  
    #     {"src": "Increment", "tgt": "Check", "guard": "True"},  
    #     {"src": "Check", "tgt": "Cleanup", "guard": "i > n"},  
    #     {"src": "Cleanup", "tgt": "End", "guard": "True"},  
    #     {"src": "Check", "tgt": "End", "guard": "(> i n)", "z3_condition": True, "z3_data_transformation_check": True, "end": "t_4"}  
    # ]  
  
    # sfc2 = SFC(  
    #     steps=steps2,  
    #     variables=["i", "fact", "n", "init", "temp"],  
    #     transitions=transitions2,  
    #     initial_step="Start"  
    # ) 
    # 
    #  ######  Factorial ########### second promt---> Equivalent ###################
    # 
    # 


    # ################# DEC TO HEX Upgraded--R2 ##############################################
    #
    # steps2 = [
    #     {"name": "Init", "function": "HexValue := 0; TempDecValue := DecValue; i := 9"},
    #     {"name": "CheckZero", "function": ""},
    #     {"name": "SetZero", "function": "HexValue := 0; Convert := 1"},
    #     {"name": "CheckRange", "function": ""},
    #     {"name": "SetError", "function": "HexValue := -1; Convert := 0"},
    #     {"name": "ConvertLoop", "function": ""},
    #     {"name": "BuildHex", "function": "TempHex := 1 + TempDecValue mod 16; HexValue := TempHex; TempDecValue := TempDecValue / 16"},
    #     {"name": "CheckExit", "function": ""},
    #     {"name": "SetSuccess", "function": "Convert := 1"},
    #     {"name": "End", "function": ""}
    # ]

    # transitions2 = [
    #     {"src": "Init", "tgt": "CheckZero", "guard": "init"},
    #     {"src": "CheckZero", "tgt": "SetZero", "guard": "DecValue = 0"},
    #     {"src": "SetZero", "tgt": "End", "guard": "True"},
    #     {"src": "CheckZero", "tgt": "CheckRange", "guard": "DecValue <> 0"},
    #     {"src": "CheckRange", "tgt": "SetError", "guard": "DecValue > 9999999999"},
    #     {"src": "SetError", "tgt": "End", "guard": "True"},
    #     {"src": "CheckRange", "tgt": "ConvertLoop", "guard": "DecValue <= 9999999999"},
    #     {"src": "ConvertLoop", "tgt": "BuildHex", "guard": "i >= 0"},
    #     {"src": "BuildHex", "tgt": "CheckExit", "guard": "True"},
    #     {"src": "CheckExit", "tgt": "SetSuccess", "guard": "TempDecValue = 0"},
    #     {"src": "SetSuccess", "tgt": "End", "guard": "True"},
    #     {"src": "CheckExit", "tgt": "ConvertLoop", "guard": "TempDecValue <> 0; i := i - 1"}
    # ]

    # sfc2 = SFC(
    #     steps=steps2,
    #     variables=["DecValue", "HexValue", "TempDecValue", "TempHex", "HexChars", "i", "Convert"],
    #     transitions=transitions2,
    #     initial_step="Init"
    # )

    ######## First Prompt ---> Equivalent ###############################
    # #####################################################################






    ############### Add rules R1: Uses only integers/arithmetic, ready for direct
                  ##### use in hardware/PLCs.##############

    ###########################             #######                     ################################
    ##########################################################################
    
    # steps2 = [
    #     {"name": "Init", "function": "HexValue := 0; TempDecValue := DecValue; i := 9"},
    #     {"name": "CheckZero", "function": ""},
    #     {"name": "SetZero", "function": "HexValue := 0; Convert := 1"},
    #     {"name": "CheckRange", "function": ""},
    #     {"name": "SetError", "function": "HexValue := -1; Convert := 0"},
    #     {"name": "ConvertLoop", "function": ""},
    #     {"name": "BuildHex", "function": "TempHex := TempDecValue mod 16; HexValue := HexValue * 16 + TempHex; TempDecValue := TempDecValue / 16"},
    #     {"name": "CheckExit", "function": ""},
    #     {"name": "SetSuccess", "function": "Convert := 1"},
    #     {"name": "End", "function": ""}
    # ]

    # transitions2 = [
    #     {"src": "Init", "tgt": "CheckZero", "guard": "init"},
    #     {"src": "CheckZero", "tgt": "SetZero", "guard": "DecValue = 0"},
    #     {"src": "SetZero", "tgt": "End", "guard": "1"},
    #     {"src": "CheckZero", "tgt": "CheckRange", "guard": "DecValue <> 0"},
    #     {"src": "CheckRange", "tgt": "SetError", "guard": "DecValue > 9999999999"},
    #     {"src": "SetError", "tgt": "End", "guard": "1"},
    #     {"src": "CheckRange", "tgt": "ConvertLoop", "guard": "DecValue <= 9999999999"},
    #     {"src": "ConvertLoop", "tgt": "BuildHex", "guard": "i >= 0"},
    #     {"src": "BuildHex", "tgt": "CheckExit", "guard": "1"},
    #     {"src": "CheckExit", "tgt": "SetSuccess", "guard": "TempDecValue = 0"},
    #     {"src": "SetSuccess", "tgt": "End", "guard": "1"},
    #     {"src": "CheckExit", "tgt": "ConvertLoop", "guard": "TempDecValue <> 0; i := i - 1"}
    # ]

    # sfc2 = SFC(
    #     steps=steps2,
    #     variables=["DecValue", "HexValue", "TempDecValue", "TempHex", "i", "Convert"],
    #     transitions=transitions2,
    #     initial_step="Init"
    # )

    ########################### First Prompt---> Eqivalent #####################################

    pn2 = sfc_to_petrinet(sfc2)

    # Diagrams
    sfc_to_dot(sfc1, "sfc1.dot")
    dot_to_png("sfc1.dot", "sfc1.png")
    petrinet_to_dot(pn1, "pn1.dot")
    dot_to_png("pn1.dot", "pn1.png")
    sfc_to_dot(sfc2, "sfc2.dot")
    dot_to_png("sfc2.dot", "sfc2.png")
    petrinet_to_dot(pn2, "pn2.dot")
    dot_to_png("pn2.dot", "pn2.png")

    img_paths = {
        "sfc1": img_to_base64("sfc1.png"),
        "pn1": img_to_base64("pn1.png"),
        "sfc2": img_to_base64("sfc2.png"),
        "pn2": img_to_base64("pn2.png")
    }

    html_report = check_pn_containment_html(sfc1, pn1, sfc2, pn2, img_paths=img_paths)
    with open("pn_containment_report.html", "w") as f:
        f.write(html_report)
    print("HTML report written to pn_containment_report.html")



















###########################END####################################################










# import subprocess
# import base64
# import os
# import z3
# import re
# import ast

# def infix_to_sexpr(expr):
#     """
#     Converts a Python infix boolean/arithmetic expression to S-expression
#     usable by Z3's parser.
#     """
#     expr = expr.replace('&&', ' and ').replace('||', ' or ').replace('!', ' not ')
#     expr = expr.replace('True', 'true').replace('False', 'false')
#     expr = expr.replace('true', 'True').replace('false', 'False')
#     # Quick fix: replace % with mod and == with =
#     expr = expr.replace('%', ' % ')
#     expr = expr.replace('==', ' == ')
#     expr = expr.replace('!=', ' != ')
#     expr = expr.replace('>=', ' >= ')
#     expr = expr.replace('<=', ' <= ')

#     try:
#         node = ast.parse(expr, mode='eval')
#     except Exception:
#         return expr

#     def walk(node):
#         if isinstance(node, ast.Expression):
#             return walk(node.body)
#         if isinstance(node, ast.BoolOp):
#             op = {ast.And: 'and', ast.Or: 'or'}[type(node.op)]
#             return f"({op} {' '.join([walk(v) for v in node.values])})"
#         if isinstance(node, ast.UnaryOp):
#             if isinstance(node.op, ast.Not):
#                 return f"(not {walk(node.operand)})"
#         if isinstance(node, ast.BinOp):
#             op = node.op
#             left = walk(node.left)
#             right = walk(node.right)
#             if isinstance(op, ast.Mod):
#                 return f"(mod {left} {right})"
#             if isinstance(op, ast.Add):
#                 return f"(+ {left} {right})"
#             if isinstance(op, ast.Sub):
#                 return f"(- {left} {right})"
#             if isinstance(op, ast.Mult):
#                 return f"(* {left} {right})"
#             if isinstance(op, ast.Div):
#                 return f"(/ {left} {right})"
#         if isinstance(node, ast.Compare):
#             left = walk(node.left)
#             if len(node.ops) == 1:
#                 op = node.ops[0]
#                 right = walk(node.comparators[0])
#                 if isinstance(op, ast.Eq):
#                     return f"(= {left} {right})"
#                 if isinstance(op, ast.NotEq):
#                     return f"(not (= {left} {right}))"
#                 if isinstance(op, ast.Lt):
#                     return f"(< {left} {right})"
#                 if isinstance(op, ast.LtE):
#                     return f"(<= {left} {right})"
#                 if isinstance(op, ast.Gt):
#                     return f"(> {left} {right})"
#                 if isinstance(op, ast.GtE):
#                     return f"(>= {left} {right})"
#             # Chained comparisons...
#         if isinstance(node, ast.Name):
#             return node.id
#         if isinstance(node, ast.Constant):
#             return str(node.value).lower()
#         return ""

#     out = walk(node)
#     return out

# class SFC:
#     def __init__(self, steps, variables, transitions, initial_step):
#         self.steps = steps
#         self.variables = variables
#         self.transitions = transitions
#         self.initial_step = initial_step

#     def step_names(self):
#         return [step["name"] for step in self.steps]

#     def step_functions(self):
#         return {step["name"]: step["function"] for step in self.steps}

# def sfc_to_dot(sfc, dot_filename="sfc.dot"):
#     with open(dot_filename, "w") as f:
#         f.write("digraph SFC {\n")
#         f.write('  rankdir=LR;\n')
#         f.write('  node [fontname="Arial"];\n')
#         fnmap = sfc.step_functions()
#         for step in sfc.steps:
#             fill = ' style=filled,fillcolor=lightblue' if step["name"] == sfc.initial_step else ""
#             action = fnmap[step["name"]]
#             f.write(f'  "{step["name"]}" [shape=box,label="{step["name"]}\\n{action}"{fill}];\n')
#         for idx, t in enumerate(sfc.transitions):
#             trans_name = f"TR_{idx+1}"
#             guard = t.get("guard", "")
#             label = guard if guard else ""
#             f.write(f'  "{trans_name}" [shape=rect,style=bold,penwidth=3,width=0.2,height=0.5,label="{label}"];\n')
#         for idx, t in enumerate(sfc.transitions):
#             trans_name = f"TR_{idx+1}"
#             srcs = t["src"] if isinstance(t["src"], list) else [t["src"]]
#             tgts = t["tgt"] if isinstance(t["tgt"], list) else [t["tgt"]]
#             for src in srcs:
#                 f.write(f'  "{src}" -> "{trans_name}";\n')
#             for tgt in tgts:
#                 f.write(f'  "{trans_name}" -> "{tgt}";\n')
#         f.write('  init [shape=point, width=0.2, color=black];\n')
#         f.write(f'  init -> "{sfc.initial_step}" [arrowhead=normal];\n')
#         f.write("}\n")

# def sfc_to_petrinet(sfc: SFC):
#     pn = {
#         "places": sfc.step_names(),
#         "functions": sfc.step_functions(),
#         "transitions": [f"t_{i}" for i in range(len(sfc.transitions))],
#         "transition_guards": {},
#         "input_arcs": [],
#         "output_arcs": [],
#         "initial_marking": [sfc.initial_step]
#     }
#     for idx, t in enumerate(sfc.transitions):
#         tid = f"t_{idx}"
#         pn["transition_guards"][tid] = t.get("guard", "")
#         srcs = t["src"] if isinstance(t["src"], list) else [t["src"]]
#         tgts = t["tgt"] if isinstance(t["tgt"], list) else [t["tgt"]]
#         for s in srcs:
#             pn["input_arcs"].append((s, tid))
#         for s in tgts:
#             pn["output_arcs"].append((tid, s))
#     return pn

# def petrinet_to_dot(pn, dot_filename="pn.dot"):
#     with open(dot_filename, "w") as f:
#         f.write("digraph PN {\n")
#         f.write('  rankdir=LR;\n')
#         f.write('  node [fontname="Arial"];\n')
#         for p in pn["places"]:
#             func = pn["functions"].get(p, "")
#             label = f"{p}\\n{func}" if func else p
#             fill = ' style=filled,fillcolor=lightgray' if p in pn["initial_marking"] else ""
#             f.write(f'  "{p}" [shape=circle,label="{label}"{fill}];\n')
#         for t in pn["transitions"]:
#             guard = pn["transition_guards"].get(t, "")
#             label = t if not guard else f"{t}\\n[{guard}]"
#             f.write(f'  "{t}" [shape=rect,width=0.3,height=0.7,label="{label}"];\n')
#         for place, trans in pn["input_arcs"]:
#             f.write(f'  "{place}" -> "{trans}";\n')
#         for trans, place in pn["output_arcs"]:
#             f.write(f'  "{trans}" -> "{place}";\n')
#         f.write("}\n")

# def dot_to_png(dot_filename, png_filename):
#     try:
#         subprocess.run(
#             ["dot", "-Tpng", dot_filename, "-o", png_filename],
#             check=True
#         )
#         print(f"{png_filename} generated.")
#     except Exception as e:
#         print(f"Error running Graphviz: {e}")

# def find_cut_points(pn):
#     out_transitions = {p: set() for p in pn["places"]}
#     in_transitions = {p: set() for p in pn["places"]}
#     trans_to_places = {t: set() for t in pn["transitions"]}
#     for (p, t) in pn["input_arcs"]:
#         if p in out_transitions:
#             out_transitions[p].add(t)
#     for (t, p) in pn["output_arcs"]:
#         if p in in_transitions:
#             in_transitions[p].add(t)
#         if t in trans_to_places:
#             trans_to_places[t].add(p)
#     cut_points = set()
#     for p in pn["initial_marking"]:
#         cut_points.add(p)
#     for p, outs in out_transitions.items():
#         if len(outs) > 1:
#             cut_points.add(p)
#     for p in pn["places"]:
#         if len(out_transitions[p]) == 0:
#             cut_points.add(p)
#     def has_back_edge(start_place):
#         stack = []
#         visited = set()
#         for t in out_transitions[start_place]:
#             for p2 in trans_to_places[t]:
#                 stack.append((p2, t))
#         while stack:
#             p, last_t = stack.pop()
#             if p == start_place:
#                 return True
#             for t2 in out_transitions.get(p, []):
#                 if (p, t2) not in visited:
#                     visited.add((p, t2))
#                     for p2 in trans_to_places[t2]:
#                         stack.append((p2, t2))
#         return False
#     for p in pn["places"]:
#         if has_back_edge(p):
#             cut_points.add(p)
#     return sorted(list(cut_points))

# def cutpoint_to_cutpoint_paths_with_conditions(sfc, pn, cutpoints):
#     out_transitions = {p: set() for p in pn["places"]}
#     trans_to_places = {t: set() for t in pn["transitions"]}
#     for (p, t) in pn["input_arcs"]:
#         out_transitions[p].add(t)
#     for (t, p) in pn["output_arcs"]:
#         if t in trans_to_places:
#             trans_to_places[t].add(p)
#     cutpoint_set = set(cutpoints)
#     paths = []
#     def to_z3_guard(guard):
#         g = guard.strip()
#         if g.lower() == "true" or g.lower() == "false":
#             return g.lower()
#         return infix_to_sexpr(g)
#     def replace_whole_word(text, word, replacement):
#         return re.sub(rf'\b{word}\b', replacement, text)
#     def to_z3_assign(assign, subst):
#         try:
#             lhs, rhs = assign.split(":=")
#             lhs = lhs.strip()
#             rhs = rhs.strip()
#             for var, val in subst.items():
#                 rhs = replace_whole_word(rhs, var, val)
#             return lhs, rhs
#         except Exception:
#             return None, None
#     def compute_condition_and_subst(path):
#         guards = []
#         subst = {v: v for v in sfc.variables}
#         subst_history = []
#         transitions = sfc.transitions
#         step_functions = {step["name"]: step["function"] for step in sfc.steps}
#         for t in path:
#             idx = int(t.split('_')[1])
#             guard = transitions[idx].get("guard", "")
#             if guard and guard.lower() != "true":
#                 guards.append(to_z3_guard(guard))
#             tgt = transitions[idx]["tgt"]
#             if not isinstance(tgt, list):
#                 tgt = [tgt]
#             for tgt_step in tgt:
#                 assign = step_functions.get(tgt_step, None)
#                 if assign:
#                     lhs, rhs = to_z3_assign(assign, subst)
#                     if lhs is not None:
#                         subst[lhs] = rhs
#                         subst_history.append(f"(= {lhs} {rhs})")
#         z3_condition = "true" if not guards else f"(and {' '.join(guards)})" if len(guards) > 1 else guards[0]
#         z3_data_transform = "true" if not subst_history else f"(and {' '.join(subst_history)})" if len(subst_history) > 1 else subst_history[0]
#         return z3_condition, z3_data_transform
#     def dfs(current_place, current_path, visited, start_cut):
#         if len(current_path) > 0 and current_place in cutpoint_set:
#             if current_place != start_cut:
#                 cond, subst = compute_condition_and_subst(current_path)
#                 paths.append({
#                     "from": start_cut,
#                     "to": current_place,
#                     "transitions": list(current_path),
#                     "cond": cond,
#                     "subst": subst
#                 })
#             return
#         for t in out_transitions.get(current_place, []):
#             for p2 in trans_to_places[t]:
#                 if (p2, t) not in visited:
#                     if p2 not in cutpoint_set or len(current_path) == 0:
#                         visited.add((p2, t))
#                         dfs(p2, current_path + [t], visited, start_cut)
#                         visited.remove((p2, t))
#     for cut in cutpoints:
#         dfs(cut, [], set(), cut)
#     return paths

# def z3_vars(variable_names):
#     return {v: z3.Int(v) for v in variable_names}

# def parse_z3_expr(expr, variables):
#     def tokenize(s):
#         s = s.replace('(', ' ( ').replace(')', ' ) ')
#         return s.split()
#     tokens = tokenize(expr)
#     def parse(tokens):
#         if not tokens:
#             raise SyntaxError("Unexpected EOF")
#         token = tokens.pop(0)
#         if token == '(':
#             L = []
#             while tokens[0] != ')':
#                 L.append(parse(tokens))
#                 if not tokens:
#                     raise SyntaxError("Missing ')'")
#             tokens.pop(0)
#             return L
#         elif token == ')':
#             raise SyntaxError("Unexpected ')'")
#         else:
#             return token
#     def build(ast):
#         if isinstance(ast, str):
#             if ast in variables:
#                 return variables[ast]
#             try:
#                 return int(ast)
#             except ValueError:
#                 if ast.lower() == 'true':
#                     return z3.BoolVal(True)
#                 if ast.lower() == 'false':
#                     return z3.BoolVal(False)
#                 return ast
#         if not isinstance(ast, list) or not ast:
#             return ast
#         head = ast[0]
#         args = ast[1:]
#         if head == 'and':
#             return z3.And(*[build(a) for a in args])
#         if head == 'or':
#             return z3.Or(*[build(a) for a in args])
#         if head == 'not':
#             return z3.Not(build(args[0]))
#         if head in ('=', '=='):
#             return build(args[0]) == build(args[1])
#         if head == '!=':
#             return build(args[0]) != build(args[1])
#         if head == '<':
#             return build(args[0]) < build(args[1])
#         if head == '<=':
#             return build(args[0]) <= build(args[1])
#         if head == '>':
#             return build(args[0]) > build(args[1])
#         if head == '>=':
#             return build(args[0]) >= build(args[1])
#         if head == '+':
#             return build(args[0]) + build(args[1])
#         if head == '-':
#             return build(args[0]) - build(args[1])
#         if head == '*':
#             return build(args[0]) * build(args[1])
#         if head == '/':
#             return build(args[0]) / build(args[1])
#         if head == 'mod':
#             return build(args[0]) % build(args[1])
#         return z3.BoolVal(True)
#     if expr.strip() == "true":
#         return z3.BoolVal(True)
#     if expr.strip() == "false":
#         return z3.BoolVal(False)
#     try:
#         ast = parse(tokens)
#         return build(ast)
#     except Exception as e:
#         print(f"Error parsing Z3 expr: {expr}, error: {e}")
#         return None

# def are_path_conditions_equivalent(cond1, cond2, variables):
#     z3_vars_dict = z3_vars(variables)
#     e1 = parse_z3_expr(cond1, z3_vars_dict)
#     e2 = parse_z3_expr(cond2, z3_vars_dict)
#     if e1 is None or e2 is None:
#         return False
#     s = z3.Solver()
#     s.add(e1 != e2)
#     return s.check() == z3.unsat

# def are_data_transformations_identical(subst1, subst2, variables):
#     z3_vars_dict = z3_vars(variables)
#     e1 = parse_z3_expr(subst1, z3_vars_dict)
#     e2 = parse_z3_expr(subst2, z3_vars_dict)
#     if e1 is None or e2 is None:
#         return False
#     s = z3.Solver()
#     s.add(e1 != e2)
#     return s.check() == z3.unsat

# def html_escape(s):
#     import html
#     return html.escape(str(s))

# def img_to_base64(path):
#     if not os.path.exists(path):
#         return None
#     with open(path, "rb") as f:
#         data = f.read()
#         return base64.b64encode(data).decode("ascii")

# def check_pn_equivalence_html(sfc1, pn1, sfc2, pn2, img_paths={}):
#     cutpoints1 = find_cut_points(pn1)
#     cutpoints2 = find_cut_points(pn2)
#     paths1 = cutpoint_to_cutpoint_paths_with_conditions(sfc1, pn1, cutpoints1)
#     paths2 = cutpoint_to_cutpoint_paths_with_conditions(sfc2, pn2, cutpoints2)
#     unmatched1 = []
#     matches1 = []
#     for p1 in paths1:
#         found = False
#         for p2 in paths2:
#             if are_path_conditions_equivalent(p1["cond"], p2["cond"], sfc1.variables) \
#                and are_data_transformations_identical(p1["subst"], p2["subst"], sfc1.variables):
#                 found = True
#                 matches1.append((p1, p2))
#                 break
#         if not found:
#             unmatched1.append(p1)
#     unmatched2 = []
#     matches2 = []
#     for p2 in paths2:
#         found = False
#         for p1 in paths1:
#             if are_path_conditions_equivalent(p1["cond"], p2["cond"], sfc1.variables) \
#                and are_data_transformations_identical(p1["subst"], p2["subst"], sfc1.variables):
#                 found = True
#                 matches2.append((p2, p1))
#                 break
#         if not found:
#             unmatched2.append(p2)
#     equivalent = (not unmatched1) and (not unmatched2)
#     html = ""
#     html += "<html><head><title>Petri Net Model Equivalence Report</title>"
#     html += """
#     <style>
#     body { font-family: Arial, sans-serif; }
#     .equiv { color: green; font-weight: bold; }
#     .notequiv { color: red; font-weight: bold; }
#     table { border-collapse: collapse; margin-bottom: 2em; }
#     th, td { border: 1px solid #aaa; padding: 5px 10px; }
#     th { background: #e4edfa; }
#     .section { margin-top: 2em; }
#     .path-table th, .path-table td { font-size: 13px; }
#     pre { margin: 0; }
#     .imgblock { margin: 1em 0; }
#     </style></head><body>
#     """
#     html += "<h1>Petri Net Model Equivalence Report</h1>"
#     html += "<div class='section'><h2>Model Diagrams</h2><table><tr>"
#     for key, label in [
#         ("sfc1", "SFC 1"), ("pn1", "PN 1"), ("sfc2", "SFC 2"), ("pn2", "PN 2")
#     ]:
#         html += f"<td style='text-align:center;'><b>{label}</b><br>"
#         b64 = img_paths.get(key, None)
#         if b64:
#             html += f"<img class='imgblock' src='data:image/png;base64,{b64}' style='max-width:300px; max-height:300px;'/></td>"
#         else:
#             html += "<span style='color:red'>Image not found</span></td>"
#     html += "</tr></table></div>"
#     html += "<div class='section'><h2>Cut-Points</h2>"
#     html += "<b>Model 1 Cut-Points:</b> " + ", ".join(html_escape(x) for x in cutpoints1) + "<br>"
#     html += "<b>Model 2 Cut-Points:</b> " + ", ".join(html_escape(x) for x in cutpoints2) + "</div>"
#     def path_table(paths, title):
#         s = f"<div class='section'><h2>{title}</h2>"
#         s += "<table class='path-table'><tr><th>From</th><th>To</th><th>Transitions</th><th>Z3 Condition</th><th>Z3 Data Transformation</th></tr>"
#         for p in paths:
#             s += "<tr>"
#             s += "<td>%s</td><td>%s</td><td>%s</td><td><pre>%s</pre></td><td><pre>%s</pre></td>" % (
#                 html_escape(p['from']), html_escape(p['to']), html_escape(p['transitions']),
#                 html_escape(p['cond']), html_escape(p['subst'])
#             )
#             s += "</tr>"
#         s += "</table></div>"
#         return s
#     html += path_table(paths1, "Model 1 Cut-Point Paths")
#     html += path_table(paths2, "Model 2 Cut-Point Paths")
#     html += "<div class='section'><h2>Path Matching (Model 1 to Model 2)</h2>"
#     if matches1:
#         html += "<table class='path-table'><tr><th>Model 1 Path</th><th>Model 2 Path</th><th>Condition</th><th>Data Transformation</th></tr>"
#         for p1, p2 in matches1:
#             html += "<tr>"
#             html += f"<td>{html_escape(p1['from'])}&rarr;{html_escape(p1['to'])} ({html_escape(p1['transitions'])})</td>"
#             html += f"<td>{html_escape(p2['from'])}&rarr;{html_escape(p2['to'])} ({html_escape(p2['transitions'])})</td>"
#             html += f"<td><pre>{html_escape(p1['cond'])}</pre></td>"
#             html += f"<td><pre>{html_escape(p1['subst'])}</pre></td>"
#             html += "</tr>"
#         html += "</table>"
#     else:
#         html += "<div>No matched paths found.</div>"
#     html += "</div>"
#     if unmatched1:
#         html += "<div class='section'><h2>Paths in Model 1 with NO match in Model 2</h2>"
#         html += path_table(unmatched1, "")
#     if unmatched2:
#         html += "<div class='section'><h2>Paths in Model 2 with NO match in Model 1</h2>"
#         html += path_table(unmatched2, "")
#     html += "<div class='section'><h2>Equivalence Result</h2>"
#     if equivalent:
#         html += "<span class='equiv'>The two PN models are EQUIVALENT (all path conditions and data transformations match).</span>"
#     else:
#         html += "<span class='notequiv'>The two PN models are NOT equivalent.</span>"
#     html += "</div></body></html>"
#     return html

# if __name__ == "__main__":
#     # SFC1
#     # SFC for factorial
#     steps1 = [
#         {"name": "Start", "function": "i := 1; fact := 1"},
#         {"name": "Check", "function": ""},
#         {"name": "Multiply", "function": "fact := fact * i"},
#         {"name": "Increment", "function": "i := i + 1"},
#         {"name": "End", "function": ""}
#     ]
#     transitions1 = [
#         {"src": "Start", "tgt": "Check", "guard": "init"},
#         {"src": "Check", "tgt": "Multiply", "guard": "i <= n"},
#         {"src": "Multiply", "tgt": "Increment", "guard": "True"},
#         {"src": "Increment", "tgt": "Check", "guard": "True"},
#         {"src": "Check", "tgt": "End", "guard": "i > n"}
#     ]
#     sfc1 = SFC(
#         steps=steps1, 
#         variables=["i", "fact", "n", "init"],
#         transitions=transitions1,
#         initial_step="Start"
#     )
        
#     pn1 = sfc_to_petrinet(sfc1)

#     # SFC2 (identical for demo; modify for non-equivalent models)
#     # SFC variant for factorial (iterative, not recursive, SFC structure)
#     steps2 = [
#         {"name": "Init", "function": "fact := 1; i := n"},
#         {"name": "Check", "function": ""},
#         {"name": "Multiply", "function": "fact := fact * i"},
#         {"name": "Decrement", "function": "i := i + 1"},
#         {"name": "End", "function": ""}
#     ]
#     transitions2 = [
#         {"src": "Init", "tgt": "Check", "guard": "init"},
#         {"src": "Check", "tgt": "Multiply", "guard": "i <= n"},
#         {"src": "Multiply", "tgt": "Decrement", "guard": "True"},
#         {"src": "Decrement", "tgt": "Check", "guard": "True"},
#         {"src": "Check", "tgt": "End", "guard": "i >= n"}
#     ]
#     sfc2 = SFC(
#         steps=steps2, 
#         variables=["i", "fact", "n", "init"],
#         transitions=transitions2,
#         initial_step="Init"
#     )
#     pn2 = sfc_to_petrinet(sfc2)

#     # Generate diagrams for both PNs and SFCs
#     sfc_to_dot(sfc1, "sfc1.dot")
#     dot_to_png("sfc1.dot", "sfc1.png")
#     petrinet_to_dot(pn1, "pn1.dot")
#     dot_to_png("pn1.dot", "pn1.png")
#     sfc_to_dot(sfc2, "sfc2.dot")
#     dot_to_png("sfc2.dot", "sfc2.png")
#     petrinet_to_dot(pn2, "pn2.dot")
#     dot_to_png("pn2.dot", "pn2.png")

#     img_paths = {
#         "sfc1": img_to_base64("sfc1.png"),
#         "pn1": img_to_base64("pn1.png"),
#         "sfc2": img_to_base64("sfc2.png"),
#         "pn2": img_to_base64("pn2.png")
#     }

#     html_report = check_pn_equivalence_html(sfc1, pn1, sfc2, pn2, img_paths=img_paths)
#     with open("pn_equivalence_report.html", "w") as f:
#         f.write(html_report)
#     print("HTML report written to pn_equivalence_report.html")


##########################OLD Code using on string no z3 is calling#######################################

# import subprocess
# import base64
# import os

# class SFC:
#     def __init__(self, steps, variables, transitions, initial_step):
#         self.steps = steps
#         self.variables = variables
#         self.transitions = transitions
#         self.initial_step = initial_step

#     def step_names(self):
#         return [step["name"] for step in self.steps]

#     def step_functions(self):
#         return {step["name"]: step["function"] for step in self.steps}

# def sfc_to_dot(sfc, dot_filename="sfc.dot"):
#     with open(dot_filename, "w") as f:
#         f.write("digraph SFC {\n")
#         f.write('  rankdir=LR;\n')
#         f.write('  node [fontname="Arial"];\n')
#         fnmap = sfc.step_functions()
#         for step in sfc.steps:
#             fill = ' style=filled,fillcolor=lightblue' if step["name"] == sfc.initial_step else ""
#             action = fnmap[step["name"]]
#             f.write(f'  "{step["name"]}" [shape=box,label="{step["name"]}\\n{action}"{fill}];\n')
#         for idx, t in enumerate(sfc.transitions):
#             trans_name = f"TR_{idx+1}"
#             guard = t.get("guard", "")
#             label = guard if guard else ""
#             f.write(f'  "{trans_name}" [shape=rect,style=bold,penwidth=3,width=0.2,height=0.5,label="{label}"];\n')
#         for idx, t in enumerate(sfc.transitions):
#             trans_name = f"TR_{idx+1}"
#             srcs = t["src"] if isinstance(t["src"], list) else [t["src"]]
#             tgts = t["tgt"] if isinstance(t["tgt"], list) else [t["tgt"]]
#             for src in srcs:
#                 f.write(f'  "{src}" -> "{trans_name}";\n')
#             for tgt in tgts:
#                 f.write(f'  "{trans_name}" -> "{tgt}";\n')
#         f.write('  init [shape=point, width=0.2, color=black];\n')
#         f.write(f'  init -> "{sfc.initial_step}" [arrowhead=normal];\n')
#         f.write("}\n")

# def sfc_to_petrinet(sfc: SFC):
#     pn = {
#         "places": sfc.step_names(),
#         "functions": sfc.step_functions(),
#         "transitions": [f"t_{i}" for i in range(len(sfc.transitions))],
#         "transition_guards": {},
#         "input_arcs": [],
#         "output_arcs": [],
#         "initial_marking": [sfc.initial_step]
#     }
#     for idx, t in enumerate(sfc.transitions):
#         tid = f"t_{idx}"
#         pn["transition_guards"][tid] = t.get("guard", "")
#         srcs = t["src"] if isinstance(t["src"], list) else [t["src"]]
#         tgts = t["tgt"] if isinstance(t["tgt"], list) else [t["tgt"]]
#         for s in srcs:
#             pn["input_arcs"].append((s, tid))
#         for s in tgts:
#             pn["output_arcs"].append((tid, s))
#     return pn

# def petrinet_to_dot(pn, dot_filename="pn.dot"):
#     with open(dot_filename, "w") as f:
#         f.write("digraph PN {\n")
#         f.write('  rankdir=LR;\n')
#         f.write('  node [fontname="Arial"];\n')
#         for p in pn["places"]:
#             func = pn["functions"].get(p, "")
#             label = f"{p}\\n{func}" if func else p
#             fill = ' style=filled,fillcolor=lightgray' if p in pn["initial_marking"] else ""
#             f.write(f'  "{p}" [shape=circle,label="{label}"{fill}];\n')
#         for t in pn["transitions"]:
#             guard = pn["transition_guards"].get(t, "")
#             label = t if not guard else f"{t}\\n[{guard}]"
#             f.write(f'  "{t}" [shape=rect,width=0.3,height=0.7,label="{label}"];\n')
#         for place, trans in pn["input_arcs"]:
#             f.write(f'  "{place}" -> "{trans}";\n')
#         for trans, place in pn["output_arcs"]:
#             f.write(f'  "{trans}" -> "{place}";\n')
#         f.write("}\n")

# def dot_to_png(dot_filename, png_filename):
#     try:
#         subprocess.run(
#             ["dot", "-Tpng", dot_filename, "-o", png_filename],
#             check=True
#         )
#         print(f"{png_filename} generated.")
#     except Exception as e:
#         print(f"Error running Graphviz: {e}")

# def find_cut_points(pn):
#     out_transitions = {p: set() for p in pn["places"]}
#     in_transitions = {p: set() for p in pn["places"]}
#     trans_to_places = {t: set() for t in pn["transitions"]}
#     for (p, t) in pn["input_arcs"]:
#         if p in out_transitions:
#             out_transitions[p].add(t)
#     for (t, p) in pn["output_arcs"]:
#         if p in in_transitions:
#             in_transitions[p].add(t)
#         if t in trans_to_places:
#             trans_to_places[t].add(p)
#     cut_points = set()
#     for p in pn["initial_marking"]:
#         cut_points.add(p)
#     for p, outs in out_transitions.items():
#         if len(outs) > 1:
#             cut_points.add(p)
#     for p in pn["places"]:
#         if len(out_transitions[p]) == 0:
#             cut_points.add(p)
#     def has_back_edge(start_place):
#         stack = []
#         visited = set()
#         for t in out_transitions[start_place]:
#             for p2 in trans_to_places[t]:
#                 stack.append((p2, t))
#         while stack:
#             p, last_t = stack.pop()
#             if p == start_place:
#                 return True
#             for t2 in out_transitions.get(p, []):
#                 if (p, t2) not in visited:
#                     visited.add((p, t2))
#                     for p2 in trans_to_places[t2]:
#                         stack.append((p2, t2))
#         return False
#     for p in pn["places"]:
#         if has_back_edge(p):
#             cut_points.add(p)
#     return sorted(list(cut_points))

# def cutpoint_to_cutpoint_paths_with_conditions(sfc, pn, cutpoints):
#     out_transitions = {p: set() for p in pn["places"]}
#     trans_to_places = {t: set() for t in pn["transitions"]}
#     for (p, t) in pn["input_arcs"]:
#         out_transitions[p].add(t)
#     for (t, p) in pn["output_arcs"]:
#         if t in trans_to_places:
#             trans_to_places[t].add(p)
#     cutpoint_set = set(cutpoints)
#     paths = []
#     def to_z3_guard(guard):
#         g = guard.strip()
#         g = g.replace(" and ", " && ").replace(" or ", " || ").replace("not ", "!")
#         g = g.replace("&&", "and").replace("||", "or").replace("!", "not ")
#         g = g.replace("==", "=")
#         g = g.replace("%", " mod ")
#         g = g.replace("^", "**")
#         return g
#     def replace_whole_word(text, word, replacement):
#         import re
#         return re.sub(rf'\b{word}\b', replacement, text)
#     def to_z3_assign(assign, subst):
#         try:
#             lhs, rhs = assign.split(":=")
#             lhs = lhs.strip()
#             rhs = rhs.strip()
#             for var, val in subst.items():
#                 rhs = replace_whole_word(rhs, var, val)
#             return lhs, rhs
#         except Exception:
#             return None, None
#     def compute_condition_and_subst(path):
#         guards = []
#         subst = {v: v for v in sfc.variables}
#         subst_history = []
#         transitions = sfc.transitions
#         step_functions = {step["name"]: step["function"] for step in sfc.steps}
#         for t in path:
#             idx = int(t.split('_')[1])
#             guard = transitions[idx].get("guard", "")
#             if guard and guard.lower() != "true":
#                 guards.append(to_z3_guard(guard))
#             tgt = transitions[idx]["tgt"]
#             if not isinstance(tgt, list):
#                 tgt = [tgt]
#             for tgt_step in tgt:
#                 assign = step_functions.get(tgt_step, None)
#                 if assign:
#                     lhs, rhs = to_z3_assign(assign, subst)
#                     if lhs is not None:
#                         subst[lhs] = rhs
#                         subst_history.append(f"(= {lhs} {rhs})")
#         z3_condition = "true" if not guards else f"(and {' '.join(guards)})"
#         z3_data_transform = "true" if not subst_history else f"(and {' '.join(subst_history)})"
#         return z3_condition, z3_data_transform
#     def dfs(current_place, current_path, visited, start_cut):
#         if len(current_path) > 0 and current_place in cutpoint_set:
#             if current_place != start_cut:
#                 cond, subst = compute_condition_and_subst(current_path)
#                 paths.append({
#                     "from": start_cut,
#                     "to": current_place,
#                     "transitions": list(current_path),
#                     "cond": cond,
#                     "subst": subst
#                 })
#             return
#         for t in out_transitions.get(current_place, []):
#             for p2 in trans_to_places[t]:
#                 if (p2, t) not in visited:
#                     if p2 not in cutpoint_set or len(current_path) == 0:
#                         visited.add((p2, t))
#                         dfs(p2, current_path + [t], visited, start_cut)
#                         visited.remove((p2, t))
#     for cut in cutpoints:
#         dfs(cut, [], set(), cut)
#     return paths

# def normalize_z3_expr(expr):
#     import re
#     expr = expr.replace(" ", "")
#     expr = re.sub(r'\(and([^\)]*)\)', r'\1', expr)
#     expr = expr.replace("true", "")
#     return expr

# def are_path_conditions_equivalent(cond1, cond2):
#     return normalize_z3_expr(cond1) == normalize_z3_expr(cond2)

# def are_data_transformations_identical(subst1, subst2):
#     return normalize_z3_expr(subst1) == normalize_z3_expr(subst2)

# def html_escape(s):
#     import html
#     return html.escape(str(s))

# def img_to_base64(path):
#     if not os.path.exists(path):
#         return None
#     with open(path, "rb") as f:
#         data = f.read()
#         return base64.b64encode(data).decode("ascii")

# def check_pn_equivalence_html(sfc1, pn1, sfc2, pn2, img_paths={}):
#     cutpoints1 = find_cut_points(pn1)
#     cutpoints2 = find_cut_points(pn2)
#     paths1 = cutpoint_to_cutpoint_paths_with_conditions(sfc1, pn1, cutpoints1)
#     paths2 = cutpoint_to_cutpoint_paths_with_conditions(sfc2, pn2, cutpoints2)
#     unmatched1 = []
#     matches1 = []
#     for p1 in paths1:
#         found = False
#         for p2 in paths2:
#             if are_path_conditions_equivalent(p1["cond"], p2["cond"]) \
#                and are_data_transformations_identical(p1["subst"], p2["subst"]):
#                 found = True
#                 matches1.append((p1, p2))
#                 break
#         if not found:
#             unmatched1.append(p1)
#     unmatched2 = []
#     matches2 = []
#     for p2 in paths2:
#         found = False
#         for p1 in paths1:
#             if are_path_conditions_equivalent(p1["cond"], p2["cond"]) \
#                and are_data_transformations_identical(p1["subst"], p2["subst"]):
#                 found = True
#                 matches2.append((p2, p1))
#                 break
#         if not found:
#             unmatched2.append(p2)
#     equivalent = (not unmatched1) and (not unmatched2)
#     html = ""
#     html += "<html><head><title>Petri Net Model Equivalence Report</title>"
#     html += """
#     <style>
#     body { font-family: Arial, sans-serif; }
#     .equiv { color: green; font-weight: bold; }
#     .notequiv { color: red; font-weight: bold; }
#     table { border-collapse: collapse; margin-bottom: 2em; }
#     th, td { border: 1px solid #aaa; padding: 5px 10px; }
#     th { background: #e4edfa; }
#     .section { margin-top: 2em; }
#     .path-table th, .path-table td { font-size: 13px; }
#     pre { margin: 0; }
#     .imgblock { margin: 1em 0; }
#     </style></head><body>
#     """
#     html += "<h1>Petri Net Model Equivalence Report</h1>"

#     # Images (SFC1, SFC2, PN1, PN2)
#     html += "<div class='section'><h2>Model Diagrams</h2><table><tr>"
#     for key, label in [
#         ("sfc1", "SFC 1"), ("pn1", "PN 1"), ("sfc2", "SFC 2"), ("pn2", "PN 2")
#     ]:
#         html += f"<td style='text-align:center;'><b>{label}</b><br>"
#         b64 = img_paths.get(key, None)
#         if b64:
#             html += f"<img class='imgblock' src='data:image/png;base64,{b64}' style='max-width:300px; max-height:300px;'/></td>"
#         else:
#             html += "<span style='color:red'>Image not found</span></td>"
#     html += "</tr></table></div>"

#     html += "<div class='section'><h2>Cut-Points</h2>"
#     html += "<b>Model 1 Cut-Points:</b> " + ", ".join(html_escape(x) for x in cutpoints1) + "<br>"
#     html += "<b>Model 2 Cut-Points:</b> " + ", ".join(html_escape(x) for x in cutpoints2) + "</div>"
#     def path_table(paths, title):
#         s = f"<div class='section'><h2>{title}</h2>"
#         s += "<table class='path-table'><tr><th>From</th><th>To</th><th>Transitions</th><th>Z3 Condition</th><th>Z3 Data Transformation</th></tr>"
#         for p in paths:
#             s += "<tr>"
#             s += "<td>%s</td><td>%s</td><td>%s</td><td><pre>%s</pre></td><td><pre>%s</pre></td>" % (
#                 html_escape(p['from']), html_escape(p['to']), html_escape(p['transitions']),
#                 html_escape(p['cond']), html_escape(p['subst'])
#             )
#             s += "</tr>"
#         s += "</table></div>"
#         return s
#     html += path_table(paths1, "Model 1 Cut-Point Paths")
#     html += path_table(paths2, "Model 2 Cut-Point Paths")
#     html += "<div class='section'><h2>Path Matching (Model 1 to Model 2)</h2>"
#     if matches1:
#         html += "<table class='path-table'><tr><th>Model 1 Path</th><th>Model 2 Path</th><th>Condition</th><th>Data Transformation</th></tr>"
#         for p1, p2 in matches1:
#             html += "<tr>"
#             html += f"<td>{html_escape(p1['from'])}&rarr;{html_escape(p1['to'])} ({html_escape(p1['transitions'])})</td>"
#             html += f"<td>{html_escape(p2['from'])}&rarr;{html_escape(p2['to'])} ({html_escape(p2['transitions'])})</td>"
#             html += f"<td><pre>{html_escape(p1['cond'])}</pre></td>"
#             html += f"<td><pre>{html_escape(p1['subst'])}</pre></td>"
#             html += "</tr>"
#         html += "</table>"
#     else:
#         html += "<div>No matched paths found.</div>"
#     html += "</div>"
#     if unmatched1:
#         html += "<div class='section'><h2>Paths in Model 1 with NO match in Model 2</h2>"
#         html += path_table(unmatched1, "")
#     if unmatched2:
#         html += "<div class='section'><h2>Paths in Model 2 with NO match in Model 1</h2>"
#         html += path_table(unmatched2, "")
#     html += "<div class='section'><h2>Equivalence Result</h2>"
#     if equivalent:
#         html += "<span class='equiv'>The two PN models are EQUIVALENT (all path conditions and data transformations match).</span>"
#     else:
#         html += "<span class='notequiv'>The two PN models are NOT equivalent.</span>"
#     html += "</div></body></html>"
#     return html

# if __name__ == "__main__":
#     # SFC1
#     steps1 = [
#         {"name": "Start", "function": "x := 0"},
#         {"name": "LoopEntry", "function": "x := x + 1"},
#         {"name": "LoopBody", "function": "y := x / 2"},
#         {"name": "Branch1", "function": "z := y + 5"},
#         {"name": "Branch2", "function": "z := y + 3"}
#     ]
#     transitions1 = [
#         {"src": "Start", "tgt": "LoopEntry", "guard": "init"},
#         {"src": "LoopEntry", "tgt": "LoopBody", "guard": "True"},
#         {"src": "LoopBody", "tgt": "LoopEntry", "guard": "x < 3"},
#         {"src": "LoopBody", "tgt": "Branch1", "guard": "x >= 3 and x % 2 == 0"},
#         {"src": "LoopBody", "tgt": "Branch2", "guard": "x >= 3 and x % 2 == 1"},
#     ]
#     sfc1 = SFC(steps=steps1, variables=["x", "y", "z","k"], transitions=transitions1, initial_step="Start")
#     pn1 = sfc_to_petrinet(sfc1)

#     # SFC2 (identical for demo; modify for non-equivalent models)
#     steps2 = [
#         {"name": "Start", "function": "x := 0"},
#         {"name": "LoopEntry", "function": "x := x + 1"},
#         {"name": "LoopBody", "function": "y := x / 2"},
#         {"name": "Branch1", "function": "z := y + 5"},
#         {"name": "Branch2", "function": "z := y + 3"}
#     ]
#     transitions2 = [
#         {"src": "Start", "tgt": "LoopEntry", "guard": "init"},
#         {"src": "LoopEntry", "tgt": "LoopBody", "guard": "True"},
#         {"src": "LoopBody", "tgt": "LoopEntry", "guard": "x < 3"},
#         {"src": "LoopBody", "tgt": "Branch1", "guard": "x >= 3 and x % 2 == 0"},
#         {"src": "LoopBody", "tgt": "Branch2", "guard": "x >= 3 and x % 2 == 1"},
#     ]
#     sfc2 = SFC(steps=steps2, variables=["x", "y", "z"], transitions=transitions2, initial_step="Start")
#     pn2 = sfc_to_petrinet(sfc2)

#     # Generate diagrams for both PNs and SFCs
#     sfc_to_dot(sfc1, "sfc1.dot")
#     dot_to_png("sfc1.dot", "sfc1.png")
#     petrinet_to_dot(pn1, "pn1.dot")
#     dot_to_png("pn1.dot", "pn1.png")
#     sfc_to_dot(sfc2, "sfc2.dot")
#     dot_to_png("sfc2.dot", "sfc2.png")
#     petrinet_to_dot(pn2, "pn2.dot")
#     dot_to_png("pn2.dot", "pn2.png")

#     img_paths = {
#         "sfc1": img_to_base64("sfc1.png"),
#         "pn1": img_to_base64("pn1.png"),
#         "sfc2": img_to_base64("sfc2.png"),
#         "pn2": img_to_base64("pn2.png")
#     }

#     html_report = check_pn_equivalence_html(sfc1, pn1, sfc2, pn2, img_paths=img_paths)
#     with open("pn_equivalence_report.html", "w") as f:
#         f.write(html_report)
#     print("HTML report written to pn_equivalence_report.html")


#     #######################################OLD Code###################################

#     # import subprocess

# # class SFC:
# #     def __init__(self, steps, variables, transitions, initial_step):
# #         self.steps = steps
# #         self.variables = variables
# #         self.transitions = transitions
# #         self.initial_step = initial_step

# #     def step_names(self):
# #         return [step["name"] for step in self.steps]

# #     def step_functions(self):
# #         return {step["name"]: step["function"] for step in self.steps}

# # def sfc_to_dot(sfc, dot_filename="sfc.dot"):
# #     with open(dot_filename, "w") as f:
# #         f.write("digraph SFC {\n")
# #         f.write('  rankdir=LR;\n')
# #         f.write('  node [fontname="Arial"];\n')
# #         fnmap = sfc.step_functions()
# #         for step in sfc.steps:
# #             fill = ' style=filled,fillcolor=lightblue' if step["name"] == sfc.initial_step else ""
# #             action = fnmap[step["name"]]
# #             f.write(f'  "{step["name"]}" [shape=box,label="{step["name"]}\\n{action}"{fill}];\n')
# #         for idx, t in enumerate(sfc.transitions):
# #             trans_name = f"TR_{idx+1}"
# #             guard = t.get("guard", "")
# #             label = guard if guard else ""
# #             f.write(f'  "{trans_name}" [shape=rect,style=bold,penwidth=3,width=0.2,height=0.5,label="{label}"];\n')
# #         for idx, t in enumerate(sfc.transitions):
# #             trans_name = f"TR_{idx+1}"
# #             srcs = t["src"] if isinstance(t["src"], list) else [t["src"]]
# #             tgts = t["tgt"] if isinstance(t["tgt"], list) else [t["tgt"]]
# #             for src in srcs:
# #                 f.write(f'  "{src}" -> "{trans_name}";\n')
# #             for tgt in tgts:
# #                 f.write(f'  "{trans_name}" -> "{tgt}";\n')
# #         f.write('  init [shape=point, width=0.2, color=black];\n')
# #         f.write(f'  init -> "{sfc.initial_step}" [arrowhead=normal];\n')
# #         f.write("}\n")

# # def sfc_to_petrinet(sfc: SFC):
# #     pn = {
# #         "places": sfc.step_names(),
# #         "functions": sfc.step_functions(),
# #         "transitions": [f"t_{i}" for i in range(len(sfc.transitions))],
# #         "transition_guards": {},
# #         "input_arcs": [],
# #         "output_arcs": [],
# #         "initial_marking": [sfc.initial_step]
# #     }
# #     for idx, t in enumerate(sfc.transitions):
# #         tid = f"t_{idx}"
# #         pn["transition_guards"][tid] = t.get("guard", "")
# #         srcs = t["src"] if isinstance(t["src"], list) else [t["src"]]
# #         tgts = t["tgt"] if isinstance(t["tgt"], list) else [t["tgt"]]
# #         for s in srcs:
# #             pn["input_arcs"].append((s, tid))
# #         for s in tgts:
# #             pn["output_arcs"].append((tid, s))
# #     return pn

# # def petrinet_to_dot(pn, dot_filename="pn.dot"):
# #     with open(dot_filename, "w") as f:
# #         f.write("digraph PN {\n")
# #         f.write('  rankdir=LR;\n')
# #         f.write('  node [fontname="Arial"];\n')
# #         for p in pn["places"]:
# #             func = pn["functions"].get(p, "")
# #             label = f"{p}\\n{func}" if func else p
# #             fill = ' style=filled,fillcolor=lightgray' if p in pn["initial_marking"] else ""
# #             f.write(f'  "{p}" [shape=circle,label="{label}"{fill}];\n')
# #         for t in pn["transitions"]:
# #             guard = pn["transition_guards"].get(t, "")
# #             label = t if not guard else f"{t}\\n[{guard}]"
# #             f.write(f'  "{t}" [shape=rect,width=0.3,height=0.7,label="{label}"];\n')
# #         for place, trans in pn["input_arcs"]:
# #             f.write(f'  "{place}" -> "{trans}";\n')
# #         for trans, place in pn["output_arcs"]:
# #             f.write(f'  "{trans}" -> "{place}";\n')
# #         f.write("}\n")

# # def dot_to_png(dot_filename, png_filename):
# #     try:
# #         subprocess.run(
# #             ["dot", "-Tpng", dot_filename, "-o", png_filename],
# #             check=True
# #         )
# #         print(f"{png_filename} generated.")
# #     except Exception as e:
# #         print(f"Error running Graphviz: {e}")

# # def find_cut_points(pn):
# #     out_transitions = {p: set() for p in pn["places"]}
# #     in_transitions = {p: set() for p in pn["places"]}
# #     trans_to_places = {t: set() for t in pn["transitions"]}
# #     for (p, t) in pn["input_arcs"]:
# #         if p in out_transitions:
# #             out_transitions[p].add(t)
# #     for (t, p) in pn["output_arcs"]:
# #         if p in in_transitions:
# #             in_transitions[p].add(t)
# #         if t in trans_to_places:
# #             trans_to_places[t].add(p)

# #     cut_points = set()
# #     for p in pn["initial_marking"]:
# #         cut_points.add(p)
# #     for p, outs in out_transitions.items():
# #         if len(outs) > 1:
# #             cut_points.add(p)
# #     for p in pn["places"]:
# #         if len(out_transitions[p]) == 0:
# #             cut_points.add(p)

# #     def has_back_edge(start_place):
# #         stack = []
# #         visited = set()
# #         for t in out_transitions[start_place]:
# #             for p2 in trans_to_places[t]:
# #                 stack.append((p2, t))
# #         while stack:
# #             p, last_t = stack.pop()
# #             if p == start_place:
# #                 return True
# #             for t2 in out_transitions.get(p, []):
# #                 if (p, t2) not in visited:
# #                     visited.add((p, t2))
# #                     for p2 in trans_to_places[t2]:
# #                         stack.append((p2, t2))
# #         return False

# #     for p in pn["places"]:
# #         if has_back_edge(p):
# #             cut_points.add(p)
# #     return sorted(list(cut_points))

# # def cutpoint_to_cutpoint_paths_with_conditions(sfc, pn, cutpoints):
# #     out_transitions = {p: set() for p in pn["places"]}
# #     trans_to_places = {t: set() for t in pn["transitions"]}
# #     for (p, t) in pn["input_arcs"]:
# #         out_transitions[p].add(t)
# #     for (t, p) in pn["output_arcs"]:
# #         if t in trans_to_places:
# #             trans_to_places[t].add(p)
# #     cutpoint_set = set(cutpoints)
# #     paths = []

# #     def to_z3_guard(guard):
# #         g = guard.strip()
# #         g = g.replace(" and ", " && ").replace(" or ", " || ").replace("not ", "!")
# #         g = g.replace("&&", "and").replace("||", "or").replace("!", "not ")
# #         g = g.replace("==", "=")
# #         g = g.replace("%", " mod ")
# #         g = g.replace("^", "**")
# #         return g

# #     def replace_whole_word(text, word, replacement):
# #         import re
# #         return re.sub(rf'\b{word}\b', replacement, text)

# #     def to_z3_assign(assign, subst):
# #         try:
# #             lhs, rhs = assign.split(":=")
# #             lhs = lhs.strip()
# #             rhs = rhs.strip()
# #             for var, val in subst.items():
# #                 rhs = replace_whole_word(rhs, var, val)
# #             return lhs, rhs
# #         except Exception:
# #             return None, None

# #     def compute_condition_and_subst(path):
# #         guards = []
# #         subst = {v: v for v in sfc.variables}
# #         subst_history = []
# #         transitions = sfc.transitions
# #         step_functions = {step["name"]: step["function"] for step in sfc.steps}
# #         for t in path:
# #             idx = int(t.split('_')[1])
# #             guard = transitions[idx].get("guard", "")
# #             if guard and guard.lower() != "true":
# #                 guards.append(to_z3_guard(guard))
# #             tgt = transitions[idx]["tgt"]
# #             if not isinstance(tgt, list):
# #                 tgt = [tgt]
# #             for tgt_step in tgt:
# #                 assign = step_functions.get(tgt_step, None)
# #                 if assign:
# #                     lhs, rhs = to_z3_assign(assign, subst)
# #                     if lhs is not None:
# #                         subst[lhs] = rhs
# #                         subst_history.append(f"(= {lhs} {rhs})")
# #         z3_condition = "true" if not guards else f"(and {' '.join(guards)})"
# #         z3_data_transform = "true" if not subst_history else f"(and {' '.join(subst_history)})"
# #         return z3_condition, z3_data_transform

# #     def dfs(current_place, current_path, visited, start_cut):
# #         if len(current_path) > 0 and current_place in cutpoint_set:
# #             if current_place != start_cut:
# #                 cond, subst = compute_condition_and_subst(current_path)
# #                 paths.append({
# #                     "from": start_cut,
# #                     "to": current_place,
# #                     "transitions": list(current_path),
# #                     "cond": cond,
# #                     "subst": subst
# #                 })
# #             return
# #         for t in out_transitions.get(current_place, []):
# #             for p2 in trans_to_places[t]:
# #                 if (p2, t) not in visited:
# #                     if p2 not in cutpoint_set or len(current_path) == 0:
# #                         visited.add((p2, t))
# #                         dfs(p2, current_path + [t], visited, start_cut)
# #                         visited.remove((p2, t))
# #     for cut in cutpoints:
# #         dfs(cut, [], set(), cut)
# #     return paths

# # def normalize_z3_expr(expr):
# #     import re
# #     expr = expr.replace(" ", "")
# #     expr = re.sub(r'\(and([^\)]*)\)', r'\1', expr)
# #     expr = expr.replace("true", "")
# #     return expr

# # def are_path_conditions_equivalent(cond1, cond2):
# #     return normalize_z3_expr(cond1) == normalize_z3_expr(cond2)

# # def are_data_transformations_identical(subst1, subst2):
# #     return normalize_z3_expr(subst1) == normalize_z3_expr(subst2)

# # def check_pn_equivalence(sfc1, pn1, sfc2, pn2, verbose=True):
# #     cutpoints1 = find_cut_points(pn1)
# #     cutpoints2 = find_cut_points(pn2)
# #     paths1 = cutpoint_to_cutpoint_paths_with_conditions(sfc1, pn1, cutpoints1)
# #     paths2 = cutpoint_to_cutpoint_paths_with_conditions(sfc2, pn2, cutpoints2)

# #     unmatched1 = []
# #     matches1 = []
# #     for p1 in paths1:
# #         found = False
# #         for p2 in paths2:
# #             if are_path_conditions_equivalent(p1["cond"], p2["cond"]) \
# #                and are_data_transformations_identical(p1["subst"], p2["subst"]):
# #                 found = True
# #                 matches1.append((p1, p2))
# #                 break
# #         if not found:
# #             unmatched1.append(p1)

# #     unmatched2 = []
# #     matches2 = []
# #     for p2 in paths2:
# #         found = False
# #         for p1 in paths1:
# #             if are_path_conditions_equivalent(p1["cond"], p2["cond"]) \
# #                and are_data_transformations_identical(p1["subst"], p2["subst"]):
# #                 found = True
# #                 matches2.append((p2, p1))
# #                 break
# #         if not found:
# #             unmatched2.append(p2)

# #     equivalent = (not unmatched1) and (not unmatched2)

# #     if verbose:
# #         print("\n--- Petri Net Model Equivalence Report ---\n")
# #         print("Model 1 Cut-Points:", cutpoints1)
# #         print("Model 2 Cut-Points:", cutpoints2)
# #         print("\nPaths in Model 1 (from cut-point to cut-point):")
# #         for p in paths1:
# #             print(f"  {p['from']} -> {p['to']}: transitions={p['transitions']}")
# #             print(f"    [Z3] Condition: {p['cond']}")
# #             print(f"    [Z3] Data transformation: {p['subst']}")
# #         print("\nPaths in Model 2 (from cut-point to cut-point):")
# #         for p in paths2:
# #             print(f"  {p['from']} -> {p['to']}: transitions={p['transitions']}")
# #             print(f"    [Z3] Condition: {p['cond']}")
# #             print(f"    [Z3] Data transformation: {p['subst']}")
# #         print("\nPath Matching (Model 1 to Model 2):")
# #         for p1, p2 in matches1:
# #             print(f"  Model1: {p1['from']} -> {p1['to']} matches Model2: {p2['from']} -> {p2['to']}")
# #             print(f"    Condition: {p1['cond']}")
# #             print(f"    Data transformation: {p1['subst']}")
# #         if unmatched1:
# #             print("\nPaths in Model 1 with NO match in Model 2:")
# #             for p in unmatched1:
# #                 print(f"  {p['from']} -> {p['to']}: transitions={p['transitions']}")
# #                 print(f"    [Z3] Condition: {p['cond']}")
# #                 print(f"    [Z3] Data transformation: {p['subst']}")
# #         if unmatched2:
# #             print("\nPaths in Model 2 with NO match in Model 1:")
# #             for p in unmatched2:
# #                 print(f"  {p['from']} -> {p['to']}: transitions={p['transitions']}")
# #                 print(f"    [Z3] Condition: {p['cond']}")
# #                 print(f"    [Z3] Data transformation: {p['subst']}")
# #         print("\n--- End of Report ---\n")
# #         if equivalent:
# #             print("RESULT: The two PN models are EQUIVALENT (all path conditions and data transformations match).")
# #         else:
# #             print("RESULT: The two PN models are NOT equivalent.")

# #     return equivalent, unmatched1, unmatched2

# # if __name__ == "__main__":
# #     # SFC1
# #     steps1 = [
# #         {"name": "Start", "function": "x := 0"},
# #         {"name": "LoopEntry", "function": "x := x + 1"},
# #         {"name": "LoopBody", "function": "y := x * 2"},
# #         {"name": "Branch1", "function": "z := y + 5"},
# #         {"name": "Branch2", "function": "z := y - 3"}
# #     ]
# #     transitions1 = [
# #         {"src": "Start", "tgt": "LoopEntry", "guard": "init"},
# #         {"src": "LoopEntry", "tgt": "LoopBody", "guard": "True"},
# #         {"src": "LoopBody", "tgt": "LoopEntry", "guard": "x < 3"},
# #         {"src": "LoopBody", "tgt": "Branch1", "guard": "x >= 3 and x % 2 == 0"},
# #         {"src": "LoopBody", "tgt": "Branch2", "guard": "x >= 3 and x % 2 == 1"},
# #     ]
# #     sfc1 = SFC(
# #         steps=steps1,
# #         variables=["x", "y", "z"],
# #         transitions=transitions1,
# #         initial_step="Start"
# #     )
# #     pn1 = sfc_to_petrinet(sfc1)

# #     # SFC2 (identical for demo; modify for non-equivalent models)
# #     steps2 = [
# #         {"name": "Start", "function": "x := 0"},
# #         {"name": "LoopEntry", "function": "x := x + 1"},
# #         {"name": "LoopBody", "function": "y := x * 2"},
# #         {"name": "Branch1", "function": "z := y + 5"},
# #         {"name": "Branch2", "function": "z := y - 3"}
# #     ]
# #     transitions2 = [
# #         {"src": "Start", "tgt": "LoopEntry", "guard": "init"},
# #         {"src": "LoopEntry", "tgt": "LoopBody", "guard": "True"},
# #         {"src": "LoopBody", "tgt": "LoopEntry", "guard": "x < 3"},
# #         {"src": "LoopBody", "tgt": "Branch1", "guard": "x >= 3 and x % 2 == 0"},
# #         {"src": "LoopBody", "tgt": "Branch2", "guard": "x >= 3 and x % 2 == 1"},
# #     ]
# #     sfc2 = SFC(
# #         steps=steps2,
# #         variables=["x", "y", "z"],
# #         transitions=transitions2,
# #         initial_step="Start"
# #     )
# #     pn2 = sfc_to_petrinet(sfc2)

# #     # Generate diagrams for both PNs
# #     sfc_to_dot(sfc1, "sfc1.dot")
# #     dot_to_png("sfc1.dot", "sfc1.png")
# #     petrinet_to_dot(pn1, "pn1.dot")
# #     dot_to_png("pn1.dot", "pn1.png")

# #     sfc_to_dot(sfc2, "sfc2.dot")
# #     dot_to_png("sfc2.dot", "sfc2.png")
# #     petrinet_to_dot(pn2, "pn2.dot")
# #     dot_to_png("pn2.dot", "pn2.png")

# #     # Check equivalence (now verbose)
# #     equivalent, unmatched1, unmatched2 = check_pn_equivalence(sfc1, pn1, sfc2, pn2, verbose=True)

# #########################################################################HTML#################################

# # import subprocess

# # class SFC:
# #     def __init__(self, steps, variables, transitions, initial_step):
# #         self.steps = steps
# #         self.variables = variables
# #         self.transitions = transitions
# #         self.initial_step = initial_step

# #     def step_names(self):
# #         return [step["name"] for step in self.steps]

# #     def step_functions(self):
# #         return {step["name"]: step["function"] for step in self.steps}

# # def sfc_to_dot(sfc, dot_filename="sfc.dot"):
# #     with open(dot_filename, "w") as f:
# #         f.write("digraph SFC {\n")
# #         f.write('  rankdir=LR;\n')
# #         f.write('  node [fontname="Arial"];\n')
# #         fnmap = sfc.step_functions()
# #         for step in sfc.steps:
# #             fill = ' style=filled,fillcolor=lightblue' if step["name"] == sfc.initial_step else ""
# #             action = fnmap[step["name"]]
# #             f.write(f'  "{step["name"]}" [shape=box,label="{step["name"]}\\n{action}"{fill}];\n')
# #         for idx, t in enumerate(sfc.transitions):
# #             trans_name = f"TR_{idx+1}"
# #             guard = t.get("guard", "")
# #             label = guard if guard else ""
# #             f.write(f'  "{trans_name}" [shape=rect,style=bold,penwidth=3,width=0.2,height=0.5,label="{label}"];\n')
# #         for idx, t in enumerate(sfc.transitions):
# #             trans_name = f"TR_{idx+1}"
# #             srcs = t["src"] if isinstance(t["src"], list) else [t["src"]]
# #             tgts = t["tgt"] if isinstance(t["tgt"], list) else [t["tgt"]]
# #             for src in srcs:
# #                 f.write(f'  "{src}" -> "{trans_name}";\n')
# #             for tgt in tgts:
# #                 f.write(f'  "{trans_name}" -> "{tgt}";\n')
# #         f.write('  init [shape=point, width=0.2, color=black];\n')
# #         f.write(f'  init -> "{sfc.initial_step}" [arrowhead=normal];\n')
# #         f.write("}\n")

# # def sfc_to_petrinet(sfc: SFC):
# #     pn = {
# #         "places": sfc.step_names(),
# #         "functions": sfc.step_functions(),
# #         "transitions": [f"t_{i}" for i in range(len(sfc.transitions))],
# #         "transition_guards": {},
# #         "input_arcs": [],
# #         "output_arcs": [],
# #         "initial_marking": [sfc.initial_step]
# #     }
# #     for idx, t in enumerate(sfc.transitions):
# #         tid = f"t_{idx}"
# #         pn["transition_guards"][tid] = t.get("guard", "")
# #         srcs = t["src"] if isinstance(t["src"], list) else [t["src"]]
# #         tgts = t["tgt"] if isinstance(t["tgt"], list) else [t["tgt"]]
# #         for s in srcs:
# #             pn["input_arcs"].append((s, tid))
# #         for s in tgts:
# #             pn["output_arcs"].append((tid, s))
# #     return pn

# # def petrinet_to_dot(pn, dot_filename="pn.dot"):
# #     with open(dot_filename, "w") as f:
# #         f.write("digraph PN {\n")
# #         f.write('  rankdir=LR;\n')
# #         f.write('  node [fontname="Arial"];\n')
# #         for p in pn["places"]:
# #             func = pn["functions"].get(p, "")
# #             label = f"{p}\\n{func}" if func else p
# #             fill = ' style=filled,fillcolor=lightgray' if p in pn["initial_marking"] else ""
# #             f.write(f'  "{p}" [shape=circle,label="{label}"{fill}];\n')
# #         for t in pn["transitions"]:
# #             guard = pn["transition_guards"].get(t, "")
# #             label = t if not guard else f"{t}\\n[{guard}]"
# #             f.write(f'  "{t}" [shape=rect,width=0.3,height=0.7,label="{label}"];\n')
# #         for place, trans in pn["input_arcs"]:
# #             f.write(f'  "{place}" -> "{trans}";\n')
# #         for trans, place in pn["output_arcs"]:
# #             f.write(f'  "{trans}" -> "{place}";\n')
# #         f.write("}\n")

# # def dot_to_png(dot_filename, png_filename):
# #     try:
# #         subprocess.run(
# #             ["dot", "-Tpng", dot_filename, "-o", png_filename],
# #             check=True
# #         )
# #         print(f"{png_filename} generated.")
# #     except Exception as e:
# #         print(f"Error running Graphviz: {e}")

# # def find_cut_points(pn):
# #     out_transitions = {p: set() for p in pn["places"]}
# #     in_transitions = {p: set() for p in pn["places"]}
# #     trans_to_places = {t: set() for t in pn["transitions"]}
# #     for (p, t) in pn["input_arcs"]:
# #         if p in out_transitions:
# #             out_transitions[p].add(t)
# #     for (t, p) in pn["output_arcs"]:
# #         if p in in_transitions:
# #             in_transitions[p].add(t)
# #         if t in trans_to_places:
# #             trans_to_places[t].add(p)
# #     cut_points = set()
# #     for p in pn["initial_marking"]:
# #         cut_points.add(p)
# #     for p, outs in out_transitions.items():
# #         if len(outs) > 1:
# #             cut_points.add(p)
# #     for p in pn["places"]:
# #         if len(out_transitions[p]) == 0:
# #             cut_points.add(p)
# #     def has_back_edge(start_place):
# #         stack = []
# #         visited = set()
# #         for t in out_transitions[start_place]:
# #             for p2 in trans_to_places[t]:
# #                 stack.append((p2, t))
# #         while stack:
# #             p, last_t = stack.pop()
# #             if p == start_place:
# #                 return True
# #             for t2 in out_transitions.get(p, []):
# #                 if (p, t2) not in visited:
# #                     visited.add((p, t2))
# #                     for p2 in trans_to_places[t2]:
# #                         stack.append((p2, t2))
# #         return False
# #     for p in pn["places"]:
# #         if has_back_edge(p):
# #             cut_points.add(p)
# #     return sorted(list(cut_points))

# # def cutpoint_to_cutpoint_paths_with_conditions(sfc, pn, cutpoints):
# #     out_transitions = {p: set() for p in pn["places"]}
# #     trans_to_places = {t: set() for t in pn["transitions"]}
# #     for (p, t) in pn["input_arcs"]:
# #         out_transitions[p].add(t)
# #     for (t, p) in pn["output_arcs"]:
# #         if t in trans_to_places:
# #             trans_to_places[t].add(p)
# #     cutpoint_set = set(cutpoints)
# #     paths = []
# #     def to_z3_guard(guard):
# #         g = guard.strip()
# #         g = g.replace(" and ", " && ").replace(" or ", " || ").replace("not ", "!")
# #         g = g.replace("&&", "and").replace("||", "or").replace("!", "not ")
# #         g = g.replace("==", "=")
# #         g = g.replace("%", " mod ")
# #         g = g.replace("^", "**")
# #         return g
# #     def replace_whole_word(text, word, replacement):
# #         import re
# #         return re.sub(rf'\b{word}\b', replacement, text)
# #     def to_z3_assign(assign, subst):
# #         try:
# #             lhs, rhs = assign.split(":=")
# #             lhs = lhs.strip()
# #             rhs = rhs.strip()
# #             for var, val in subst.items():
# #                 rhs = replace_whole_word(rhs, var, val)
# #             return lhs, rhs
# #         except Exception:
# #             return None, None
# #     def compute_condition_and_subst(path):
# #         guards = []
# #         subst = {v: v for v in sfc.variables}
# #         subst_history = []
# #         transitions = sfc.transitions
# #         step_functions = {step["name"]: step["function"] for step in sfc.steps}
# #         for t in path:
# #             idx = int(t.split('_')[1])
# #             guard = transitions[idx].get("guard", "")
# #             if guard and guard.lower() != "true":
# #                 guards.append(to_z3_guard(guard))
# #             tgt = transitions[idx]["tgt"]
# #             if not isinstance(tgt, list):
# #                 tgt = [tgt]
# #             for tgt_step in tgt:
# #                 assign = step_functions.get(tgt_step, None)
# #                 if assign:
# #                     lhs, rhs = to_z3_assign(assign, subst)
# #                     if lhs is not None:
# #                         subst[lhs] = rhs
# #                         subst_history.append(f"(= {lhs} {rhs})")
# #         z3_condition = "true" if not guards else f"(and {' '.join(guards)})"
# #         z3_data_transform = "true" if not subst_history else f"(and {' '.join(subst_history)})"
# #         return z3_condition, z3_data_transform
# #     def dfs(current_place, current_path, visited, start_cut):
# #         if len(current_path) > 0 and current_place in cutpoint_set:
# #             if current_place != start_cut:
# #                 cond, subst = compute_condition_and_subst(current_path)
# #                 paths.append({
# #                     "from": start_cut,
# #                     "to": current_place,
# #                     "transitions": list(current_path),
# #                     "cond": cond,
# #                     "subst": subst
# #                 })
# #             return
# #         for t in out_transitions.get(current_place, []):
# #             for p2 in trans_to_places[t]:
# #                 if (p2, t) not in visited:
# #                     if p2 not in cutpoint_set or len(current_path) == 0:
# #                         visited.add((p2, t))
# #                         dfs(p2, current_path + [t], visited, start_cut)
# #                         visited.remove((p2, t))
# #     for cut in cutpoints:
# #         dfs(cut, [], set(), cut)
# #     return paths

# # def normalize_z3_expr(expr):
# #     import re
# #     expr = expr.replace(" ", "")
# #     expr = re.sub(r'\(and([^\)]*)\)', r'\1', expr)
# #     expr = expr.replace("true", "")
# #     return expr

# # def are_path_conditions_equivalent(cond1, cond2):
# #     return normalize_z3_expr(cond1) == normalize_z3_expr(cond2)

# # def are_data_transformations_identical(subst1, subst2):
# #     return normalize_z3_expr(subst1) == normalize_z3_expr(subst2)

# # def html_escape(s):
# #     import html
# #     return html.escape(str(s))

# # def check_pn_equivalence_html(sfc1, pn1, sfc2, pn2):
# #     cutpoints1 = find_cut_points(pn1)
# #     cutpoints2 = find_cut_points(pn2)
# #     paths1 = cutpoint_to_cutpoint_paths_with_conditions(sfc1, pn1, cutpoints1)
# #     paths2 = cutpoint_to_cutpoint_paths_with_conditions(sfc2, pn2, cutpoints2)
# #     unmatched1 = []
# #     matches1 = []
# #     for p1 in paths1:
# #         found = False
# #         for p2 in paths2:
# #             if are_path_conditions_equivalent(p1["cond"], p2["cond"]) \
# #                and are_data_transformations_identical(p1["subst"], p2["subst"]):
# #                 found = True
# #                 matches1.append((p1, p2))
# #                 break
# #         if not found:
# #             unmatched1.append(p1)
# #     unmatched2 = []
# #     matches2 = []
# #     for p2 in paths2:
# #         found = False
# #         for p1 in paths1:
# #             if are_path_conditions_equivalent(p1["cond"], p2["cond"]) \
# #                and are_data_transformations_identical(p1["subst"], p2["subst"]):
# #                 found = True
# #                 matches2.append((p2, p1))
# #                 break
# #         if not found:
# #             unmatched2.append(p2)
# #     equivalent = (not unmatched1) and (not unmatched2)
# #     html = ""
# #     html += "<html><head><title>Petri Net Model Equivalence Report</title>"
# #     html += """
# #     <style>
# #     body { font-family: Arial, sans-serif; }
# #     .equiv { color: green; font-weight: bold; }
# #     .notequiv { color: red; font-weight: bold; }
# #     table { border-collapse: collapse; margin-bottom: 2em; }
# #     th, td { border: 1px solid #aaa; padding: 5px 10px; }
# #     th { background: #e4edfa; }
# #     .section { margin-top: 2em; }
# #     .path-table th, .path-table td { font-size: 13px; }
# #     pre { margin: 0; }
# #     </style></head><body>
# #     """
# #     html += "<h1>Petri Net Model Equivalence Report</h1>"
# #     html += "<div class='section'><h2>Cut-Points</h2>"
# #     html += "<b>Model 1 Cut-Points:</b> " + ", ".join(html_escape(x) for x in cutpoints1) + "<br>"
# #     html += "<b>Model 2 Cut-Points:</b> " + ", ".join(html_escape(x) for x in cutpoints2) + "</div>"
# #     def path_table(paths, title):
# #         s = f"<div class='section'><h2>{title}</h2>"
# #         s += "<table class='path-table'><tr><th>From</th><th>To</th><th>Transitions</th><th>Z3 Condition</th><th>Z3 Data Transformation</th></tr>"
# #         for p in paths:
# #             s += "<tr>"
# #             s += "<td>%s</td><td>%s</td><td>%s</td><td><pre>%s</pre></td><td><pre>%s</pre></td>" % (
# #                 html_escape(p['from']), html_escape(p['to']), html_escape(p['transitions']),
# #                 html_escape(p['cond']), html_escape(p['subst'])
# #             )
# #             s += "</tr>"
# #         s += "</table></div>"
# #         return s
# #     html += path_table(paths1, "Model 1 Cut-Point Paths")
# #     html += path_table(paths2, "Model 2 Cut-Point Paths")
# #     html += "<div class='section'><h2>Path Matching (Model 1 to Model 2)</h2>"
# #     if matches1:
# #         html += "<table class='path-table'><tr><th>Model 1 Path</th><th>Model 2 Path</th><th>Condition</th><th>Data Transformation</th></tr>"
# #         for p1, p2 in matches1:
# #             html += "<tr>"
# #             html += f"<td>{html_escape(p1['from'])}&rarr;{html_escape(p1['to'])} ({html_escape(p1['transitions'])})</td>"
# #             html += f"<td>{html_escape(p2['from'])}&rarr;{html_escape(p2['to'])} ({html_escape(p2['transitions'])})</td>"
# #             html += f"<td><pre>{html_escape(p1['cond'])}</pre></td>"
# #             html += f"<td><pre>{html_escape(p1['subst'])}</pre></td>"
# #             html += "</tr>"
# #         html += "</table>"
# #     else:
# #         html += "<div>No matched paths found.</div>"
# #     html += "</div>"
# #     if unmatched1:
# #         html += "<div class='section'><h2>Paths in Model 1 with NO match in Model 2</h2>"
# #         html += path_table(unmatched1, "")
# #     if unmatched2:
# #         html += "<div class='section'><h2>Paths in Model 2 with NO match in Model 1</h2>"
# #         html += path_table(unmatched2, "")
# #     html += "<div class='section'><h2>Equivalence Result</h2>"
# #     if equivalent:
# #         html += "<span class='equiv'>The two PN models are EQUIVALENT (all path conditions and data transformations match).</span>"
# #     else:
# #         html += "<span class='notequiv'>The two PN models are NOT equivalent.</span>"
# #     html += "</div></body></html>"
# #     return html

# # if __name__ == "__main__":
# #     # SFC1
# #     steps1 = [
# #         {"name": "Start", "function": "x := 0"},
# #         {"name": "LoopEntry", "function": "x := x + 1"},
# #         {"name": "LoopBody", "function": "y := x * 2"},
# #         {"name": "Branch1", "function": "z := y + 5"},
# #         {"name": "Branch2", "function": "z := y - 3"}
# #     ]
# #     transitions1 = [
# #         {"src": "Start", "tgt": "LoopEntry", "guard": "init"},
# #         {"src": "LoopEntry", "tgt": "LoopBody", "guard": "True"},
# #         {"src": "LoopBody", "tgt": "LoopEntry", "guard": "x < 3"},
# #         {"src": "LoopBody", "tgt": "Branch1", "guard": "x >= 3 and x % 2 == 0"},
# #         {"src": "LoopBody", "tgt": "Branch2", "guard": "x >= 3 and x % 2 == 1"},
# #     ]
# #     sfc1 = SFC(steps=steps1, variables=["x", "y", "z"], transitions=transitions1, initial_step="Start")
# #     pn1 = sfc_to_petrinet(sfc1)

# #     # SFC2 (identical for demo; modify for non-equivalent models)
# #     steps2 = [
# #         {"name": "Start", "function": "x := 0"},
# #         {"name": "LoopEntry", "function": "x := x - 1"},
# #         {"name": "LoopBody", "function": "y := x * 2"},
# #         {"name": "Branch1", "function": "z := y + 5"},
# #         {"name": "Branch2", "function": "z := y - 3"}
# #     ]
# #     transitions2 = [
# #         {"src": "Start", "tgt": "LoopEntry", "guard": "init"},
# #         {"src": "LoopEntry", "tgt": "LoopBody", "guard": "True"},
# #         {"src": "LoopBody", "tgt": "LoopEntry", "guard": "x < 3"},
# #         {"src": "LoopBody", "tgt": "Branch1", "guard": "x >= 3 and x % 2 == 0"},
# #         {"src": "LoopBody", "tgt": "Branch2", "guard": "x >= 3 and x % 2 == 1"},
# #     ]
# #     sfc2 = SFC(steps=steps2, variables=["x", "y", "z"], transitions=transitions2, initial_step="Start")
# #     pn2 = sfc_to_petrinet(sfc2)

# #     html_report = check_pn_equivalence_html(sfc1, pn1, sfc2, pn2)
# #     with open("pn_equivalence_report.html", "w") as f:
# #         f.write(html_report)
# #     print("HTML report written to pn_equivalence_report.html")
