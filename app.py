#!/usr/bin/env python3
"""
Antarbhukti — Streamlit UI (clean, no debug mode)

- Runs src/antarbhukti/driver.py with unbuffered Python (-u).
- Captures stdout/stderr and displays them.
- Extracts corrected SFC text when present (fenced blocks, indented blocks,
  or SFC-structured sections like `steps = [...]`, `transitions = [...]`,
  `variables = [...]`, `initial_step = ...`).
- Probes common outputs/**/success/** locations for a saved file matching the
  uploaded NEW filename and displays its contents if found.

This is a clean production-style UI without verbose debug output.
"""

import streamlit as st
import os
import subprocess
import datetime
import shutil
import re
import glob
import time
import unicodedata
import json

# ---------------------------
# Config loader
# ---------------------------
def load_config():
    app_dir = os.path.dirname(os.path.abspath(__file__))
    cfg_path = os.path.join(app_dir, "src", "antarbhukti", "config.json")
    if not os.path.exists(cfg_path):
        st.error(f"Config file missing: {cfg_path}")
        st.stop()
    with open(cfg_path, "r", encoding="utf-8") as f:
        return json.load(f)

# ---------------------------
# Page settings
# ---------------------------
st.set_page_config(page_title="Antarbhukti — LLM Verification", page_icon="🧠", layout="wide")
st.markdown("""
<style>
.title { font-size: 26px; font-weight: 700; color: #2E86C1; }
.log-box { background-color: #fafafa; color: #111; padding: 10px; border-radius: 6px;
           height: 360px; overflow-y: auto; font-family: monospace; font-size: 13px; border: 1px solid #ddd; }
</style>
""", unsafe_allow_html=True)
st.markdown('<div class="title">🧠 Antarbhukti — LLM-Driven PLC Upgrade Verification</div>', unsafe_allow_html=True)
st.write("Upload OLD and NEW SFC files, run verification, and view corrected outputs.")

# ---------------------------
# Load config and LLM selection
# ---------------------------
config_list = load_config()
llm_names = [c.get("llm_name", "unknown") for c in config_list] if config_list else ["gpt4o"]

st.sidebar.title("Settings")
selected_llm = st.sidebar.selectbox("Choose LLM (single-run)", llm_names)
run_mode = st.sidebar.radio("Run mode", ("Single LLM (fast)", "All LLMs (slow)"))

# ---------------------------
# Tabs and upload
# ---------------------------
tab1, tab2, tab3, tab4 = st.tabs(["Upload", "Run", "Output", "About"])

with tab1:
    st.header("Upload SFC Files")
    st.write("Upload the OLD and NEW SFC program files (text).")
    old_file = st.file_uploader("OLD PLC Program", type=["txt", "st"])
    new_file = st.file_uploader("NEW PLC Program", type=["txt", "st"])
    if old_file and new_file:
        st.success("Files uploaded. Switch to Run tab.")

# ---------------------------
# Logging helper (minimal)
# ---------------------------
def add_log_text(logs, msg, panel):
    logs += f"[{datetime.datetime.now().isoformat()}] {msg}\n"
    panel.text_area("Logs", logs, height=360)
    return logs

# ---------------------------
# Text sanitizer
# ---------------------------
def sanitize_text(s: str) -> str:
    if s is None:
        return ""
    s = unicodedata.normalize("NFKC", s)
    s = s.replace("→", "->").replace("←", "<-").replace("⇒", "=>").replace("⇐", "<=")
    return "".join(ch for ch in s if ch == "\n" or ch == "\t" or (31 < ord(ch) < 0x10FFFF))

# ---------------------------
# Extractor (clean)
# ---------------------------
def extract_blocks(full_output: str):
    out = sanitize_text(full_output or "")
    blocks = []

    # fenced blocks
    fenced = re.findall(r"```(?:\w*\n)?([\s\S]*?)```", out)
    blocks.extend([b.strip() for b in fenced if b.strip()])

    # indented 4-space blocks
    for m in re.finditer(r"(?:^|\n)((?: {4}.+(?:\n|$))+)", out):
        block = m.group(1)
        cleaned = "\n".join([ln[4:] if ln.startswith("    ") else ln for ln in block.splitlines()])
        if cleaned.strip():
            blocks.append(cleaned.strip())

    # SFC-structured blocks: steps/transitions/variables/initial_step
    sfc_parts = []
    steps_match = re.search(r"(steps\s*=\s*\[([\s\S]*?)\])", out, flags=re.IGNORECASE)
    if steps_match:
        sfc_parts.append(steps_match.group(1).strip())
        transitions_match = re.search(r"(transitions\s*=\s*\[([\s\S]*?)\])", out, flags=re.IGNORECASE)
        if transitions_match:
            sfc_parts.append(transitions_match.group(1).strip())
        variables_match = re.search(r"(variables\s*=\s*\[([\s\S]*?)\])", out, flags=re.IGNORECASE)
        if variables_match:
            sfc_parts.append(variables_match.group(1).strip())
        init_match = re.search(r"(initial_step\s*=\s*['\"].+?['\"])", out, flags=re.IGNORECASE)
        if init_match:
            sfc_parts.append(init_match.group(1).strip())

    if sfc_parts:
        combined = "\n\n".join(sfc_parts)
        blocks.insert(0, combined)

    # PLC heuristic (fallback)
    plc_keywords = ["STEP", "STATE", "TRANSITION", "IF", "THEN", "ELSE", ":=", "="]
    plc_lines = [ln for ln in out.splitlines() if any(k in ln for k in plc_keywords)]
    if len(plc_lines) >= 3 and not blocks:
        blocks.append("\n".join(plc_lines))

    return blocks

# ---------------------------
# Filesystem probe for saved file
# ---------------------------
def find_saved_file_by_basename(basename, repo_root, min_mtime=0.0):
    # search common result dirs
    patterns = [
        os.path.join(repo_root, "outputs", "**", "success", "**", basename),
        os.path.join(repo_root, "output", "**", "success", "**", basename),
        os.path.join(repo_root, "**", basename),
        os.path.join("/mnt", "c", "**", basename),
        os.path.join("/mnt", "c", "**", "OneDrive*", "**", basename),
    ]
    for pat in patterns:
        for match in glob.glob(pat, recursive=True):
            try:
                if os.path.isfile(match) and os.path.getmtime(match) + 1e-6 >= min_mtime:
                    return os.path.abspath(match)
            except Exception:
                continue
    return None

# ---------------------------
# Run tab: execute driver
# ---------------------------
with tab2:
    st.header("Run Verification")
    run_button = st.button("Start Verification")
    status_panel = st.empty()
    log_panel = st.empty()
    logs = ""

    if run_button:
        if old_file is None or new_file is None:
            st.error("Please upload both OLD and NEW files before running.")
        else:
            # save uploads
            shutil.rmtree("uploads", ignore_errors=True)
            os.makedirs("uploads/old", exist_ok=True)
            os.makedirs("uploads/new", exist_ok=True)
            old_path = os.path.join("uploads/old", old_file.name)
            new_path = os.path.join("uploads/new", new_file.name)
            with open(old_path, "wb") as f:
                f.write(old_file.getbuffer())
            with open(new_path, "wb") as f:
                f.write(new_file.getbuffer())

            status_panel.info("Running driver.py ...")
            run_start = time.time()

            driver_path = os.path.join(os.path.dirname(__file__), "src", "antarbhukti", "driver.py")
            prompt_file = os.path.join(os.path.dirname(driver_path), "prompts", "original", "iterative_prompting.txt")
            os.makedirs(os.path.dirname(prompt_file), exist_ok=True)
            if not os.path.exists(prompt_file):
                with open(prompt_file, "w") as ph:
                    ph.write("Provide PLC upgrade rules and verify correctness.\n")

            result_root = "outputs"
            os.makedirs(result_root, exist_ok=True)

            llm_arg = selected_llm.lower() if run_mode.startswith("Single") else "all"
            cmd = [
                "python3",
                "-u",
                driver_path,
                "--src_path", os.path.join("uploads", "old"),
                "--mod_path", os.path.join("uploads", "new"),
                "--result_root", result_root,
                "--prompt_path", prompt_file,
                "--config_path", os.path.join(os.path.dirname(driver_path), "config.json"),
                "--llms", llm_arg
            ]

            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)

            full_stdout = ""
            full_stderr = ""

            # stream stdout
            try:
                for line in process.stdout:
                    full_stdout += line
                    logs = add_log_text(logs, line.rstrip(), log_panel)
                leftover = process.stdout.read()
                if leftover:
                    full_stdout += leftover
                    logs = add_log_text(logs, leftover.rstrip(), log_panel)
            except Exception:
                pass

            # capture stderr
            try:
                full_stderr = process.stderr.read()
                if full_stderr:
                    logs = add_log_text(logs, full_stderr.strip(), log_panel)
            except Exception:
                pass

            retcode = process.wait()

            status_panel.success("Driver run completed.")

            # extract blocks from captured output
            blocks = extract_blocks(full_stdout)

            # if none found, attempt to read a saved file matching the NEW filename
            if not blocks:
                saved_path = find_saved_file_by_basename(os.path.basename(new_file.name), os.getcwd(), min_mtime=run_start)
                if saved_path:
                    try:
                        with open(saved_path, "r", encoding="utf-8", errors="replace") as fh:
                            content = fh.read()
                            blocks = [sanitize_text(content)]
                            logs = add_log_text(logs, f"Found corrected file: {saved_path}", log_panel)
                    except Exception:
                        pass

            # Display full output and any extracted blocks
            with tab3:
                st.header("Verification Output")
                st.subheader("Console Output")
                st.text_area("Full Output", full_stdout + ("\n" + full_stderr if full_stderr else ""), height=400)
                if blocks:
                    st.subheader("Extracted Corrected SFC")
                    for i, b in enumerate(blocks, start=1):
                        st.markdown(f"### Block {i}")
                        st.code(b, language="")
                else:
                    st.info("No corrected SFC was extracted or found on disk.")

            # persist result summary
            try:
                with open(os.path.join(result_root, "result.txt"), "w", encoding="utf-8", errors="replace") as rf:
                    rf.write(full_stdout + ("\n" + full_stderr if full_stderr else ""))
            except Exception:
                pass

# ---------------------------
# About
# ---------------------------
with tab4:
    st.header("About")
    st.markdown("""
Antarbhukti is an LLM-driven PLC upgrade verification framework.

Notes:
- This UI intentionally keeps output concise (no debug mode).
- If no corrected SFC appears, try running with "Single LLM (fast)" and check the console-run of driver.py for details.
""")
# import streamlit as st
# import os
# import json
# import subprocess
# import datetime
# import shutil
# import re

# # ---------------------------------------------------------
# # CONFIG LOADER
# # ---------------------------------------------------------

# def load_config():
#     app_dir = os.path.dirname(os.path.abspath(__file__))
#     cfg_path = os.path.join(app_dir, "src", "antarbhukti", "config.json")
#     if not os.path.exists(cfg_path):
#         st.error(f"❌ Config file missing: {cfg_path}")
#         st.stop()
#     with open(cfg_path, "r") as f:
#         return json.load(f)

# # ---------------------------------------------------------
# # STREAMLIT PAGE SETTINGS
# # ---------------------------------------------------------

# st.set_page_config(
#     page_title="Antarbhukti – LLM-based PLC Verification",
#     page_icon="🧠",
#     layout="wide"
# )

# st.markdown("""
# <style>
# .big-title { font-size: 32px !important; font-weight: 700 !important; color: #2E86C1; }
# .log-box { background-color: #1E1E1E; color: #00FF41; padding: 15px; border-radius: 8px;
#            height: 350px; overflow-y: scroll; font-family: monospace; font-size: 14px; border: 1px solid #555; }
# </style>
# """, unsafe_allow_html=True)

# st.markdown('<p class="big-title">🧠 Antarbhukti — LLM-Driven PLC Upgrade Verification</p>', unsafe_allow_html=True)
# st.write("Automatically generate upgrade rules for PLC programs using LLMs and verify correctness using formal methods.")

# # ---------------------------------------------------------
# # LOAD CONFIG & SELECT LLM
# # ---------------------------------------------------------

# config_list = load_config()
# llm_names = [c["llm_name"] for c in config_list]

# st.sidebar.title("⚙️ LLM Configuration")
# selected_llm = st.sidebar.selectbox("Choose LLM", llm_names)
# config = next(c for c in config_list if c["llm_name"] == selected_llm)
# st.sidebar.success(f"Using model: {config['model_name']}")

# # ---------------------------------------------------------
# # TABS
# # ---------------------------------------------------------

# tab1, tab2, tab3, tab4 = st.tabs(["📤 Upload Files", "⚙️ Run Verification", "📜 Logs", "ℹ️ About"])

# # ---------------------------------------------------------
# # TAB 1 — FILE UPLOAD
# # ---------------------------------------------------------

# with tab1:
#     st.subheader("📤 Upload the PLC Programs")
#     st.markdown("Upload the **OLD** and **NEW** versions of the PLC program.")
#     old_file = st.file_uploader("OLD PLC Program", type=["txt", "st"])
#     new_file = st.file_uploader("NEW PLC Program", type=["txt", "st"])
#     if old_file and new_file:
#         st.success("Files ready for processing. Move to **Run Verification** tab.")

# # ---------------------------------------------------------
# # LIVE LOGGING FUNCTION
# # ---------------------------------------------------------

# def add_log(logs, msg, panel, level="INFO"):
#     color = {"INFO": "#00AEEF", "ERROR": "#FF4444", "SUCCESS": "#00CC66"}.get(level, "#00AEEF")
#     logs += f"<span style='color:{color};'>[{datetime.datetime.now()}] {msg}</span><br>"
#     panel.markdown(f"<div class='log-box'>{logs}</div>", unsafe_allow_html=True)
#     return logs

# # ---------------------------------------------------------
# # SAFE CODE BLOCK EXTRACTOR (NEW FIX)
# # ---------------------------------------------------------

# def extract_code_blocks(full_output: str):
#     """
#     Extract code from LLM output even when no triple-backticks exist.
#     This makes Streamlit behave EXACTLY like console.
#     """

#     # 1. Extract normal fenced code blocks if present
#     fenced = re.findall(r"```(?:\w*\n)?([\s\S]*?)```", full_output)
#     if fenced:
#         return fenced

#     # 2. If no fenced blocks → extract meaningful PLC code lines (fallback)
#     keywords = ["STEP", "STATE", "TRANSITION", "IF", "THEN", "ELSE", ":=", "="]

#     candidate_lines = []
#     for line in full_output.split("\n"):
#         if any(k in line for k in keywords):
#             candidate_lines.append(line)

#     if len(candidate_lines) >= 3:
#         return ["\n".join(candidate_lines)]

#     # 3. If still nothing → return empty list
#     return []

# # ---------------------------------------------------------
# # TAB 2 — RUN VERIFICATION
# # ---------------------------------------------------------

# with tab2:
#     st.subheader("⚙️ Run the Antarbhukti Verification Pipeline")
#     run_btn = st.button("🚀 Start Verification")

#     if run_btn:
#         if old_file is None or new_file is None:
#             st.error("❌ Please upload both OLD and NEW files.")
#             st.stop()

#         # Save uploaded files
#         st.info("📁 Saving uploaded files...")
#         old_folder = "uploads/old"
#         new_folder = "uploads/new"
#         shutil.rmtree("uploads", ignore_errors=True)
#         os.makedirs(old_folder, exist_ok=True)
#         os.makedirs(new_folder, exist_ok=True)

#         with open(os.path.join(old_folder, old_file.name), "wb") as f:
#             f.write(old_file.read())
#         with open(os.path.join(new_folder, new_file.name), "wb") as f:
#             f.write(new_file.read())
#         st.success("Uploaded files saved successfully.")

#         # Ensure prompt file exists
#         driver_path = os.path.join(os.path.dirname(__file__), "src", "antarbhukti", "driver.py")
#         prompts_dir = os.path.join(os.path.dirname(driver_path), "prompts", "original")
#         os.makedirs(prompts_dir, exist_ok=True)
#         prompt_file = os.path.join(prompts_dir, "iterative_prompting.txt")
#         if not os.path.exists(prompt_file):
#             with open(prompt_file, "w") as f:
#                 f.write("# Default iterative prompt for Antarbhukti\nProvide PLC upgrade rules and verify correctness.\n")
#             st.info(f"Created default prompt file at {prompt_file}")

#         os.makedirs("outputs", exist_ok=True)

#         cmd = [
#             "python3",
#             driver_path,
#             "--src_path", old_folder,
#             "--mod_path", new_folder,
#             "--result_root", "outputs",
#             "--prompt_path", prompt_file,
#             "--config_path", os.path.join(os.path.dirname(driver_path), "config.json"),
#             "--llms", "all"
#         ]

#         progress = st.progress(0)
#         status_text = st.empty()
#         log_panel = st.empty()
#         logs = ""
#         status_text.write("⏳ Running verification pipeline...")

#         # Run driver.py
#         process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)
#         full_stdout = ""

#         for line in process.stdout:
#             full_stdout += line
#             logs = add_log(logs, line.rstrip(), log_panel, "INFO")

#         stderr_output = process.stderr.read()
#         if stderr_output:
#             logs = add_log(logs, stderr_output.strip(), log_panel, "ERROR")

#         retcode = process.wait()

#         # Extract code blocks (new logic)
#         code_blocks = extract_code_blocks(full_stdout)

#         if code_blocks:
#             logs = add_log(logs, f"✔ Extracted {len(code_blocks)} code blocks.", log_panel, "SUCCESS")
#         else:
#             logs = add_log(logs, "⚠️ No code blocks found. Showing raw output.", log_panel, "INFO")
#             code_blocks = [full_stdout]  # force console-like display

#         output_text = full_stdout + "\n" + stderr_output

#         if retcode != 0:
#             st.warning("⚠️ driver.py exited with errors. See logs.")
#         else:
#             st.success("🎉 Verification Finished Successfully!")

#         progress.progress(100)
#         st.subheader("📘 Verification Output")

#         # Show EXACTLY like console
#         st.text_area("Full Output", output_text, height=500)

#         # Save results
#         with open("outputs/result.txt", "w") as f:
#             f.write(output_text)

#         with open("outputs/result.txt", "rb") as f:
#             st.download_button("⬇️ Download Verification Report", f, file_name="antarbhukti_result.txt")

# # ---------------------------------------------------------
# # TAB 3 — LOG PANEL
# # ---------------------------------------------------------

# with tab3:
#     st.subheader("📜 Execution Logs")
#     st.info("Logs will appear in real-time during execution.")

# # ---------------------------------------------------------
# # TAB 4 — ABOUT
# # ---------------------------------------------------------

# with tab4:
#     st.subheader("ℹ️ About Antarbhukti")
#     st.markdown("""
# **Antarbhukti** is an AI-driven PLC upgrade verification framework.

# ### Features
# - 🤖 LLM-based PLC upgrade rule synthesis  
# - 🔍 Formal equivalence checking  
# - 🧪 PLC model extraction  
# - 📝 Detailed verification reports  
# - 🧩 Extendable architecture  

# Developed by **Dr. Soumyadip Bandyopadhyay**, ABB.
# """)

