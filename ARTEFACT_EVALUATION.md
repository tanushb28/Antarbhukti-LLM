# Artefact Evaluation Instructions — SEFM'26

---

## A.1 Badge claims

We hope to claim the **Artefacts Functional** badge for this submission.

The artefact is the **LLMA (Antarbhukti-LLM) verification tool**, a Streamlit-based web application backed by a formal verification engine. It implements iterative LLM-guided repair of upgraded SFC (Sequential Function Chart) programs, verified for behavioural containment using the Z3 SMT solver.

### Functional outcomes

The following functional outcomes can be reproduced using the artefact:

- **F1** – Given a pair of SFC programs (original SFC1 and a candidate upgraded SFC2), the tool correctly determines whether SFC2 is behaviourally contained within SFC1 using Petri net containment checking (Z3 SMT solver). Containment checks on the provided OSCAT benchmark pairs should match the pass/fail results reported in Table *(N)* of the paper.

- **F2** – When SFC2 initially fails containment, the tool's iterative LLM-repair loop (up to 10 iterations) successfully repairs a statistically significant proportion of failing programs, matching the success rates reported for each LLM (GPT-4o, Gemini, LLaMA, Claude, Perplexity) in Table *(M)* of the paper.

- **F3** – The **Upgraded SFC Generator** tab correctly synthesises a new candidate SFC2 from a user-supplied SFC1, applying the selected upgrade strategy (Reliability or Safety) and user-specified When/Action requirements via LLM prompt engineering.

---

## A.2 Quick start

**Important Note:** A hosted version of the tool is available at https://llma-tool.streamlit.app/ with functional LLM API keys pre-configured. 

If you wish to run the tool locally, follow the instructions below.

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) installed on the reviewer's machine (Linux, macOS, or Windows).
- LLM API credentials for at least one of: OpenAI (GPT-4o), Google (Gemini), Groq (LLaMA), Anthropic (Claude), or Perplexity.
  *(These will be communicated to reviewers securely via the EasyChair submission notes.)*

### Setup

**Option A — Docker Compose (recommended)**

```bash
# 1. Extract the source archive
unzip antarbhukti_artefact.zip
cd antarbhukti_artefact

# 2. Fill in your API key(s) in the config file
cp src/antarbhukti/config_example.json src/antarbhukti/config.json
# Edit config.json: replace placeholder api_key values with real keys.

# 3. Uncomment the config.json volume mount in docker-compose.yml, then start
docker-compose up --build
```

**Option B — Pre-built Docker image**

```bash
# Load the submitted image (no build required)
docker load -i antarbhukti-image.tar

# Provide config.json with credentials, then run
docker run -p 8501:8501 \
  -v "$(pwd)/src/antarbhukti/config.json:/app/src/antarbhukti/config.json:ro" \
  -v "$(pwd)/outputs:/app/outputs" \
  antarbhukti-app
```

### Sanity check

Open a web browser and navigate to `http://localhost:8501`.  
✅ Expected: The **LLMA Verification Suite** dashboard loads with five tabs visible.

### Directory structure

```
antarbhukti_artefact/
├── app.py .................................. Main Streamlit application (entry point)
├── Dockerfile .............................. Container build instructions
├── docker-compose.yml ...................... Compose configuration
├── requirements.txt ........................ Python dependencies
├── setup.py ................................ Package installer
├── src/antarbhukti/ ........................ Core verification library
│   ├── sfc.py .............................. SFC data model & Petri net converter
│   ├── sfc_verifier.py ..................... Z3 containment engine
│   ├── driver.py ........................... Iterative LLM-repair orchestrator
│   ├── llm_mgr.py .......................... Abstract LLM base class
│   ├── llm_codegen.py ...................... Concrete LLM implementations (GPT, Gemini, etc.)
│   ├── genreport.py ........................ HTML/CSV report generator
│   ├── promptgen.py ........................ Prompt assembly utilities
│   ├── config_example.json ................. Credential template (fill and rename to config.json)
│   └── prompts/ ............................ Prompt templates used by the repair loop
├── prompts/original/ ....................... Prompt templates used at runtime by app.py
│   └── iterative_prompting.txt ............. Primary iterative refinement prompt
├── new_benchmarks/ ......................... ⭐ Sample SFC pairs for evaluation (see below)
│   ├── reliability/
│   │   ├── orig/ ........................... 25 original SFC1 programs (reliability category)
│   │   └── mod/ ............................ 25 upgraded SFC2 programs (reliability category)
│   ├── safety/
│   │   ├── orig/ ........................... Original SFC1 programs (safety category)
│   │   └── mod/ ............................ Upgraded SFC2 programs (safety category)
│   └── testsafety/ ......................... Quick-test subset: 5 orig/mod pairs
│       ├── orig/ ........................... 5 original SFC1 files
│       └── mod/ ............................ 5 upgraded SFC2 files
├── benchmarks/ ............................. OSCAT benchmark SFC pairs
│   ├── Benchmark-Source-OSCAT.py ........... 80 original SFC1 programs
│   └── Benchmarks-Upgrade-OSCAT.py ......... 80 upgraded SFC2 programs
└── evaluation/ ............................. Supporting evaluation scripts
```

### Sample benchmarks

The artefact ships with ready-to-upload SFC pairs in `new_benchmarks/`. Files are named uniformly (matching `orig/` and `mod/` names), so no renaming is required before uploading.

| Folder | Type | # Pairs | Recommended for |
|---|---|---|---|
| `new_benchmarks/testsafety/` | Safety upgrades | 5 | **Quick sanity check (< 5 min)** |
| `new_benchmarks/safety/` | Safety upgrades | Full set | Full safety evaluation |
| `new_benchmarks/reliability/` | Reliability upgrades | 25 | Full reliability evaluation |

> **Recommended starting point for reviewers:** Use `testsafety/` first. It has only 5 pairs and will complete in a few minutes, confirming the tool works end-to-end before running a larger batch.

---

## A.3 Functional evaluation

### Verifying F1 & F2 — OSCAT benchmark batch verification

This reproduces the main experimental results (containment checking + iterative LLM repair).

**Recommended quick run (≈ 5 min):** Use the `new_benchmarks/testsafety/` subset (5 pairs).
**Full evaluation:** Use `new_benchmarks/reliability/` (25 pairs) or `new_benchmarks/safety/`.

1. Open the app at `http://localhost:8501`.
2. In the **sidebar**, select the LLM engine(s) you wish to test (e.g., `gpt4o`).
3. Go to the **📂 Workstation** tab.
   - Under *"1. Original SFCs"*, upload all `.txt` files from `new_benchmarks/testsafety/orig/`.
   - Under *"2. Modified SFCs"*, upload all `.txt` files from `new_benchmarks/testsafety/mod/`.
   - Files are matched alphabetically — since both folders share the same filenames, pairing is automatic.
4. Go to the **🚀 Processing Engine** tab and click **▶️ Start Batch Verification**.
5. A live console streams the output of `driver.py` per file pair. When complete, the **📝 Reports** tab shows:
   - **Success Rate** — percentage of SFC2 programs that passed containment (possibly after LLM repair).
   - **Avg. Iterations** — average LLM refinement calls needed.
   - A downloadable CSV with per-benchmark results.

**Expected outcome (F1 & F2):** The success rates and average iteration counts should closely match Table *(N)* and Table *(M)* of the paper for the corresponding LLM.

---

### Verifying F3 — Upgraded SFC Generator

1. Go to the **Upgraded SFC Generator** tab.
2. Under *"1. Source & Intent"*, upload any `.txt` SFC1 file (e.g., one from `benchmarks/`).
3. Select an upgrade objective (e.g., **Reliability**) and one tactic rule (e.g., *Input Validation*).
4. Optionally customise the *When* and *Action* fields, then click **Generate Upgrade Prompt & Code**.
5. The tool calls the selected LLM and displays the generated SFC2 code.

**Expected outcome (F3):** The generated SFC2 follows the structured format (`steps`, `transitions`, `variables`, `initial_step`) and reflects the selected reliability/safety requirement. The generated file can then be downloaded and fed back into the **Workstation** tab to verify containment.
