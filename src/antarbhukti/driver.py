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
from openpyxl import Workbook, load_workbook

def write_token_usage_to_excel(excel_path: str, sfc_name: str, token_dict: dict):
    """
    Append a row to Excel with SFC name and token usage.
    token_dict = {"GPT4o": 1234, "Gemini": 567, ...}
    """
    # Create workbook if not exists
    if not os.path.exists(excel_path):
        wb = Workbook()
        ws = wb.active
        # header row
        ws.append(["SFC Name"] + list(token_dict.keys()))
    else:
        wb = load_workbook(excel_path)
        ws = wb.active
    # append data row
    ws.append([sfc_name] + [token_dict.get(llm, 0) for llm in token_dict.keys()])
    wb.save(excel_path)

# src/antarbhukti/driver.py

def update_token_usage_excel(file_name: str, token_usages: dict):
    """
    Updates an Excel sheet with the token usage for each LLM.
    This version is more robust, checking headers and using flexible name matching.
    """
    excel_file = "llm_token_usage.xlsx"
    header = ["Name", "GPT4o", "Gemini", "LLaMA", "Claude", "Perplexity"]

    try:
        workbook = load_workbook(excel_file)
        sheet = workbook.active
        # Check if header is correct, if not, recreate it
        if sheet["A1"].value != header[0] or sheet["B1"].value != header[1]:
            sheet.delete_rows(1)
            sheet.insert_rows(1)
            sheet.append(header)
    except FileNotFoundError:
        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "Token Usage"
        sheet.append(header)

    # Find the row for the current file or create a new one
    file_row = -1
    for row_num, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):
        if row and row[0] == file_name:
            file_row = row_num
            break

    if file_row == -1:
        # Create a new row with the file name and zeros for all LLMs
        new_row_data = [file_name] + [0] * (len(header) - 1)
        sheet.append(new_row_data)
        file_row = sheet.max_row

    # Update the token counts using a more flexible 'in' check
    for llm_name, token_count in token_usages.items():
        llm_name_lower = llm_name.lower()
        if "gpt4o" in llm_name_lower:
            sheet.cell(row=file_row, column=2).value = token_count
        elif "gemini" in llm_name_lower:
            sheet.cell(row=file_row, column=3).value = token_count
        elif "llama" in llm_name_lower:
            sheet.cell(row=file_row, column=4).value = token_count
        elif "claude" in llm_name_lower:
            sheet.cell(row=file_row, column=5).value = token_count
        elif "perplexity" in llm_name_lower:
            sheet.cell(row=file_row, column=6).value = token_count 

    workbook.save(excel_file)
    print(f"Updated token usage in {excel_file}")

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

def refine_code(src, mod, llm:LLM_Mgr, prompt_template, dest_root):
    # Create verifier and report generator instances
    verifier = Verifier()
    # Load SFC models
    sfc1 = SFC()
    sfc2 = SFC()
    sfc1.load(src)
    sfc2.load(mod)
    #basename2 = os.path.splitext(os.path.basename(mod))[0]
    # Convert SFC models to Petri nets
    pn1 = sfc1.to_pn()
    total_token_usage = 0
    for iter_count in range(10):
        # Convert SFC models to Petri nets
        pn2 = sfc2.to_pn()
        # Perform containment analysis
        resp= verifier.check_pn_containment(sfc1, pn1, sfc2, pn2)
        if not resp:
            print(f"\n>>> Running {llm.name} to improve ...")
            llm_prompt = llm.generate_prompt(sfc1, sfc2, verifier.get_unmatched_paths(), prompt_template_path=prompt_template)
            if llm_prompt is None:  # No unmatched paths to improve
                print("No unmatched paths to improve on.")
                return (iter_count+1, False,total_token_usage)   
            # Call LLM to improve SFC2 if needed
            dest = gendestname(mod, dest_root+"/failed", iter_count)
            os.makedirs(dest_root+"/failed", exist_ok=True)
            improved,token_usage = llm.improve_code(llm_prompt, sfc2, dest)
            if token_usage:
                total_token_usage += token_usage

            if not improved:
                print("No further improvement possible or LLM failed.")
                return (iter_count+1, False,total_token_usage)      
            sfc2 = SFC()
            sfc2.load(dest)
        else:
            dest = gendestname(mod, dest_root+"/success", iter_count)
            os.makedirs(dest_root+"/success", exist_ok=True)
            sfc2.save(dest)
            return (iter_count+1, True,total_token_usage)
        
    print("No further improvement possible- max iteration reached.")
    return (iter_count+1, False,total_token_usage)   

def refine_all(args, llm):
    outdir = args.result_root + "/" + llm.name
    os.makedirs(outdir, exist_ok=True)
    
    if os.path.isfile(args.src_path):
        # This block runs for a single file.
        itr, iscontained, token_usage = refine_code(args.src_path, args.mod_path, llm, args.prompt_path, outdir)
        token_usages_dict = {llm.name: token_usage}
        print(f"No further improvement possible or LLM failed after {itr} iterations." if not iscontained else f"{args.mod_path} corrected after {itr} iterations and saved to {outdir}/success/{os.path.basename(args.mod_path)}")
        
        # Update Excel for the single file run inside the 'if' block.
        file_name = os.path.splitext(os.path.basename(args.src_path))[0]
        update_token_usage_excel(file_name, token_usages_dict)
    else:
        # This block runs for a directory.
        srcfiles = readfiles(args.src_path)
        modfiles = readfiles(args.mod_path)
        total_token_usages = {}
        for src, mod in zip(srcfiles, modfiles):
            # Correctly unpack all three return values from refine_code
            itr, iscontained, token_usage = refine_code(src, mod, llm, args.prompt_path, outdir)
            # Add the token usage from this run to the total for the current LLM
            total_token_usages[llm.name] = total_token_usages.get(llm.name, 0) + token_usage
            print(f"No further improvement possible or LLM failed after {itr} iterations." if not iscontained else f"{mod} corrected after {itr} iterations and saved to {outdir}/success/{os.path.basename(mod)}")
        
        # Update Excel for the entire directory run inside the 'else' block.
        file_name = os.path.basename(args.src_path)
        update_token_usage_excel(file_name, total_token_usages)

def run_all_llms(args):
    llm_names = [name.strip().lower() for name in args.llms.split(",") if name.strip()]
    llms_config = read_config_file(args.config_path)
    llms= instantiate_llms(llm_names, llms_config )
    for llm in llms:
        refine_all(args, llm)

def main():
    args = parse_args()
#    checkcontainment("./src/dec2hex.txt", "./dec2hex_mod_wrong_3.txt")
    run_all_llms(args)

if __name__ == "__main__":
    main()
