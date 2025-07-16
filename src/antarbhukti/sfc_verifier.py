import subprocess
import base64
import os
import z3
import re
import ast
from sfc import SFC

class Verifier:
    """Petri Net Model Containment Verifier"""
    
    def __init__(self):
        self.cutpoints1 = []
        self.cutpoints2 = []
        self.paths1 = []
        self.paths2 = []
        self.matches1 = []
        self.unmatched1 = []
        self.contained = False
    
    def infix_to_sexpr(self, expr):
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



    def find_cut_points(self, pn):
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

    def cutpoint_to_cutpoint_paths_with_conditions(self, sfc, pn, cutpoints, allowed_variables=None):
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
            return self.infix_to_sexpr(g)
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
                            subst_history.append(f"(= {lhs} {self.infix_to_sexpr(rhs)})")
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

    def z3_vars(self, variable_names):
        return {v: z3.Int(v) for v in variable_names}

    def preprocess_condition_for_equivalence(self, expr):
        expr = expr.strip()
        # Treat 'init' as 'true' for equivalence checking
        if expr == "init":
            return "true"
        return expr

    def parse_z3_expr(self, expr, variables):
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

    def are_path_conditions_equivalent(self, cond1, cond2, variables):
        # Preprocess the conditions to treat 'init' as 'true'
        cond1 = self.preprocess_condition_for_equivalence(cond1)
        cond2 = self.preprocess_condition_for_equivalence(cond2)
        z3_vars_dict = self.z3_vars(variables)
        e1 = self.parse_z3_expr(cond1, z3_vars_dict)
        e2 = self.parse_z3_expr(cond2, z3_vars_dict)
        if e1 is None or e2 is None:
            return False
        if not (z3.is_expr(e1) and z3.is_expr(e2)):
            return False
        s = z3.Solver()
        s.add(e1 != e2)
        return s.check() == z3.unsat

    def parse_z3_assignments(self, expr):
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

    def are_data_transformations_equivalent(self, subst1, subst2, allowed_vars):
        d1 = self.parse_z3_assignments(subst1)
        d2 = self.parse_z3_assignments(subst2)
        for v in allowed_vars:
            v1 = d1.get(v, None)
            v2 = d2.get(v, None)
            if v1 != v2:
                return False
        return True

    def check_pn_containment(self, sfc1, pn1, sfc2, pn2):
        """Perform containment analysis and store results as instance attributes"""
        self.cutpoints1 = self.find_cut_points(pn1)
        self.cutpoints2 = self.find_cut_points(pn2)
        common_vars = list(sorted(set(sfc1.variables) & set(sfc2.variables)))
        self.paths1 = self.cutpoint_to_cutpoint_paths_with_conditions(sfc1, pn1, self.cutpoints1, allowed_variables=common_vars)
        self.paths2 = self.cutpoint_to_cutpoint_paths_with_conditions(sfc2, pn2, self.cutpoints2, allowed_variables=common_vars)
        self.unmatched1 = []
        self.matches1 = []
        for p1 in self.paths1:
            found = False
            for p2 in self.paths2:
                if self.are_path_conditions_equivalent(p1["cond"], p2["cond"], common_vars) \
                   and self.are_data_transformations_equivalent(p1["subst"], p2["subst"], common_vars):
                    found = True
                    self.matches1.append((p1, p2))
                    break
            if not found:
                self.unmatched1.append(p1)
        self.contained = not self.unmatched1
        return self.contained

    def get_analysis_results(self):
        """Get all analysis results as a dictionary"""
        return {
            'cutpoints1': self.cutpoints1,
            'cutpoints2': self.cutpoints2,
            'paths1': self.paths1,
            'paths2': self.paths2,
            'matches1': self.matches1,
            'unmatched1': self.unmatched1,
            'contained': self.contained
        }

    def is_contained(self):
        """Check if model 1 is contained in model 2"""
        return self.contained

    def get_unmatched_paths(self):
        """Get paths from model 1 that have no equivalent in model 2"""
        return self.unmatched1

    def get_matched_paths(self):
        """Get matched path pairs between model 1 and model 2"""
        return self.matches1

if __name__ == "__main__":
    ########################### Example Usage #####################################
    # Main execution code has been moved to driver.py
    # Run driver.py for a complete example of using Verifier and GenReport classes
    print("This module provides Verifier class for Petri Net containment analysis.")
    print("Run driver.py for a complete example of usage.")
