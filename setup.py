#!/usr/bin/env python3
"""
Setup script for AntarBhukti

This script configures the AntarBhukti SFC verification tool for installation.
"""

import os

from setuptools import find_packages, setup

# Read the contents of your README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Read requirements from requirements.txt


def parse_requirements(filename):
    """Parse requirements from requirements.txt file."""
    with open(filename, 'r') as f:
        return [line.strip() for line in f
                if line.strip() and not line.startswith('#')]


requirements = parse_requirements('requirements.txt')

setup(
    name="antarbhukti",
    version="1.0.0",
    author="AntarBhukti Team",
    author_email="your-email@example.com",
    description="SFC verification tool using LLM for sequential function charts",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/Antarbhukti-LLM",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-mock>=3.10.0",
            "flake8>=6.0.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "mypy>=1.0.0",
        ],
        "security": [
            "bandit>=1.7.0",
            "safety>=2.3.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "antarbhukti=antarbhukti.sfc:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
