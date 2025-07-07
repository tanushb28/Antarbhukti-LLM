# AntarBhukti

AntarBhukti is a verification tool for evolving software, designed to verify changes between two versions of SFCs (Sequential Function Charts) — a source and a target. It is specifically tailored for use with OSCAT application benchmarks.

---

## Features

- **Compare SFCs:** Verifies the correctness of software evolution using textual SFC representations.
- **Easy to Use:** Simple command line interface for fast verification tasks.
- **Benchmark Suite:** Works on all 80 OSCAT benchmark applications.  
  - `benchmarks/Benchmark-Source-OSCAT.py` contains the source/original SFCs.  
  - `benchmarks/Benchmarks-Upgrade-OSCAT.py` contains the upgraded/target SFCs.
- **Superior Performance:** Outperforms [verifaps](https://formal.kastel.kit.edu/~weigl/verifaps/index.html) in coverage and flexibility.
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

# 3. Install package and run tests
pip install -e .
pytest
```

## Getting Started

**Core files:**  
- `src/antarbhukti/` - Main library code
- `examples/driver.py` - Example driver script  
- `examples/example_usage.py` - Usage examples
- `benchmarks/` - Benchmark suite
- `data/` - Sample SFC data files
- `setup.py` - Installation script

### Prerequisites

- Python 3.8+
- [Z3 SMT solver](https://github.com/Z3Prover/z3) (Python bindings)
- Azure OpenAI credentials (for LLM features)
- Conda (recommended) or pip for environment management

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

4. Set up environment variables:
```sh
cp .env.template .env
# Edit .env with your Azure OpenAI credentials
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

3. Install dependencies:
```sh
pip install -r requirements.txt
pip install -e .
```

4. Set up environment variables:
```sh
cp .env.template .env
# Edit .env with your Azure OpenAI credentials
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
