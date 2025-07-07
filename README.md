# AntarBhukti

AntarBhukti is a verification tool for evolving software, designed to verify changes between two versions of SFCs (Sequential Function Charts) — a source and a target. It is specifically tailored for use with OSCAT application benchmarks.

---

## Features

- **Compare SFCs:** Verifies the correctness of software evolution using textual SFC representations.
- **Easy to Use:** Simple command line interface for fast verification tasks.
- **Benchmark Suite:** Works on all 80 OSCAT benchmark applications.  
  - `benchmarks/Benchmark-Source-OSCAT.py` contains the source/original SFCs.  
  - `benchmarks/Benchmarks-Upgrade-OSCAT.py` contains the upgraded/target SFCs.
- **Superior Performance:** Outperforms [verifaps](https://formal.kastel.kit.edu/verifaps/index.html) in coverage and flexibility.
- **Open ST Reference:** Reference ST code for the OSCAT library is available in the [SamaTulyata4PLC](https://github.com/soumyadipcsis/SamaTulyata4PLC) repository.

---

## Quick Start

Get up and running in 3 steps:

```sh
# 1. Clone and enter directory
git clone https://github.com/your-username/Antarbhukti-LLM.git
cd Antarbhukti-LLM

# 2. Set up environment (choose conda or pip)
conda env create -f environment.yml && conda activate antarbhukti
# OR: pip install -r requirements.txt

# 3. Install package
pip install -e .

# 4. (Optional) Set up environment variables and system dependencies
python setup_helper.py
```

## Environment Variables Setup

**⚠️ Important:** Before using AntarBhukti, you must configure environment variables with your API credentials.

1. Copy the template file:
   ```sh
   cp .env.template .env
   ```

2. Edit the `.env` file with your actual values:
   ```sh
   nano .env  # or use your preferred editor
   ```

3. Update the following variables in `.env`:
   - `AZURE_OPENAI_ENDPOINT` - Your Azure OpenAI service endpoint
   - `AZURE_OPENAI_API_KEY` - Your Azure OpenAI API key
   - `AZURE_OPENAI_API_VERSION` - API version (e.g., "2023-12-01-preview")
   - Any other required environment variables as specified in the template

The application will not function properly without these environment variables configured.

## Getting Started

**Core files:**  
- `src/antarbhukti/` - Main library code
- `examples/driver.py` - Example driver script  
- `examples/example_usage.py` - Usage examples
- `benchmarks/` - Benchmark suite
- `data/` - Sample SFC data files
- `setup.py` - Package configuration and installation
- `setup_helper.py` - Environment setup helper script

### Prerequisites

- Python 3.8+
- [Z3 SMT solver](https://github.com/Z3Prover/z3) (Python bindings)
- Azure OpenAI credentials (for LLM features)
- Conda (recommended) or pip for environment management
- Graphviz (optional, for visualization features)

### Installation

#### Option 1: Using Conda (Recommended)

1. Clone the repository:
```sh
git clone https://github.com/your-username/Antarbhukti-LLM.git
cd Antarbhukti-LLM
```

2. Create and activate conda environment:
```sh
conda env create -f environment.yml
conda activate antarbhukti
```

3. Install the package in development mode:
```sh
pip install -e .
```

4. (Optional) Set up environment variables and system dependencies:
```sh
python setup_helper.py
```
This will:
- Create `.env` file from template (if not exists)
- Install Graphviz system dependency (if needed)
- Verify Python version compatibility

5. Configure your Azure OpenAI credentials:
```sh
# Edit .env with your Azure OpenAI credentials
nano .env  # or use your preferred editor
```

#### Option 2: Using pip

1. Clone the repository:
```sh
git clone https://github.com/your-username/Antarbhukti-LLM.git
cd Antarbhukti-LLM
```

2. Create a virtual environment (optional but recommended):
```sh
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies and package:
```sh
pip install -r requirements.txt
pip install -e .
```

4. (Optional) Set up environment variables and system dependencies:
```sh
python setup_helper.py
```

5. Configure your Azure OpenAI credentials:
```sh
# Edit .env with your Azure OpenAI credentials
nano .env  # or use your preferred editor
```

### Manual Setup (Alternative)

If you prefer to set up manually without using `setup_helper.py`:

1. Create environment file:
```sh
cp .env.template .env
# Edit .env with your Azure OpenAI credentials
```

2. Install Graphviz (for visualization features):
```sh
# macOS
brew install graphviz

# Ubuntu/Debian
sudo apt-get install graphviz

# CentOS/RHEL
sudo yum install graphviz

# Windows
# Download and install from https://graphviz.org/download/
```

### Environment Management

If you used conda to install:

```sh
# Activate the environment
conda activate antarbhukti

# Deactivate the environment
conda deactivate

# Update environment from file
conda env update -f environment.yml

# Remove environment
conda env remove -n antarbhukti
```

### Local Development & Testing

After installation, you can run the test suite locally:

```sh
# Run all tests
pytest

# Run tests with coverage
pytest --cov=src --cov-report=term-missing

# Run specific test files
pytest tests/test_sfc.py

# Run with verbose output
pytest -v

# Run linting checks
flake8 src/ tests/
black --check src/ tests/
isort --check-only src/ tests/

# Auto-format code
black src/ tests/
isort src/ tests/
```

### Usage

**Basic verification:**
```sh
cd examples
python driver.py
```

**Example with custom SFC files:**
```sh
python examples/driver.py
# Edit the driver.py file to specify your SFC files
```

**Run example usage:**
```sh
python examples/example_usage.py
```

---

## OSCAT Benchmarks

AntarBhukti has been tested on all 80 OSCAT automation benchmarks for robust and reliable verification.

---

## Reference

- For Structured Text (ST) code for the OSCAT library, see the [SamaTulyata4PLC](https://github.com/soumyadipcsis/SamaTulyata4PLC) repository.

---

## License

MIT License

Copyright (c) 2025 soumyadipcsis

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

---

## Acknowledgements

- Inspired by the need for robust SFC verification in industrial automation.
- Thanks to the OSCAT project and the verifaps tool for foundational ideas.
