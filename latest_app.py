#!/usr/bin/env python3
"""
Antarbhukti — Streamlit UI (Batch Processing Enabled)

- Runs src/antarbhukti/driver.py with unbuffered Python (-u).
- Captures stdout/stderr and displays them.
- Extracts corrected SFC text.
- Supports BATCH uploading (side-by-side Old/New pairs).
- Generates session-specific CSV reports.
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
import pandas as pd # Required for CSV display

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
st.write("Batch Mode: Upload multiple pairs of OLD and NEW SFC files to verify them sequentially.")

# ---------------------------
# Load config and LLM selection
# ---------------------------
config_list = load_config()
llm_names = [c.get("llm_name", "unknown") for c in config_list] if config_list else ["gpt4o"]

st.sidebar.title("Settings")
selected_llm = st.sidebar.selectbox("Choose LLM (single-run)", llm_names)
run_mode = st.sidebar.radio("Run mode", ("Single LLM (fast)", "All LLMs (slow)"))

# ---------------------------
# Session State
# ---------------------------
if "file_pairs" not in st.session_state:
    st.session_state.file_pairs = [{"id": 0}]
if "pair_counter" not in st.session_state:
    st.session_state.pair_counter = 1
# New: Track the current batch report CSV path
if "current_batch_csv" not in st.session_state:
    st.session_state.current_batch_csv = None

def add_pair():
    st.session_state.file_pairs.append({"id": st.session_state.pair_counter})
    st.session_state.pair_counter += 1

def remove_pair(index):
    if len(st.session_state.file_pairs) > 1:
        st.session_state.file_pairs.pop(index)

# ---------------------------
# Tabs
# ---------------------------
tab1, tab2, tab3, tab4 = st.tabs(["Upload (Batch)", "Run", "Output", "About"])

with tab1:
    st.header("Batch Upload")
    st.write("Add pairs of files. Each row represents one verification task.")
    
    has_valid_pair = False

    for index, pair in enumerate(st.session_state.file_pairs):
        with st.container():
            st.markdown(f"**Pair #{index + 1}**")
            col1, col2, col3 = st.columns([5, 5, 1])
            with col1:
                old_f = st.file_uploader(f"OLD SFC #{index+1}", type=["txt", "st"], key=f"old_{pair['id']}")
            with col2:
                new_f = st.file_uploader(f"NEW SFC #{index+1}", type=["txt", "st"], key=f"new_{pair['id']}")
            with col3:
                st.write("") 
                st.write("")
                if st.button("❌", key=f"del_{pair['id']}", help="Remove this pair"):
                    remove_pair(index)
                    st.rerun()
            
            if old_f and new_f:
                has_valid_pair = True
                
            st.divider()

    st.button("➕ Add Another Pair", on_click=add_pair)
    
    if has_valid_pair:
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

    # SFC-structured blocks
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
# Filesystem probe
# ---------------------------
def find_saved_file_by_basename(basename, repo_root, min_mtime=0.0):
    patterns = [
        os.path.join(repo_root, "outputs", "**", "success", "**", basename),
        os.path.join(repo_root, "output", "**", "success", "**", basename),
        os.path.join(repo_root, "**", basename),
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
# Run tab: execute driver (Batch support)
# ---------------------------
with tab2:
    st.header("Run Batch Verification")
    run_button = st.button("Start Batch Verification", type="primary")
    
    if run_button:
        # 1. Collect Valid Pairs
        valid_pairs = []
        for index, pair in enumerate(st.session_state.file_pairs):
            old_f = st.session_state.get(f"old_{pair['id']}")
            new_f = st.session_state.get(f"new_{pair['id']}")
            if old_f and new_f:
                valid_pairs.append({
                    "id": pair['id'], 
                    "index": index+1, 
                    "old_file": old_f, 
                    "new_file": new_f
                })
        
        if not valid_pairs:
            st.error("Please upload at least one pair of OLD and NEW files.")
        else:
            # 2. Prepare Directories & CSV
            if os.path.exists("uploads"):
                shutil.rmtree("uploads", ignore_errors=True)
            result_root = "outputs"
            os.makedirs(result_root, exist_ok=True)
            
            # --- NEW: Generate Unique CSV for this Batch ---
            timestamp = int(time.time())
            csv_filename = f"batch_report_{timestamp}.csv"
            session_csv_path = os.path.abspath(os.path.join(result_root, csv_filename))
            st.session_state.current_batch_csv = session_csv_path
            
            # 3. Process Pairs Sequentially
            progress_bar = st.progress(0)
            
            for i, task in enumerate(valid_pairs):
                pair_upload_dir = os.path.join("uploads", f"pair_{task['id']}")
                old_dir = os.path.join(pair_upload_dir, "old")
                new_dir = os.path.join(pair_upload_dir, "new")
                
                os.makedirs(old_dir, exist_ok=True)
                os.makedirs(new_dir, exist_ok=True)
                
                with open(os.path.join(old_dir, task['old_file'].name), "wb") as f:
                    f.write(task['old_file'].getbuffer())
                with open(os.path.join(new_dir, task['new_file'].name), "wb") as f:
                    f.write(task['new_file'].getbuffer())
                
                with st.expander(f"Processing Pair {task['index']}: {task['new_file'].name}", expanded=True):
                    status_panel = st.empty()
                    log_panel = st.empty()
                    logs = ""
                    
                    status_panel.info(f"Running verification for {task['new_file'].name}...")
                    run_start = time.time()
                    
                    driver_path = os.path.join(os.path.dirname(__file__), "src", "antarbhukti", "driver.py")
                    prompt_file = os.path.join(os.path.dirname(__file__), "prompts", "original", "iterative_prompting.txt")
                    
                    os.makedirs(os.path.dirname(prompt_file), exist_ok=True)
                    if not os.path.exists(prompt_file):
                         with open(prompt_file, "w") as ph:
                             ph.write("Provide PLC upgrade rules and verify correctness.\n")

                    llm_arg = selected_llm.lower() if run_mode.startswith("Single") else "all"
                    
                    cmd = [
                        "python3", "-u", driver_path,
                        "--src_path", old_dir,
                        "--mod_path", new_dir,
                        "--result_root", result_root,
                        "--prompt_path", prompt_file,
                        "--config_path", os.path.join(os.path.dirname(driver_path), "config.json"),
                        "--llms", llm_arg
                    ]
                    
                    # --- NEW: Pass CSV Path via Env Var ---
                    # Copy current environment and add our custom CSV path
                    env_vars = os.environ.copy()
                    env_vars["BENCHMARK_CSV_PATH"] = session_csv_path
                    
                    try:
                        process = subprocess.Popen(
                            cmd, 
                            stdout=subprocess.PIPE, 
                            stderr=subprocess.STDOUT, 
                            text=True, 
                            bufsize=1,
                            env=env_vars  # Pass the modified environment
                        )
                        
                        full_stdout = ""
                        for line in process.stdout:
                            full_stdout += line
                            logs = add_log_text(logs, line.rstrip(), log_panel)
                        
                        retcode = process.wait()
                        
                        if retcode == 0:
                            status_panel.success(f"Finished: {task['new_file'].name}")
                        else:
                            status_panel.error(f"Failed: {task['new_file'].name}")
                            
                        # Extract result
                        blocks = extract_blocks(full_stdout)
                        if not blocks:
                            saved_path = find_saved_file_by_basename(os.path.basename(task['new_file'].name), os.getcwd(), min_mtime=run_start)
                            if saved_path:
                                with open(saved_path, "r", encoding="utf-8", errors="replace") as fh:
                                    blocks = [sanitize_text(fh.read())]
                                    logs = add_log_text(logs, f"Found file: {saved_path}", log_panel)

                        if blocks:
                            st.subheader("Corrected Code Preview")
                            st.code(blocks[0], language="")
                            
                    except Exception as e:
                        st.error(f"Execution failed: {str(e)}")

                progress_bar.progress((i + 1) / len(valid_pairs))
            
            st.success("Batch Queue Completed! Check Output tab for report.")

# ---------------------------
# Output Tab
# ---------------------------
with tab3:
    st.header("Verification Output")
    
    # 1. Batch CSV Report (Dynamic)
    current_csv = st.session_state.get("current_batch_csv")
    
    if current_csv and os.path.exists(current_csv):
        st.subheader("📊 Current Batch Report")
        try:
            df = pd.read_csv(current_csv)
            st.dataframe(df)
            
            with open(current_csv, "rb") as f:
                st.download_button(
                    label="📥 Download Batch CSV",
                    data=f,
                    file_name=os.path.basename(current_csv),
                    mime="text/csv"
                )
        except Exception as e:
            st.error(f"Error reading CSV: {e}")
    else:
        st.info("No batch report generated yet. Run a verification batch to see results here.")
    
    st.divider()
    
    # 2. File Browser
    st.subheader("Generated Files")
    success_files = []
    for root, dirs, files in os.walk("outputs"):
        if "success" in root:
            for file in files:
                success_files.append(os.path.join(root, file))
    
    if success_files:
        selected_file = st.selectbox("Select a result file to view:", success_files)
        if selected_file:
            with open(selected_file, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
                st.text_area("File Content", content, height=400)
                st.download_button("📥 Download File", content, file_name=os.path.basename(selected_file))
    else:
        st.info("No successful output files found yet.")

# ---------------------------
# About
# ---------------------------
with tab4:
    st.header("About")
    st.markdown("""
Antarbhukti is an LLM-driven PLC upgrade verification framework.

Notes:
- Batch Mode enabled: Upload pairs in Tab 1.
- Results are saved in `outputs/`.
- CSV Reports are generated per-batch in the Output tab.
""")
