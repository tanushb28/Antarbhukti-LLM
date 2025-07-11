#!/usr/bin/env python3
"""
Codebase Reorganization Script
==============================

This script reorganizes the current scattered file structure into a logical,
well-organized hierarchy that separates prompts, data, and evaluation components.
"""

import os
import shutil
from pathlib import Path


def create_new_structure():
    """Create the new organized directory structure"""
    
    new_structure = {
        "prompts": {
            "original": "Original/previous prompts for comparison",
            "current": "Current enhanced prompts", 
            "strategies": {
                "cost_effective": "Cost-optimized prompts",
                "sweet_spot": "Balanced cost-quality prompts",
                "accuracy_effective": "Maximum quality prompts"
            },
            "archive": "Deprecated or experimental prompts"
        },
        "data": {
            "sfc_files": "SFC data files for testing",
            "test_data": "Test data for evaluation",
            "examples": "Example SFC implementations"
        },
        "evaluation": {
            "testing": "Test scripts and A/B testing",
            "framework": "Evaluation framework",
            "results": "Test results and reports",
            "docs": "Documentation"
        }
    }
    
    def create_dirs(structure, base_path=""):
        """Recursively create directory structure"""
        for key, value in structure.items():
            current_path = os.path.join(base_path, key)
            os.makedirs(current_path, exist_ok=True)
            
            if isinstance(value, dict):
                create_dirs(value, current_path)
            else:
                # Create README in leaf directories
                readme_path = os.path.join(current_path, "README.md")
                with open(readme_path, 'w') as f:
                    f.write(f"# {key.replace('_', ' ').title()}\n\n{value}\n")
    
    create_dirs(new_structure)
    print("✅ New directory structure created!")


def plan_file_migrations():
    """Plan the file migrations"""
    
    migrations = [
        # Move original prompts
        ("data/previous_prompts/", "prompts/original/"),
        
        # Move current enhanced prompts
        ("data/PythonCodePrompt.txt", "prompts/current/PythonCodePrompt.txt"),
        ("data/PromptForUpgrade.txt", "prompts/current/PromptForUpgrade.txt"),
        ("data/iterative_prompting.txt", "prompts/current/iterative_prompting.txt"),
        ("data/prompt_refiner.txt", "prompts/current/prompt_refiner.txt"),
        ("data/prompt_refiner_iter1.txt", "prompts/current/prompt_refiner_iter1.txt"),
        ("data/prompt_evaluation_framework.txt", "prompts/current/prompt_evaluation_framework.txt"),
        
        # Move strategy prompts
        ("prompt_evaluation/prompt_types/cost_effective/", "prompts/strategies/cost_effective/"),
        ("prompt_evaluation/prompt_types/sweet_spot/", "prompts/strategies/sweet_spot/"),
        ("prompt_evaluation/prompt_types/accuracy_effective/", "prompts/strategies/accuracy_effective/"),
        
        # Move SFC data files
        ("data/SFC-DEC_TO_HEX.txt", "data/sfc_files/SFC-DEC_TO_HEX.txt"),
        ("data/SFC_FACT.txt", "data/sfc_files/SFC_FACT.txt"),
        ("data/SFC_TLC.txt", "data/sfc_files/SFC_TLC.txt"),
        ("data/dec2hex.txt", "data/sfc_files/dec2hex.txt"),
        ("data/dec2hex_mod.txt", "data/sfc_files/dec2hex_mod.txt"),
        
        # Move test data
        ("tests/test_data/", "data/test_data/"),
        
        # Move examples
        ("examples/", "data/examples/"),
        
        # Rename and reorganize evaluation
        ("prompt_evaluation/testing/", "evaluation/testing/"),
        ("prompt_evaluation/framework/", "evaluation/framework/"),
        ("prompt_evaluation/results/", "evaluation/results/"),
        ("prompt_evaluation/docs/", "evaluation/docs/"),
        ("prompt_evaluation/verification/", "evaluation/verification/")
    ]
    
    return migrations


def show_proposed_structure():
    """Show the proposed new structure"""
    
    print("🎯 PROPOSED NEW CODEBASE ORGANIZATION:")
    print("=" * 45)
    
    structure = """
📁 Antarbhukti-LLM/
├── 📁 prompts/                    # All prompt-related files
│   ├── 📁 original/               # Previous/original prompts
│   │   ├── PythonCodePrompt.txt
│   │   ├── PromptForUpgrade.txt
│   │   ├── iterative_prompting.txt
│   │   └── prompt_refiner.txt
│   ├── 📁 current/                # Current enhanced prompts
│   │   ├── PythonCodePrompt.txt
│   │   ├── PromptForUpgrade.txt
│   │   ├── iterative_prompting.txt
│   │   └── prompt_refiner.txt
│   ├── 📁 strategies/             # Cost-accuracy optimized prompts
│   │   ├── 📁 cost_effective/
│   │   ├── 📁 sweet_spot/
│   │   └── 📁 accuracy_effective/
│   └── 📁 archive/                # Deprecated prompts
│
├── 📁 data/                       # Pure data files only
│   ├── 📁 sfc_files/              # SFC data files
│   │   ├── SFC-DEC_TO_HEX.txt
│   │   ├── SFC_FACT.txt
│   │   ├── dec2hex.txt
│   │   └── dec2hex_mod.txt
│   ├── 📁 test_data/              # Test data
│   │   ├── simple_sfc.txt
│   │   ├── invalid_sfc.txt
│   │   └── modified_sfc.txt
│   └── 📁 examples/               # Example implementations
│
├── 📁 evaluation/                 # Evaluation and testing
│   ├── 📁 testing/                # Test scripts
│   │   ├── ab_test_example.py
│   │   ├── cost_accuracy_analysis.py
│   │   └── sfc_prompt_tester.py
│   ├── 📁 framework/              # Evaluation framework
│   ├── 📁 results/                # Test results
│   ├── 📁 docs/                   # Documentation
│   └── 📁 verification/           # Verification scripts
│
├── 📁 src/                        # Source code (unchanged)
│   └── 📁 antarbhukti/
│
└── 📁 tests/                      # Unit tests (unchanged)
    """
    
    print(structure)
    
    print("\n🎯 BENEFITS OF NEW ORGANIZATION:")
    print("=" * 35)
    print("✅ **Clear Separation**: Prompts, data, and evaluation separated")
    print("✅ **Easy Discovery**: Find what you need quickly")
    print("✅ **Logical Hierarchy**: Related items grouped together")
    print("✅ **Scalable**: Easy to add new prompt strategies")
    print("✅ **Maintainable**: Clear ownership and responsibilities")
    print("✅ **Professional**: Industry-standard organization")


def update_import_paths():
    """Generate script to update import paths after reorganization"""
    
    path_updates = [
        # Update evaluation scripts
        ("prompt_evaluation/testing/", "evaluation/testing/"),
        ("data/previous_prompts/", "prompts/original/"),
        ("data/", "prompts/current/"),
        ("prompt_evaluation/prompt_types/", "prompts/strategies/"),
    ]
    
    print("\n🔧 FILES THAT NEED PATH UPDATES:")
    print("=" * 35)
    
    files_to_update = [
        "evaluation/testing/ab_test_example.py",
        "evaluation/testing/cost_accuracy_analysis.py",
        "demonstrate_prompt_strategies.py",
        "src/antarbhukti/sfc_verifier.py",
        "Any scripts importing from old paths"
    ]
    
    for file in files_to_update:
        print(f"📝 {file}")
    
    print("\n🎯 Path Update Examples:")
    print("OLD: data/previous_prompts/PythonCodePrompt.txt")
    print("NEW: prompts/original/PythonCodePrompt.txt")
    print()
    print("OLD: prompt_evaluation/prompt_types/sweet_spot/")
    print("NEW: prompts/strategies/sweet_spot/")


def main():
    """Main reorganization planner"""
    
    print("🗂️ CODEBASE REORGANIZATION ANALYSIS")
    print("=" * 40)
    
    # Show current issues
    print("\n❌ CURRENT ISSUES:")
    print("- Prompts scattered across data/ and prompt_evaluation/")
    print("- SFC data files mixed with prompt files")
    print("- Poor discoverability and navigation")
    print("- No clear separation of concerns")
    
    # Show proposed structure
    show_proposed_structure()
    
    # Show update requirements
    update_import_paths()
    
    print("\n🎯 RECOMMENDATION:")
    print("=" * 17)
    print("**REORGANIZE IMMEDIATELY** - This will significantly improve:")
    print("• Code maintainability")
    print("• Developer experience")
    print("• Project scalability")
    print("• Professional appearance")
    
    print("\n💡 IMPLEMENTATION STEPS:")
    print("1. Create new directory structure")
    print("2. Move files to appropriate locations")
    print("3. Update import paths in scripts")
    print("4. Update documentation")
    print("5. Test all functionality")


if __name__ == "__main__":
    main() 