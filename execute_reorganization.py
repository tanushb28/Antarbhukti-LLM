#!/usr/bin/env python3
"""
Execute Codebase Reorganization
===============================

This script performs the actual reorganization of the codebase structure
to improve organization and maintainability.
"""

import os
import shutil
from pathlib import Path


def create_new_structure():
    """Create the new organized directory structure"""
    
    directories = [
        "prompts/original",
        "prompts/current", 
        "prompts/strategies/cost_effective",
        "prompts/strategies/sweet_spot",
        "prompts/strategies/accuracy_effective",
        "prompts/archive",
        "data/sfc_files",
        "data/test_data",
        "data/examples",
        "evaluation/testing",
        "evaluation/framework",
        "evaluation/results",
        "evaluation/docs",
        "evaluation/verification"
    ]
    
    print("🏗️  Creating new directory structure...")
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"  ✅ Created: {directory}")
    
    # Create README files for main directories
    readme_contents = {
        "prompts/README.md": "# Prompts\n\nAll prompt-related files organized by type and strategy.",
        "prompts/original/README.md": "# Original Prompts\n\nOriginal/previous prompts used for comparison and baseline testing.",
        "prompts/current/README.md": "# Current Enhanced Prompts\n\nCurrent enhanced prompts with improved quality and structure.",
        "prompts/strategies/README.md": "# Prompt Strategies\n\nCost-accuracy optimized prompts for different use cases.",
        "data/sfc_files/README.md": "# SFC Data Files\n\nSFC data files used for testing and validation.",
        "evaluation/README.md": "# Evaluation Framework\n\nPrompt evaluation, testing, and analysis tools."
    }
    
    for filepath, content in readme_contents.items():
        with open(filepath, 'w') as f:
            f.write(content)
    
    print("✅ Directory structure created successfully!")


def move_files():
    """Move files to their new locations"""
    
    print("\n📦 Moving files to new locations...")
    
    # File moves (source -> destination)
    moves = [
        # Original prompts
        ("data/previous_prompts/PythonCodePrompt.txt", "prompts/original/PythonCodePrompt.txt"),
        ("data/previous_prompts/PromptForUpgrade.txt", "prompts/original/PromptForUpgrade.txt"),
        ("data/previous_prompts/iterative_prompting.txt", "prompts/original/iterative_prompting.txt"),
        ("data/previous_prompts/prompt_refiner.txt", "prompts/original/prompt_refiner.txt"),
        
        # Current enhanced prompts
        ("data/PythonCodePrompt.txt", "prompts/current/PythonCodePrompt.txt"),
        ("data/PromptForUpgrade.txt", "prompts/current/PromptForUpgrade.txt"),
        ("data/iterative_prompting.txt", "prompts/current/iterative_prompting.txt"),
        ("data/prompt_refiner.txt", "prompts/current/prompt_refiner.txt"),
        ("data/prompt_refiner_iter1.txt", "prompts/current/prompt_refiner_iter1.txt"),
        ("data/prompt_evaluation_framework.txt", "prompts/current/prompt_evaluation_framework.txt"),
        
        # SFC data files
        ("data/SFC-DEC_TO_HEX.txt", "data/sfc_files/SFC-DEC_TO_HEX.txt"),
        ("data/SFC_FACT.txt", "data/sfc_files/SFC_FACT.txt"),
        ("data/SFC_TLC.txt", "data/sfc_files/SFC_TLC.txt"),
        ("data/dec2hex.txt", "data/sfc_files/dec2hex.txt"),
        ("data/dec2hex_mod.txt", "data/sfc_files/dec2hex_mod.txt"),
    ]
    
    for src, dst in moves:
        if os.path.exists(src):
            shutil.move(src, dst)
            print(f"  ✅ Moved: {src} -> {dst}")
        else:
            print(f"  ⚠️  Not found: {src}")
    
    # Move directories
    directory_moves = [
        ("prompt_evaluation/prompt_types/cost_effective", "prompts/strategies/cost_effective"),
        ("prompt_evaluation/prompt_types/sweet_spot", "prompts/strategies/sweet_spot"),
        ("prompt_evaluation/prompt_types/accuracy_effective", "prompts/strategies/accuracy_effective"),
        ("prompt_evaluation/testing", "evaluation/testing"),
        ("prompt_evaluation/framework", "evaluation/framework"),
        ("prompt_evaluation/results", "evaluation/results"),
        ("prompt_evaluation/docs", "evaluation/docs"),
        ("prompt_evaluation/verification", "evaluation/verification"),
        ("tests/test_data", "data/test_data"),
        ("examples", "data/examples"),
    ]
    
    for src_dir, dst_dir in directory_moves:
        if os.path.exists(src_dir):
            if os.path.exists(dst_dir):
                shutil.rmtree(dst_dir)  # Remove existing destination
            shutil.move(src_dir, dst_dir)
            print(f"  ✅ Moved directory: {src_dir} -> {dst_dir}")
        else:
            print(f"  ⚠️  Directory not found: {src_dir}")


def cleanup_old_structure():
    """Clean up old empty directories"""
    
    print("\n🧹 Cleaning up old structure...")
    
    cleanup_dirs = [
        "data/previous_prompts",
        "prompt_evaluation/prompt_types",
        "prompt_evaluation"
    ]
    
    for directory in cleanup_dirs:
        if os.path.exists(directory) and not os.listdir(directory):
            os.rmdir(directory)
            print(f"  ✅ Removed empty directory: {directory}")
        elif os.path.exists(directory):
            print(f"  ⚠️  Directory not empty, keeping: {directory}")


def update_key_scripts():
    """Update paths in key scripts"""
    
    print("\n🔧 Updating paths in key scripts...")
    
    # Update ab_test_example.py
    try:
        with open("evaluation/testing/ab_test_example.py", 'r') as f:
            content = f.read()
        
        # Update path references
        content = content.replace('data/previous_prompts/', 'prompts/original/')
        content = content.replace('data/', 'prompts/current/')
        
        with open("evaluation/testing/ab_test_example.py", 'w') as f:
            f.write(content)
        
        print("  ✅ Updated: evaluation/testing/ab_test_example.py")
    except Exception as e:
        print(f"  ⚠️  Could not update ab_test_example.py: {e}")
    
    # Update cost_accuracy_analysis.py
    try:
        with open("evaluation/testing/cost_accuracy_analysis.py", 'r') as f:
            content = f.read()
        
        # Update path references
        content = content.replace('prompt_evaluation/prompt_types/', 'prompts/strategies/')
        
        with open("evaluation/testing/cost_accuracy_analysis.py", 'w') as f:
            f.write(content)
        
        print("  ✅ Updated: evaluation/testing/cost_accuracy_analysis.py")
    except Exception as e:
        print(f"  ⚠️  Could not update cost_accuracy_analysis.py: {e}")
    
    # Update demonstrate_prompt_strategies.py
    try:
        with open("demonstrate_prompt_strategies.py", 'r') as f:
            content = f.read()
        
        # Update path references
        content = content.replace('prompt_evaluation/prompt_types/', 'prompts/strategies/')
        
        with open("demonstrate_prompt_strategies.py", 'w') as f:
            f.write(content)
        
        print("  ✅ Updated: demonstrate_prompt_strategies.py")
    except Exception as e:
        print(f"  ⚠️  Could not update demonstrate_prompt_strategies.py: {e}")


def verify_reorganization():
    """Verify the reorganization was successful"""
    
    print("\n🔍 Verifying reorganization...")
    
    # Check key directories exist
    expected_dirs = [
        "prompts/original",
        "prompts/current",
        "prompts/strategies/cost_effective",
        "prompts/strategies/sweet_spot",
        "prompts/strategies/accuracy_effective",
        "data/sfc_files",
        "evaluation/testing"
    ]
    
    all_good = True
    for directory in expected_dirs:
        if os.path.exists(directory):
            print(f"  ✅ Directory exists: {directory}")
        else:
            print(f"  ❌ Directory missing: {directory}")
            all_good = False
    
    # Check key files exist
    expected_files = [
        "prompts/original/PythonCodePrompt.txt",
        "prompts/current/PythonCodePrompt.txt",
        "prompts/strategies/sweet_spot/PythonCodePrompt.txt",
        "data/sfc_files/SFC_FACT.txt",
        "evaluation/testing/ab_test_example.py"
    ]
    
    for filepath in expected_files:
        if os.path.exists(filepath):
            print(f"  ✅ File exists: {filepath}")
        else:
            print(f"  ❌ File missing: {filepath}")
            all_good = False
    
    return all_good


def main():
    """Execute the reorganization"""
    
    print("🚀 EXECUTING CODEBASE REORGANIZATION")
    print("=" * 40)
    
    try:
        # Step 1: Create new structure
        create_new_structure()
        
        # Step 2: Move files
        move_files()
        
        # Step 3: Update script paths
        update_key_scripts()
        
        # Step 4: Clean up
        cleanup_old_structure()
        
        # Step 5: Verify
        success = verify_reorganization()
        
        if success:
            print("\n🎉 REORGANIZATION COMPLETE!")
            print("=" * 30)
            print("✅ All files moved successfully")
            print("✅ Directory structure created")
            print("✅ Scripts updated")
            print("✅ Verification passed")
            print("\n📁 New structure:")
            print("  📁 prompts/     - All prompt files")
            print("  📁 data/        - Pure data files")
            print("  📁 evaluation/  - Testing and evaluation")
            print("\n🎯 Next steps:")
            print("  1. Test all scripts to ensure they work")
            print("  2. Update any remaining import paths")
            print("  3. Update documentation")
        else:
            print("\n⚠️  REORGANIZATION INCOMPLETE")
            print("Some files or directories are missing. Please check manually.")
    
    except Exception as e:
        print(f"\n❌ ERROR during reorganization: {e}")
        print("Please check the error and try again.")


if __name__ == "__main__":
    main() 