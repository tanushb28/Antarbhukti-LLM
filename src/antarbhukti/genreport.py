import subprocess
import base64
import os
import json

class GenReport:
    """Report generation and utility functions for Petri Net analysis"""
    
    def __init__(self):
        pass
    
    def sfc_to_dot(self, sfc, dot_filename="sfc.dot"):
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

    def petrinet_to_dot(self, pn, dot_filename="pn.dot"):
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

    def dot_to_png(self, dot_filename, png_filename):
        try:
            subprocess.run(
                ["dot", "-Tpng", dot_filename, "-o", png_filename],
                check=True
            )
            print(f"{png_filename} generated.")
        except Exception as e:
            print(f"Error running Graphviz: {e}")

    def html_escape(self, s):
        import html
        return html.escape(str(s))

    def img_to_base64(self, path):
        if not os.path.exists(path):
            return None
        with open(path, "rb") as f:
            data = f.read()
            return base64.b64encode(data).decode("ascii")

    def generate_containment_json_report(self, cutpoints1, cutpoints2, paths1, paths2, matches1, unmatched1, contained):
        """Generate JSON report for Petri Net model containment analysis."""
        # Build the JSON report structure
        report = {
            "title": "Petri Net Model Containment Report",
            "cut_points": {
                "model1": cutpoints1,
                "model2": cutpoints2
            },
            "paths": {
                "model1": [
                    {
                        "from": p["from"],
                        "to": p["to"],
                        "transitions": p["transitions"],
                        "condition": p["cond"],
                        "data_transformation": p["subst"]
                    } for p in paths1
                ],
                "model2": [
                    {
                        "from": p["from"],
                        "to": p["to"],
                        "transitions": p["transitions"],
                        "condition": p["cond"],
                        "data_transformation": p["subst"]
                    } for p in paths2
                ]
            },
            "path_mapping": {
                "matched_paths": [
                    {
                        "model1_path": {
                            "from": p1["from"],
                            "to": p1["to"],
                            "transitions": p1["transitions"],
                            "condition": p1["cond"],
                            "data_transformation": p1["subst"]
                        },
                        "model2_path": {
                            "from": p2["from"],
                            "to": p2["to"],
                            "transitions": p2["transitions"],
                            "condition": p2["cond"],
                            "data_transformation": p2["subst"]
                        }
                    } for p1, p2 in matches1
                ],
                "unmatched_paths": [
                    {
                        "from": p["from"],
                        "to": p["to"],
                        "transitions": p["transitions"],
                        "condition": p["cond"],
                        "data_transformation": p["subst"]
                    } for p in unmatched1
                ]
            },
            "containment_result": {
                "contained": contained,
                "description": "All paths of Model 1 are equivalent to some path of Model 2 (Model 1 is contained in Model 2)." if contained else "There are paths in Model 1 that are not matched in Model 2 (Containment does NOT hold).",
                "unmatched_path_count": len(unmatched1),
                "matched_paths_count": len(matches1)
            }
        }
        
        return json.dumps(report, indent=2)

    def generate_containment_html_report(self, cutpoints1, cutpoints2, paths1, paths2, matches1, unmatched1, contained, img_paths):
        """Generate HTML report for Petri Net model containment analysis."""
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
        html += "<b>Model 1 Cut-Points:</b> " + ", ".join(self.html_escape(x) for x in cutpoints1) + "<br>"
        html += "<b>Model 2 Cut-Points:</b> " + ", ".join(self.html_escape(x) for x in cutpoints2) + "</div>"
        def path_table(paths, title):
            s = f"<div class='section'><h2>{title}</h2>"
            s += "<table class='path-table'><tr><th>From</th><th>To</th><th>Transitions</th><th>Condition</th><th>Data Transformation</th></tr>"
            for p in paths:
                s += "<tr>"
                s += "<td>%s</td><td>%s</td><td>%s</td><td><pre>%s</pre></td><td><pre>%s</pre></td>" % (
                    self.html_escape(p['from']), self.html_escape(p['to']), self.html_escape(p['transitions']),
                    self.html_escape(p['cond']), self.html_escape(p['subst'])
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
                html += f"<td>{self.html_escape(p1['from'])}&rarr;{self.html_escape(p1['to'])} ({self.html_escape(p1['transitions'])})</td>"
                html += f"<td>{self.html_escape(p2['from'])}&rarr;{self.html_escape(p2['to'])} ({self.html_escape(p2['transitions'])})</td>"
                html += f"<td><pre>{self.html_escape(p1['cond'])}</pre></td>"
                html += f"<td><pre>{self.html_escape(p1['subst'])}</pre></td>"
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
