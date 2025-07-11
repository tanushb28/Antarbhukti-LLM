#!/usr/bin/env python3
"""
Example usage of the Containment Checker tool

This script demonstrates how to:
1. Create SFC instances from the benchmark examples
2. Convert SFCs to Petri nets
3. Visualize SFCs and Petri nets
4. Perform basic containment checking

Prerequisites:
- Install dependencies: pip install -r requirements.txt
- Install Graphviz for visualization
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from benchmarks.Benchmarks import sfc_examples
from antarbhukti.genreport import GenReport
from antarbhukti.sfc import SFC
from antarbhukti.sfc_verifier import Verifier


def create_factorial_sfc():
    """Create a factorial computation SFC example"""
    steps = [
        {"name": "Start", "function": "i := 1; fact := 1"},
        {"name": "Check", "function": ""},
        {"name": "Multiply", "function": "fact := fact * i"},
        {"name": "Increment", "function": "i := i + 1"},
        {"name": "End", "function": ""}
    ]

    transitions = [
        {"src": "Start", "tgt": "Check", "guard": "init"},
        {"src": "Check", "tgt": "Multiply", "guard": "i <= n"},
        {"src": "Multiply", "tgt": "Increment", "guard": "True"},
        {"src": "Increment", "tgt": "Check", "guard": "True"},
        {"src": "Check", "tgt": "End", "guard": "i > n"}
    ]

    sfc = SFC()
    sfc.steps = steps
    sfc.variables = ["i", "fact", "n", "init"]
    sfc.transitions = transitions
    sfc.initial_step = "Start"
    return sfc


def demonstrate_sfc_analysis():
    """Demonstrate SFC analysis and visualization"""
    print("=== Containment Checker Demo ===\n")

    # Create SFC from factorial example
    print("1. Creating factorial SFC...")
    sfc = create_factorial_sfc()
    print(f"   Steps: {[step['name'] for step in sfc.steps]}")
    print(f"   Variables: {sfc.variables}")
    print(f"   Initial step: {sfc.initial_step}")

    # Create verifier and report generator
    verifier = Verifier()
    gen_report = GenReport()

    # Convert to Petri net
    print("\n2. Converting SFC to Petri net...")
    pn = verifier.sfc_to_petrinet(sfc)
    print(f"   Places: {pn['places']}")
    print(f"   Transitions: {pn['transitions']}")
    print(f"   Initial marking: {pn['initial_marking']}")

    # Find cut points
    print("\n3. Finding cut points...")
    cut_points = verifier.find_cut_points(pn)
    print(f"   Cut points: {cut_points}")

    # Generate visualizations
    print("\n4. Generating visualizations...")
    try:
        # SFC visualization
        gen_report.sfc_to_dot(sfc, "factorial_sfc.dot")
        gen_report.dot_to_png("factorial_sfc.dot", "factorial_sfc.png")
        print("   ✓ SFC diagram saved as factorial_sfc.png")

        # Petri net visualization
        gen_report.petrinet_to_dot(pn, "factorial_pn.dot")
        gen_report.dot_to_png("factorial_pn.dot", "factorial_pn.png")
        print("   ✓ Petri net diagram saved as factorial_pn.png")

    except Exception as e:
        print(f"   ⚠ Visualization failed: {e}")
        print("   (Make sure Graphviz is installed)")


def demonstrate_benchmark_examples():
    """Demonstrate using benchmark examples"""
    print("\n=== Benchmark Examples ===\n")

    print("Available benchmark examples:")
    for i, example in enumerate(sfc_examples[:5]):  # Show first 5 examples
        print(
            f"  {i+1}. {len(example['steps'])} steps, {len(example['variables'])} variables")
        print(f"     Variables: {example['variables']}")

    # Use the first example (sum of natural numbers)
    print(f"\nAnalyzing example 1: Sum of first n natural numbers")
    example = sfc_examples[0]

    sfc = SFC()
    sfc.steps = example["steps"]
    sfc.variables = example["variables"]
    sfc.transitions = example["transitions"]
    sfc.initial_step = example["steps"][0]["name"]

    print(f"Steps: {sfc.step_names()}")
    print(f"Initial step: {sfc.initial_step}")

    # Convert to Petri net and analyze
    verifier = Verifier()
    pn = verifier.sfc_to_petrinet(sfc)
    cut_points = verifier.find_cut_points(pn)
    print(f"Cut points: {cut_points}")


def main():
    """Main demo function"""
    print("Containment Checker - Example Usage\n")
    print("This script demonstrates basic functionality of the SFC verification tool.\n")

    try:
        demonstrate_sfc_analysis()
        demonstrate_benchmark_examples()

        print("\n=== Demo Complete ===")
        print("\nNext steps:")
        print("1. Try running: python LLM_Manager.py SFC_FACT.txt")
        print("2. Explore the Benchmarks.py file for more examples")
        print("3. Use Verifier.py for advanced containment checking")
        print("4. Check the generated .png files for visualizations")

    except ImportError as e:
        print(f"Import error: {e}")
        print("Please install required dependencies: pip install -r requirements.txt")
    except Exception as e:
        print(f"Error during demo: {e}")
        print("Please check your installation and try again.")


if __name__ == "__main__":
    main()
