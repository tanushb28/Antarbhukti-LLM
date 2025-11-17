#!/usr/bin/env python3
"""
Driver script for Petri Net containment checking.
This script demonstrates how to use the Verifier and GenReport classes
to perform containment analysis and generate reports.
"""

import sys
from sfc import SFC
from sfc_verifier import Verifier
from genreport import GenReport
from codegenutil import gendestname, savefile, readfiles, read_config_file, parse_args
from llm_mgr import LLM_Mgr
from llm_codegen import instantiate_llms
import shutil
import os
import time
from openpyxl import Workbook, load_workbook
from genreport import create_newbenchmark_csv_if_missing

create_newbenchmark_csv_if_missing("NewBenchmark - Sheet1.csv")

# def update_token_usage_excel(file_name: str, token_usages: dict):
#     """
#     Updates a CSV file with the token usage for each LLM.
#     This method is robust against file corruption and race conditions.
#     """
#     csv_file = "llm_token_usage.csv"
#     header = ["Name", "GPT4o", "Gemini", "LLaMA", "Claude", "Perplexity"]
    
#     # Read the existing data from the CSV
#     data = []
#     if os.path.exists(csv_file):
#         with open(csv_file, mode='r', newline='', encoding='utf-8') as infile:
#             reader = csv.DictReader(infile)
#             # Ensure the header is what we expect, even if the file is empty
#             if set(header) != set(reader.fieldnames or []):
#                  # If headers are bad, we'll overwrite with good data
#                  pass
#             else:
#                 for row in reader:
#                     data.append(row)

#     # Find the entry for the current file or create it
#     file_entry = None
#     for row in data:
#         # Use .strip() for robust matching
#         if row.get("Name", "").strip() == file_name.strip():
#             file_entry = row
#             break
            
#     if file_entry is None:
#         # If the file name was not found, create a new entry
#         file_entry = {key: "0" for key in header} # Initialize all values as strings
#         file_entry["Name"] = file_name
#         data.append(file_entry)

#     # Update the token count for the specific LLM
#     for llm_name, token_count in token_usages.items():
#         # Find the header key that matches the LLM name
#         for key in header:
#             if llm_name.lower() in key.lower():
#                 # Get the current count, add the new count, and update
#                 current_count = int(file_entry.get(key, 0))
#                 file_entry[key] = str(current_count + token_count)
#                 break

#     # Write the entire updated dataset back to the CSV file
#     try:
#         with open(csv_file, mode='w', newline='', encoding='utf-8') as outfile:
#             writer = csv.DictWriter(outfile, fieldnames=header)
#             writer.writeheader()
#             writer.writerows(data)
#         print(f"Updated token usage in {csv_file}")
#     except IOError as e:
#         print(f"Error writing to {csv_file}: {e}")


def check_pn_containment_html(verifier, gen_report, sfc1, pn1, sfc2, pn2):
    gen_report.sfc_to_dot(sfc1, "sfc1.dot")
    gen_report.dot_to_png("sfc1.dot", "sfc1.png")
    gen_report.petrinet_to_dot(pn1, "pn1.dot")
    gen_report.dot_to_png("pn1.dot", "pn1.png")
    gen_report.sfc_to_dot(sfc2, "sfc2.dot")
    gen_report.dot_to_png("sfc2.dot", "sfc2.png")
    gen_report.petrinet_to_dot(pn2, "pn2.dot")
    gen_report.dot_to_png("pn2.dot", "pn2.png")

    # Prepare image paths for report
    img_paths = {
        "sfc1": gen_report.img_to_base64("sfc1.png"),
        "pn1": gen_report.img_to_base64("pn1.png"),
        "sfc2": gen_report.img_to_base64("sfc2.png"),
        "pn2": gen_report.img_to_base64("pn2.png")
    }
    
    # Use GenReport instance to generate HTML report
    return gen_report.generate_containment_html_report(
        verifier.cutpoints1, verifier.cutpoints2, verifier.paths1, verifier.paths2, 
        verifier.matches1, verifier.unmatched1, verifier.contained, img_paths
    )


def checkcontainment(src1,src2, dest_root="output"):
    # Create verifier and report generator instances
    verifier = Verifier()
    gen_report = GenReport()
    destsfc2=""
    report_file=""
    # Load SFC models
    sfc1 = SFC()
    sfc2 = SFC()
    sfc1.load(src1)
    sfc2.load(src2)
    basename2 = os.path.splitext(os.path.basename(src2))[0]
    # Convert SFC models to Petri nets
    pn1 = sfc1.to_pn()
    pn2 = sfc2.to_pn()
    
    # Perform containment analysis
    resp= verifier.check_pn_containment(sfc1, pn1, sfc2, pn2)
    jsonreport = gen_report.generate_containment_json_report(
        verifier.cutpoints1, verifier.cutpoints2, verifier.paths1, verifier.paths2, 
        verifier.matches1, verifier.unmatched1, verifier.contained )
    
    if not resp:
    # Write report to file
        destsfc2 = gendestname(src2, dest_root+"/failed")
        os.makedirs(dest_root+"/failed", exist_ok=True)
        report_file = gendestname(basename2+".json", dest_root+"/failed")
    else:
        destsfc2 = gendestname(src2, dest_root+"/success")
        os.makedirs(dest_root+"/success", exist_ok=True)
        report_file = gendestname(basename2+".json", dest_root+"/success")    
    savefile(report_file, jsonreport)
    shutil.move(src2, destsfc2)
    return resp

def refine_code(src, mod, llm: LLM_Mgr, prompt_template, dest_root):
    import time
    verifier = Verifier()
    sfc1 = SFC()
    sfc2 = SFC()
    try:
        sfc1.load(src)
        sfc2.load(mod)
    except Exception as e:
        return {"status": "error", "message": f"SFC loading failed: {e}", "token_usage": 0, "count": 0, "llm_time": 0}

    pn1 = sfc1.to_pn()
    total_token_usage = 0
    max_iterations = 10
    llm_time_taken = 0  # Track total LLM time

    for iter_count in range(max_iterations):
        pn2 = sfc2.to_pn()
        resp = verifier.check_pn_containment(sfc1, pn1, sfc2, pn2)

        if resp:
            dest = gendestname(mod, dest_root + "/success", iter_count)
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            sfc2.save(dest)
            print(f"Time taken by {llm.name}: {llm_time_taken:.2f} seconds")
            return {"status": "success", "count": iter_count + 1, "token_usage": total_token_usage, "llm_time": llm_time_taken}

        print(f"\n>>> Running {llm.name} to improve ...")
        start_time = time.time()
        llm_prompt = llm.generate_prompt(sfc1, sfc2, verifier.get_unmatched_paths(), prompt_template_path=prompt_template)
        llm_time_taken += time.time() - start_time  # Add prompt generation time

        if llm_prompt is None:
            msg = "Containment failed but no unmatched paths found."
            print(msg)
            print(f"Time taken by {llm.name}: {llm_time_taken:.2f} seconds")
            return {"status": "error", "message": msg, "token_usage": total_token_usage, "count": iter_count + 1, "llm_time": llm_time_taken}

        dest = gendestname(mod, dest_root + "/failed", iter_count)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        start_time = time.time()
        improved_status = llm.improve_code(llm_prompt, sfc2, dest)
        llm_time_taken += time.time() - start_time  # Add LLM call time

        token_usage = improved_status.get("token_usage", 0)
        if token_usage:
            total_token_usage += token_usage

        if not improved_status.get("improved"):
            msg = improved_status.get("error", "LLM failed to improve code.")
            print(msg)
            print(f"Time taken by {llm.name}: {llm_time_taken:.2f} seconds")
            return {"status": "error", "message": msg, "token_usage": total_token_usage, "count": iter_count + 1, "llm_time": llm_time_taken}

        sfc2 = SFC()
        try:
            sfc2.load(dest)
        except ValueError as e:
            msg = f"Failed to load improved SFC from {dest}: {e}"
            print(msg)
            print(f"Time taken by {llm.name}: {llm_time_taken:.2f} seconds")
            return {"status": "error", "message": msg, "token_usage": total_token_usage, "count": iter_count + 1, "llm_time": llm_time_taken}

    print("Max iterations reached.")
    print(f"Time taken by {llm.name}: {llm_time_taken:.2f} seconds")
    return {"status": "timeout", "count": max_iterations, "token_usage": total_token_usage, "llm_time": llm_time_taken}

def run_all_llms(args):
    llm_names = [name.strip().lower() for name in args.llms.split(",") if name.strip()]
    llms_config = read_config_file(args.config_path)
    llms = instantiate_llms(llm_names, llms_config)
    reporter = GenReport()

    if os.path.isdir(args.src_path):
        src_files = readfiles(args.src_path)
        mod_files = readfiles(args.mod_path)

        for src, mod in zip(src_files, mod_files):
            file_name = os.path.splitext(os.path.basename(src))[0]
            path_parts = src.split(os.sep)
            test_type = "unknown"
            if "new_benchmarks" in path_parts:
                try:
                    test_type_index = path_parts.index("new_benchmarks") + 1
                    if test_type_index < len(path_parts):
                        test_type = path_parts[test_type_index]
                except (ValueError, IndexError):
                    pass

            all_results = {}
            for llm in llms:
                outdir = args.result_root + "/" + llm.name
                os.makedirs(outdir, exist_ok=True)
                result = refine_code(src, mod, llm, args.prompt_path, outdir)
                all_results[llm.name] = result
                
                if result.get("status") == "success":
                    print(f"{mod} corrected by {llm.name} after {result.get('count')} iterations and saved to {outdir}/success/{os.path.basename(mod)}")
                else:
                    print(f"For {mod}, {llm.name} failed after {result.get('count', 1)} iterations.")
            
            reporter.generate_csv(file_name, test_type, all_results)

    else: # Single file mode
        file_name = os.path.splitext(os.path.basename(args.src_path))[0]
        path_parts = args.src_path.split(os.sep)
        test_type = "unknown"
        if "new_benchmarks" in path_parts:
            try:
                test_type_index = path_parts.index("new_benchmarks") + 1
                if test_type_index < len(path_parts):
                    test_type = path_parts[test_type_index]
            except (ValueError, IndexError):
                pass

        all_results = {}
        for llm in llms:
            outdir = args.result_root + "/" + llm.name
            os.makedirs(outdir, exist_ok=True)
            result = refine_code(args.src_path, args.mod_path, llm, args.prompt_path, outdir)
            all_results[llm.name] = result

            if result.get("status") == "success":
                print(f"{args.mod_path} corrected by {llm.name} after {result.get('count')} iterations and saved to {outdir}/success/{os.path.basename(args.mod_path)}")
            else:
                print(f"For {args.mod_path}, {llm.name} failed after {result.get('count', 1)} iterations.")

        reporter.generate_csv(file_name, test_type, all_results)

def main():
    args = parse_args()
#    checkcontainment("./src/dec2hex.txt", "./dec2hex_mod_wrong_3.txt")
    run_all_llms(args)

if __name__ == "__main__":
    main()
