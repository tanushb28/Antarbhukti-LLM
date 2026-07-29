FROM python:3.10-slim

WORKDIR /app

# Install system-level dependencies (mirrors packages.txt)
RUN apt-get update && apt-get install -y \
    cmake \
    g++ \
    build-essential \
    libz3-dev \
    graphviz \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application source
COPY . .

# Install the Antarbhukti package in editable mode.
# If this fails in some environments, the PYTHONPATH fallback below ensures the app still works.
RUN pip install -e . || echo "Editable install skipped; using PYTHONPATH."

# Ensure the core library is always importable regardless of editable install outcome
ENV PYTHONPATH="/app/src:${PYTHONPATH}"

# SECURITY: The real config.json with API keys must NOT be baked into the image.
# Reviewers must supply LLM credentials at runtime via environment variables, which
# are picked up by app.py via Streamlit Secrets or the BENCHMARK_CSV_PATH mechanism.
# See ARTEFACT_EVALUATION.md for instructions.

# Expose the Streamlit default port
EXPOSE 8501

# Health-check to confirm the app is running
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Launch the Streamlit application
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
