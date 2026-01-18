import subprocess
import base64
import os
import json
import csv
import pandas as pd

def create_newbenchmark_csv_if_missing(csv_file):
    if not os.path.exists(csv_file):
        # Define the multi-level columns
        columns = [
            "Benchmark Name", "Type",
            "GPT4o_iter", "Gemini_iter", "LLaMA_iter", "Claude_iter", "Perplexity_iter",
            "GPT4o_tokens", "Gemini_tokens", "LLaMA_tokens", "Claude_tokens", "Perplexity_tokens",
            "GPT4o_time", "Gemini_time", "LLaMA_time", "Claude_time", "Perplexity_time"
        ]
        df = pd.DataFrame(columns=columns)
        df.to_csv(csv_file, index=False)
        # print("[DEBUG] Created CSV at:", os.path.abspath(csv_file))
        # print("[DEBUG] Files in directory after creation:", os.listdir(os.path.dirname(os.path.abspath(csv_file))))
        print(f"Created new blank {csv_file}")


def get_llm_names_from_config(config_path="config.json"):
    with open(config_path, "r") as f:
        config = json.load(f)
    llm_names = []
    for entry in config:
        if isinstance(entry, dict) and "llm_name" in entry:
            llm_names.append(entry["llm_name"].lower())
    return llm_names

class GenReport:
    """Report generation and utility functions for Petri Net analysis"""
    
    def __init__(self, csv_file_path):
        self.csv_file_path = csv_file_path
        #print("[DEBUG] GenReport initialized with CSV path:", os.path.abspath(self.csv_file_path))
    
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
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background-color: #0E1117; 
            color: #FAFAFA; 
            margin: 20px;
        }
        h1, h2 { color: #4DB6AC; border-bottom: 1px solid #333; padding-bottom: 10px; }
        .contained { color: #00E676; font-weight: bold; padding: 10px; border: 1px solid #00E676; border-radius: 5px; display: inline-block; }
        .notcontained { color: #FF5252; font-weight: bold; padding: 10px; border: 1px solid #FF5252; border-radius: 5px; display: inline-block; }
        
        /* Table Styling */
        table { border-collapse: collapse; width: 100%; margin-bottom: 2em; background-color: #161B22; }
        th, td { border: 1px solid #30363D; padding: 12px 15px; text-align: left; }
        th { background-color: #21262D; color: #58A6FF; font-weight: 600; }
        tr:nth-child(even) { background-color: #0D1117; }
        
        .section { margin-top: 3em; background: #161B22; padding: 20px; border-radius: 8px; border: 1px solid #30363D; }
        pre { margin: 0; white-space: pre-wrap; word-wrap: break-word; color: #A5D6FF; font-family: 'Consolas', 'Courier New', monospace; }
        
        /* Diagram Grid - Full Width & Vertical Stacking */
        .diagram-container {
            display: flex;
            flex-direction: column;
            gap: 40px;
            align-items: center;
            width: 100%;
        }
        .diagram-box {
            background-color: #ffffff; /* White background strictly for images so black text is visible */
            padding: 15px;
            border-radius: 8px;
            text-align: center;
            width: 90%;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
        }
        .diagram-box b { color: #333; font-size: 1.2rem; display: block; margin-bottom: 10px; }
        .imgblock { max-width: 100%; height: auto; border: 1px solid #ddd; }
        </style></head><body>
        """
        html += "<h1>⚡ Petri Net Model Containment Report</h1>"
        
        # Modified Diagram Layout: Vertical Stacking with White Backgrounds
        html += "<div class='section'><h2>Model Diagrams</h2><div class='diagram-container'>"
        for key, label in [
            ("sfc1", "Original SFC (Source)"), ("pn1", "Original Petri Net"), 
            ("sfc2", "Modified SFC (Target)"), ("pn2", "Modified Petri Net")
        ]:
            b64 = img_paths.get(key, None)
            html += f"<div class='diagram-box'><b>{label}</b>"
            if b64:
                html += f"<img class='imgblock' src='data:image/png;base64,{b64}'/>"
            else:
                html += "<span style='color:red'>Image not found</span>"
            html += "</div>"
        html += "</div></div>"

        html += "<div class='section'><h2>Cut-Points</h2>"
        html += "<p><b>Model 1 Cut-Points:</b> " + ", ".join(self.html_escape(x) for x in cutpoints1) + "</p>"
        html += "<p><b>Model 2 Cut-Points:</b> " + ", ".join(self.html_escape(x) for x in cutpoints2) + "</p></div>"
        
        def path_table(paths, title):
            s = f"<div class='section'><h2>{title}</h2>"
            if not paths:
                s += "<p><i>No paths found.</i></p></div>"
                return s
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
                html += f"<td>{self.html_escape(p1['from'])}&rarr;{self.html_escape(p1['to'])} <br><small>({self.html_escape(p1['transitions'])})</small></td>"
                html += f"<td>{self.html_escape(p2['from'])}&rarr;{self.html_escape(p2['to'])} <br><small>({self.html_escape(p2['transitions'])})</small></td>"
                html += f"<td><pre>{self.html_escape(p1['cond'])}</pre></td>"
                html += f"<td><pre>{self.html_escape(p1['subst'])}</pre></td>"
                html += "</tr>"
            html += "</table>"
        else:
            html += "<div>No matched paths found.</div>"
        html += "</div>"
        
        if unmatched1:
            html += "<div class='section' style='border-color: #FF5252;'><h2>⚠️ Paths in Model 1 with NO equivalent path in Model 2</h2>"
            html += path_table(unmatched1, "")
            
        html += "<div class='section'><h2>Containment Result</h2>"
        if contained:
            html += "<span class='contained'>All paths of Model 1 are equivalent to some path of Model 2 (Model 1 is contained in Model 2).</span>"
        else:
            html += "<span class='notcontained'>There are paths in Model 1 that are not matched in Model 2 (Containment does NOT hold).</span>"
        html += "</div></body></html>"
        return html

    
    def generate_csv(self, file_name: str, test_type: str, all_results: dict):
        csv_file = self.csv_file_path
        #fix
        base_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(base_dir, "config.json")

        try:
            #print("Attempting to read CSV from:", os.path.abspath(csv_file))
            df = pd.read_csv(csv_file)  

            row_index = df[(df["Benchmark Name"] == file_name) & (df["Type"] == test_type)].index

            # Dynamically get LLM names from config
            #config_path = "config.json" #dont need this line (its overrwriting my set path.)
            llm_names = get_llm_names_from_config(config_path)

            # Build column maps dynamically
            # Map lowercase config names to your specific CSV header format
            def format_header_name(name):
                name_lower = name.lower()
                if name_lower == "gpt4o":
                    return "GPT4o"
                elif name_lower == "llama":
                    return "LLaMA"
                else:
                    # Default behavior for Gemini, Claude, Perplexity (e.g., "gemini" -> "Gemini")
                    return name.capitalize()

            # Build column maps using the formatter
            token_column_map = {llm: f"{format_header_name(llm)}_tokens" for llm in llm_names}
            iteration_column_map = {llm: f"{format_header_name(llm)}_iter" for llm in llm_names}
            time_column_map = {llm: f"{format_header_name(llm)}_time" for llm in llm_names}


            if not row_index.empty:
                idx = row_index[0]
            else:
                # Create a new row with all columns empty
                new_row = pd.Series({col: "" for col in df.columns}, name=len(df))
                new_row["Benchmark Name"] = file_name
                new_row["Type"] = test_type
                df = pd.concat([df, new_row.to_frame().T], ignore_index=True)
                idx = df.index[-1]

            for llm_name, result in all_results.items():
                token_usage = result.get("token_usage", 0)
                iteration_info = result
                time_taken = result.get("llm_time", "")

                # Update token usage
                token_col = token_column_map.get(llm_name.lower())
                if token_col and token_col in df.columns:
                    df.loc[idx, token_col] = token_usage

                # Update iteration info
                iteration_col = iteration_column_map.get(llm_name.lower())
                if iteration_col and iteration_col in df.columns:
                    status = iteration_info.get("status")
                    if status == "success":
                        df.loc[idx, iteration_col] = iteration_info.get("count", 0)
                    elif status == "timeout":
                        df[iteration_col] = df[iteration_col].astype(object)
                        df.loc[idx, iteration_col] = "Timeout"
                    elif status == "error":
                        df[iteration_col] = df[iteration_col].astype(object)
                        error_msg = iteration_info.get("message", "Unknown Error")
                        df.loc[idx, iteration_col] = f"ERROR: {error_msg[:100]}"

                # Update time taken
                time_col = time_column_map.get(llm_name.lower())
                if time_col and time_col in df.columns:
                    if isinstance(time_taken, (float, int)):
                        df.loc[idx, time_col] = round(time_taken, 2)
                    else:
                        df.loc[idx, time_col] = time_taken

            df.to_csv(csv_file, index=False)
            print(f"Updated CSV for {file_name} ({test_type})")

        except FileNotFoundError as e:
            print(f"Error: A required file was not found. Details: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")