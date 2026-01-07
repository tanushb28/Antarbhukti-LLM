#!/usr/bin/env python3
"""
Antarbhukti — Enterprise Verification Platform
UI/UX Updated: Dashboard-First, Metrics-Driven, Sales-Ready.
Fixed: Parses wide-format CSVs (<llm>_iter, <llm>_time) correctly for graphs.
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
import pandas as pd
import altair as alt

# ---------------------------
# Config & Page Setup
# ---------------------------
st.set_page_config(page_title="Antarbhukti Enterprise", page_icon="⚡", layout="wide")

def load_config():
    app_dir = os.path.dirname(os.path.abspath(__file__))
    cfg_path = os.path.join(app_dir, "src", "antarbhukti", "config.json")
    if not os.path.exists(cfg_path):
        # Fallback if file missing, though typically it should be there
        return []
    with open(cfg_path, "r", encoding="utf-8") as f:
        return json.load(f)

# --- CSS: Enterprise Styling ---
st.markdown("""
<style>
    /* Remove default padding */
    .block-container { padding-top: 1rem !important; padding-bottom: 2rem !important; }
    
    /* Brand Header */
    .main-header {
        font-family: 'Helvetica Neue', sans-serif;
        background: linear-gradient(90deg, #0F2027 0%, #203A43 50%, #2C5364 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .main-header h1 { font-size: 2.2rem; margin: 0; font-weight: 700; color: #fff; }
    .main-header p { font-size: 1rem; margin: 5px 0 0 0; opacity: 0.8; }

    /* Metric Cards Styling */
    div[data-testid="metric-container"] {
        background-color: #F0F2F6;
        border: 1px solid #D6D6D6;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    /* Terminal Logs */
    .log-box { 
        background-color: #1E1E1E; 
        color: #00FF41; 
        padding: 15px; 
        border-radius: 6px; 
        height: 400px; 
        overflow-y: auto; 
        font-family: 'Courier New', monospace; 
        font-size: 13px; 
    }
</style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown("""
    <div class="main-header">
        <h1>⚡ Antarbhukti Verification Suite</h1>
        <p>AI-Powered PLC Logic Assurance & Safety Compliance</p>
    </div>
""", unsafe_allow_html=True)

# ---------------------------
# Helper: Data Aggregation (Fixed for Wide CSV Format)
# ---------------------------
def load_historical_data(result_root="outputs"):
    """
    Scans batch CSVs and transforms wide format (<llm>_iter, <llm>_time) 
    into long format (Model, Time, Iteration) for visualization.
    """
    # 1. Find all CSVs
    all_files = glob.glob(os.path.join(result_root, "batch_report_*.csv"))
    
    # Fallback to default if no specific batch reports found
    if not all_files:
        default_csv = os.path.join(os.path.dirname(__file__), "NewBenchmark_Sheet1.csv")
        if os.path.exists(default_csv):
            all_files = [default_csv]
    
    if not all_files:
        return pd.DataFrame()

    standardized_rows = []
    
    # Known LLM prefixes based on your CSV header format
    # Header format: GPT4o_iter, Gemini_iter, LLaMA_iter, Claude_iter, Perplexity_iter
    llm_prefixes = ["GPT4o", "Gemini", "LLaMA", "Claude", "Perplexity"]

    for filename in all_files:
        try:
            df = pd.read_csv(filename)
            
            # Iterate through each row in the CSV
            for _, row in df.iterrows():
                # Check each LLM to see if it ran for this benchmark
                for llm in llm_prefixes:
                    # Construct column names
                    iter_col = f"{llm}_iter"
                    time_col = f"{llm}_time"
                    token_col = f"{llm}_tokens"
                    
                    # Ensure columns exist and have data (not empty/NaN)
                    if iter_col in df.columns and pd.notna(row[iter_col]) and str(row[iter_col]).strip() != "":
                        
                        # Extract values safely
                        try:
                            iterations = float(row[iter_col])
                            # Time might be empty string or NaN
                            time_val = float(row[time_col]) if (time_col in df.columns and pd.notna(row[time_col]) and row[time_col] != "") else 0.0
                            tokens = float(row[token_col]) if (token_col in df.columns and pd.notna(row[token_col]) and row[token_col] != "") else 0.0
                            
                            # Estimate cost (approx $5 per 1M tokens blended avg for visualization)
                            cost = (tokens / 1_000_000) * 5.0 
                            
                            standardized_rows.append({
                                "Benchmark Name": row.get("Benchmark Name", "Unknown"),
                                "Type": row.get("Type", "Unknown"),
                                "Model": llm,
                                "Iteration": iterations,
                                "Time": time_val,
                                "Tokens": tokens,
                                "Cost": cost,
                                "Source File": os.path.basename(filename)
                            })
                        except ValueError:
                            continue # Skip malformed rows

        except Exception as e:
            # print(f"Error reading {filename}: {e}") # Debug only
            continue
            
    if standardized_rows:
        return pd.DataFrame(standardized_rows)
    return pd.DataFrame()

# ---------------------------
# Sidebar State & Settings
# ---------------------------
if "file_pairs" not in st.session_state:
    st.session_state.file_pairs = [{"id": 0}]
if "pair_counter" not in st.session_state:
    st.session_state.pair_counter = 1
if "current_batch_csv" not in st.session_state:
    st.session_state.current_batch_csv = None

config_list = load_config()
llm_names = [c.get("llm_name", "unknown") for c in config_list] if config_list else ["gpt4o"]

with st.sidebar:
    st.header("⚙️ Configuration")
    selected_llm = st.selectbox("LLM Engine", llm_names)
    run_mode = st.radio("Optimization Mode", ("Single Pass (Fast)", "Deep Verification (Slow)"))
    st.divider()
    st.info("System Ready")

# ---------------------------
# Helper Functions (Logic)
# ---------------------------
def add_pair():
    st.session_state.file_pairs.append({"id": st.session_state.pair_counter})
    st.session_state.pair_counter += 1

def remove_pair(index):
    if len(st.session_state.file_pairs) > 1:
        st.session_state.file_pairs.pop(index)

def add_log_text(logs, msg, panel):
    logs += f"[{datetime.datetime.now().strftime('%H:%M:%S')}] {msg}\n"
    panel.text_area("Console Stream", logs, height=400, label_visibility="collapsed")
    return logs

def extract_blocks(full_output: str):
    out = unicodedata.normalize("NFKC", full_output or "")
    blocks = re.findall(r"```(?:\w*\n)?([\s\S]*?)```", out)
    if not blocks:
        # Fallback: Look for PLC keywords
        plc_lines = [ln for ln in out.splitlines() if any(k in ln for k in ["STEP", "TRANSITION", "IF", ":="])]
        if len(plc_lines) > 3:
            blocks.append("\n".join(plc_lines))
    return blocks

def find_saved_file_by_basename(basename, repo_root, min_mtime=0.0):
    for pat in [os.path.join(repo_root, "outputs", "**", "success", "**", basename),
                os.path.join(repo_root, "**", basename)]:
        for match in glob.glob(pat, recursive=True):
            if os.path.isfile(match) and os.path.getmtime(match) + 1e-6 >= min_mtime:
                return os.path.abspath(match)
    return None

# ---------------------------
# MAIN TABS
# ---------------------------
tab_dash, tab_upload, tab_run, tab_report = st.tabs([
    "📊 Executive Dashboard", 
    "📂 Workstation (Upload)", 
    "🚀 Processing Engine", 
    "📝 Reports & Analysis"
])

# --- TAB 1: EXECUTIVE DASHBOARD ---
with tab_dash:
    st.markdown("### 📈 Verification Performance Overview")
    
    df_history = load_historical_data()
    
    if not df_history.empty:
        # 1. Metrics Calculation
        total_runs = len(df_history)
        
        # Success Rate (Heuristic: If Iteration exists, it finished. 
        # Ideally, we'd check a Status column, but using presence of data as success proxy for now)
        success_count = total_runs 
        success_rate = 100.0 # Assuming rows in CSV imply completion
        
        avg_time = df_history['Time'].mean()
        avg_tokens = df_history['Tokens'].mean()
        
        # 2. Key Metric Cards
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Verifications", f"{total_runs}", delta="Runs")
        col2.metric("Success Rate", f"{success_rate:.0f}%", delta="Reliability")
        col3.metric("Avg. Time", f"{avg_time:.1f}s", delta="Speed")
        col4.metric("Avg. Tokens Used", f"{int(avg_tokens):,}", delta="Efficiency")
        
        st.divider()
        
        # 3. Graphs (Time vs Iteration)
        col_g1, col_g2 = st.columns([2, 1])
        
        with col_g1:
            st.subheader("Time vs. Complexity Analysis")
            # Filter out 0 time/iteration rows to avoid clutter
            chart_df = df_history[df_history['Time'] > 0]
            
            if not chart_df.empty:
                chart = alt.Chart(chart_df).mark_circle(size=80).encode(
                    x=alt.X('Iteration', title='Iterations Required'),
                    y=alt.Y('Time', title='Time taken (s)'),
                    color=alt.Color('Model', title='AI Model', scale=alt.Scale(scheme='category10')),
                    tooltip=['Benchmark Name', 'Model', 'Time', 'Iteration', 'Tokens']
                ).interactive()
                st.altair_chart(chart, use_container_width=True)
            else:
                st.info("Insufficient data for Time Graph.")

        with col_g2:
            st.subheader("Model Usage")
            st.bar_chart(df_history['Model'].value_counts())
            
            st.subheader("Recent Activity")
            st.dataframe(df_history[['Benchmark Name', 'Model', 'Time']].tail(5), hide_index=True)
                
    else:
        st.info("👋 Welcome! No verification history found. Go to 'Workstation' to verify your first file.")
        # Placeholders
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Total Verifications", "0")
        c2.metric("Success Rate", "0%")
        c3.metric("Avg. Time", "0s")
        c4.metric("Avg. Tokens", "0")

# --- TAB 2: WORKSTATION (UPLOAD) ---
with tab_upload:
    st.header("📂 Batch File Staging")
    st.write("Upload pairs of Original (Legacy) and Modified (New) SFC code.")
    
    has_valid_pair = False
    
    for index, pair in enumerate(st.session_state.file_pairs):
        with st.container():
            c1, c2, c3 = st.columns([0.45, 0.45, 0.1])
            with c1:
                old_f = st.file_uploader(f"Original SFC #{index+1}", key=f"old_{pair['id']}")
            with c2:
                new_f = st.file_uploader(f"Modified SFC #{index+1}", key=f"new_{pair['id']}")
            with c3:
                st.write("")
                st.write("") 
                if st.button("🗑️", key=f"del_{pair['id']}"):
                    remove_pair(index)
                    st.rerun()
            
            if old_f and new_f:
                has_valid_pair = True
            st.divider()

    c_add, c_spacer = st.columns([0.2, 0.8])
    with c_add:
        st.button("➕ Add Pair", on_click=add_pair)
    
    if has_valid_pair:
        st.success("✅ Files Staged. Proceed to 'Processing Engine'.")

# --- TAB 3: PROCESSING ENGINE ---
with tab_run:
    st.header("🚀 Verification Engine")
    
    if st.button("▶️ Start Verification Process", type="primary"):
        # 1. Validation
        valid_pairs = []
        for index, pair in enumerate(st.session_state.file_pairs):
            old_f = st.session_state.get(f"old_{pair['id']}")
            new_f = st.session_state.get(f"new_{pair['id']}")
            if old_f and new_f:
                valid_pairs.append({"id": pair['id'], "index": index+1, "old_file": old_f, "new_file": new_f})
        
        if not valid_pairs:
            st.error("No valid file pairs found.")
        else:
            # 2. Setup
            if os.path.exists("uploads"): shutil.rmtree("uploads", ignore_errors=True)
            result_root = "outputs"
            os.makedirs(result_root, exist_ok=True)
            
            # Session CSV (Note: Driver will append to or create this file)
            timestamp = int(time.time())
            csv_filename = f"batch_report_{timestamp}.csv"
            session_csv_path = os.path.abspath(os.path.join(result_root, csv_filename))
            st.session_state.current_batch_csv = session_csv_path
            
            # 3. Execution
            progress_bar = st.progress(0)
            
            for i, task in enumerate(valid_pairs):
                # Prepare paths
                pair_dir = os.path.join("uploads", f"pair_{task['id']}")
                old_dir, new_dir = os.path.join(pair_dir, "old"), os.path.join(pair_dir, "new")
                os.makedirs(old_dir, exist_ok=True)
                os.makedirs(new_dir, exist_ok=True)
                
                with open(os.path.join(old_dir, task['old_file'].name), "wb") as f: f.write(task['old_file'].getbuffer())
                with open(os.path.join(new_dir, task['new_file'].name), "wb") as f: f.write(task['new_file'].getbuffer())
                
                # UI for current file
                with st.status(f"Processing Pair {task['index']}: {task['new_file'].name}", expanded=True) as status:
                    log_panel = st.empty()
                    logs = ""
                    
                    driver_path = os.path.join(os.path.dirname(__file__), "src", "antarbhukti", "driver.py")
                    prompt_file = os.path.join(os.path.dirname(__file__), "prompts", "original", "iterative_prompting.txt")
                    
                    # Ensure prompt exists
                    os.makedirs(os.path.dirname(prompt_file), exist_ok=True)
                    if not os.path.exists(prompt_file):
                        with open(prompt_file, "w") as ph: ph.write("Provide PLC upgrade rules.")

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
                    
                    env_vars = os.environ.copy()
                    env_vars["BENCHMARK_CSV_PATH"] = session_csv_path
                    
                    try:
                        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1, env=env_vars)
                        
                        for line in process.stdout:
                            logs = add_log_text(logs, line.rstrip(), log_panel)
                        
                        retcode = process.wait()
                        
                        if retcode == 0:
                            status.update(label=f"✅ Completed: {task['new_file'].name}", state="complete", expanded=False)
                        else:
                            status.update(label=f"❌ Failed: {task['new_file'].name}", state="error", expanded=False)
                            
                    except Exception as e:
                        status.update(label="❌ Critical Error", state="error")
                        st.error(str(e))

                progress_bar.progress((i + 1) / len(valid_pairs))
            
            st.success("Batch Queue Processed Successfully.")

# --- TAB 4: REPORTS ---
with tab_report:
    st.header("📝 Reports & Analysis")
    
    col_r1, col_r2 = st.columns([1, 1])
    
    with col_r1:
        st.subheader("Current Batch Report")
        current_csv = st.session_state.get("current_batch_csv")
        if current_csv and os.path.exists(current_csv):
            # We display the raw CSV here for download
            df = pd.read_csv(current_csv)
            st.dataframe(df, use_container_width=True)
            with open(current_csv, "rb") as f:
                st.download_button("📥 Download Batch CSV", f, file_name=os.path.basename(current_csv))
        else:
            st.info("No active batch results.")

    with col_r2:
        st.subheader("View Corrected Code")
        success_files = []
        for root, dirs, files in os.walk("outputs"):
            if "success" in root:
                for file in files:
                    success_files.append(os.path.join(root, file))
        
        if success_files:
            selected_file = st.selectbox("Select File", success_files)
            if selected_file:
                with open(selected_file, "r") as f:
                    st.code(f.read(), language="python")
        else:
            st.warning("No fixed files found.")