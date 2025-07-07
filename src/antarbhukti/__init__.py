"""
AntarBhukti - A verification tool for evolving Sequential Function Charts (SFCs)

This package provides tools for verifying changes between two versions of SFCs,
specifically tailored for OSCAT application benchmarks.
"""

__version__ = "1.0.0"
__author__ = "soumyadipcsis"
__email__ = "soumyadip.csis@gmail.com"

from .genreport import GenReport
from .llm_manager import LLM_Mgr
# Main exports
from .sfc import SFC
from .sfc_verifier import Verifier

__all__ = [
    "SFC",
    "Verifier",
    "GenReport",
    "LLM_Mgr",
]
