#!/usr/bin/env python3
"""
SFC Prompt Testing and Validation Script
========================================

This script provides practical tools to test and compare SFC prompt improvements
with GPT-4, measuring concrete improvements in code quality and task completion.
"""

import json
import time
import re
import ast
import os
from datetime import datetime
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class TestCase:
    """Define a test case for SFC prompt evaluation"""
    name: str
    domain: str  # factorial, dec2hex_r1, dec2hex_r2
    sfc1_code: str
    expected_features: List[str]
    validation_criteria: List[str]
    missing_paths: str = ""


@dataclass
class TestResult:
    """Store results of a single test"""
    test_name: str
    prompt_version: str
    response: str
    scores: Dict[str, float]
    timestamp: str
    execution_time: float
    errors: List[str]


class SFCCodeValidator:
    """Validate SFC code quality and correctness"""
    
    def __init__(self):
        self.syntax_patterns = {
            'steps_format': r'steps\s*=\s*\[.*?\]',
            'transitions_format': r'transitions\s*=\s*\[.*?\]',
            'dict_structure': r'\{\s*["\']name["\']\s*:\s*["\'].*?["\'].*?\}',
            'guard_condition': r'["\']guard["\']\s*:\s*["\'].*?["\']'
        }
    
    def validate_syntax(self, code: str) -> Tuple[bool, List[str]]:
        """Check if the generated code has valid Python syntax"""
        errors = []
        
        try:
            # Try to parse as Python AST
            ast.parse(code)
            return True, []
        except SyntaxError as e:
            errors.append(f"Syntax Error: {e}")
            return False, errors
    
    def validate_sfc_structure(self, code: str) -> Tuple[float, List[str]]:
        """Validate SFC structure compliance (0-100 score)"""
        score = 0.0
        issues = []
        
        # Check for required components
        if 'steps' in code and '=' in code:
            score += 25
        else:
            issues.append("Missing 'steps' definition")
        
        if 'transitions' in code and '=' in code:
            score += 25
        else:
            issues.append("Missing 'transitions' definition")
        
        # Check dictionary structure
        if re.search(self.syntax_patterns['dict_structure'], code, re.DOTALL):
            score += 25
        else:
            issues.append("Invalid dictionary structure")
        
        # Check for proper quoting
        if '"name"' in code or "'name'" in code:
            score += 25
        else:
            issues.append("Missing proper key quoting")
        
        return score, issues
    
    def validate_domain_requirements(self, code: str, domain: str, expected_features: List[str]) -> Tuple[float, List[str]]:
        """Validate domain-specific requirements"""
        score = 0.0
        issues = []
        feature_points = 100.0 / len(expected_features) if expected_features else 0
        
        if domain == "factorial":
            if "temp" in code.lower():
                score += feature_points
            else:
                issues.append("Missing 'temp' variable for loop tracking")
                
            if "cleanup" in code.lower() or "reset" in code.lower():
                score += feature_points
            else:
                issues.append("Missing cleanup mechanism")
        
        elif domain == "dec2hex_r1":
            if "mod 16" in code and "mod 15" not in code:
                score += feature_points
            else:
                issues.append("Incorrect modulo operation (should be mod 16)")
                
            if "float" not in code.lower() and "/" not in code:
                score += feature_points
            else:
                issues.append("Contains floating point operations")
        
        elif domain == "dec2hex_r2":
            if '"Error"' in code or "'Error'" in code:
                score += feature_points
            else:
                issues.append("Missing string-based error handling")
                
            if "HexValue" in code and ("string" in code.lower() or "str" in code.lower()):
                score += feature_points
            else:
                issues.append("HexValue not properly handled as string")
        
        return score, issues


class SFCPromptTester:
    """Main testing framework for SFC prompts"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.validator = SFCCodeValidator()
        self.results = []
        self.test_cases = []
        self.api_key = api_key or ""
        
        # Create test cases
        self._initialize_test_cases()
    
    def _initialize_test_cases(self):
        """Initialize standard test cases"""
        
        # Factorial test case
        factorial_sfc = """
        steps = [
            {"name": "Init", "function": "n := input; result := 1; counter := 1"},
            {"name": "Loop", "function": ""},
            {"name": "Multiply", "function": "result := result * counter; counter := counter + 1"},
            {"name": "End", "function": "output := result"}
        ]
        transitions = [
            {"src": "Init", "tgt": "Loop", "guard": "n > 0"},
            {"src": "Loop", "tgt": "Multiply", "guard": "counter <= n"},
            {"src": "Multiply", "tgt": "Loop", "guard": "counter <= n"},
            {"src": "Loop", "tgt": "End", "guard": "counter > n"}
        ]
        """
        
        self.test_cases.append(TestCase(
            name="factorial_upgrade",
            domain="factorial",
            sfc1_code=factorial_sfc,
            expected_features=["temp variable", "cleanup mechanism"],
            validation_criteria=["loop tracking", "auxiliary reset"]
        ))
        
        # DEC2HEX test case
        dec2hex_sfc = """
        steps = [
            {"name": "Init", "function": "HexValue := 0; TempDecValue := DecValue"},
            {"name": "ConvertLoop", "function": ""},
            {"name": "BuildHex", "function": "TempHex := TempDecValue mod 15; HexValue := HexValue * 16 + TempHex"},
            {"name": "End", "function": ""}
        ]
        transitions = [
            {"src": "Init", "tgt": "ConvertLoop", "guard": "DecValue > 0"},
            {"src": "ConvertLoop", "tgt": "BuildHex", "guard": "TempDecValue > 0"},
            {"src": "BuildHex", "tgt": "End", "guard": "TempDecValue = 0"}
        ]
        """
        
        self.test_cases.append(TestCase(
            name="dec2hex_r1_fix",
            domain="dec2hex_r1",
            sfc1_code=dec2hex_sfc,
            expected_features=["mod 16", "integer only"],
            validation_criteria=["correct modulo", "no floating point"]
        ))
    
    def simulate_gpt4_response(self, prompt: str, test_case: TestCase) -> str:
        """Simulate GPT-4 response (replace with actual API call)"""
        # This is a placeholder - replace with actual OpenAI API call
        # For testing purposes, return a mock response
        
        if test_case.domain == "factorial":
            return """
            steps = [
                {"name": "Init", "function": "n := input; result := 1; counter := 1; temp := 0"},
                {"name": "Loop", "function": "temp := temp + 1"},
                {"name": "Multiply", "function": "result := result * counter; counter := counter + 1"},
                {"name": "Cleanup", "function": "temp := 0"},
                {"name": "End", "function": "output := result"}
            ]
            transitions = [
                {"src": "Init", "tgt": "Loop", "guard": "n > 0"},
                {"src": "Loop", "tgt": "Multiply", "guard": "counter <= n"},
                {"src": "Multiply", "tgt": "Loop", "guard": "counter <= n"},
                {"src": "Loop", "tgt": "Cleanup", "guard": "counter > n"},
                {"src": "Cleanup", "tgt": "End", "guard": "True"}
            ]
            """
        
        elif test_case.domain == "dec2hex_r1":
            return """
            steps = [
                {"name": "Init", "function": "HexValue := 0; TempDecValue := DecValue"},
                {"name": "ConvertLoop", "function": ""},
                {"name": "BuildHex", "function": "TempHex := TempDecValue mod 16; HexValue := HexValue * 16 + TempHex"},
                {"name": "End", "function": ""}
            ]
            transitions = [
                {"src": "Init", "tgt": "ConvertLoop", "guard": "DecValue > 0"},
                {"src": "ConvertLoop", "tgt": "BuildHex", "guard": "TempDecValue > 0"},
                {"src": "BuildHex", "tgt": "End", "guard": "TempDecValue = 0"}
            ]
            """
        
        return "# Generated SFC code would appear here"
    
    def run_single_test(self, prompt_file: str, test_case: TestCase) -> TestResult:
        """Run a single test case"""
        start_time = time.time()
        
        # Load prompt
        with open(prompt_file, 'r') as f:
            prompt = f.read()
        
        # Format prompt with test case data
        # Handle different prompt template formats
        try:
            formatted_prompt = prompt.format(
                sfc1_code=test_case.sfc1_code,
                sfc2_code=test_case.sfc1_code,  # Use sfc1_code for sfc2_code when not available
                non_equiv_paths_str=test_case.missing_paths
            )
        except KeyError:
            # If formatting fails, use the original prompt
            formatted_prompt = prompt
        
        # Get GPT-4 response (simulated)
        response = self.simulate_gpt4_response(formatted_prompt, test_case)
        
        execution_time = time.time() - start_time
        
        # Validate response
        scores = {}
        errors = []
        
        # Syntax validation
        syntax_valid, syntax_errors = self.validator.validate_syntax(response)
        scores['syntax_valid'] = 100.0 if syntax_valid else 0.0
        errors.extend(syntax_errors)
        
        # Structure validation
        structure_score, structure_issues = self.validator.validate_sfc_structure(response)
        scores['structure_score'] = structure_score
        errors.extend(structure_issues)
        
        # Domain validation
        domain_score, domain_issues = self.validator.validate_domain_requirements(
            response, test_case.domain, test_case.expected_features
        )
        scores['domain_score'] = domain_score
        errors.extend(domain_issues)
        
        # Calculate overall score
        scores['overall_score'] = (scores['syntax_valid'] + scores['structure_score'] + scores['domain_score']) / 3
        
        return TestResult(
            test_name=test_case.name,
            prompt_version=os.path.basename(prompt_file),
            response=response,
            scores=scores,
            timestamp=datetime.now().isoformat(),
            execution_time=execution_time,
            errors=errors
        )
    
    def compare_prompts(self, original_prompt: str, improved_prompt: str) -> Dict[str, Any]:
        """Compare two prompt versions across all test cases"""
        results = {
            'original_results': [],
            'improved_results': [],
            'comparison_summary': {}
        }
        
        # Run tests with both prompts
        for test_case in self.test_cases:
            print(f"Testing {test_case.name}...")
            
            # Test original prompt
            original_result = self.run_single_test(original_prompt, test_case)
            results['original_results'].append(original_result)
            
            # Test improved prompt
            improved_result = self.run_single_test(improved_prompt, test_case)
            results['improved_results'].append(improved_result)
        
        # Calculate comparison summary
        results['comparison_summary'] = self._calculate_comparison_summary(
            results['original_results'], 
            results['improved_results']
        )
        
        return results
    
    def _calculate_comparison_summary(self, original: List[TestResult], improved: List[TestResult]) -> Dict[str, Any]:
        """Calculate summary statistics for comparison"""
        summary = {}
        
        # Calculate average scores
        orig_scores = [r.scores['overall_score'] for r in original]
        imp_scores = [r.scores['overall_score'] for r in improved]
        
        summary['average_scores'] = {
            'original': sum(orig_scores) / len(orig_scores),
            'improved': sum(imp_scores) / len(imp_scores)
        }
        
        # Calculate improvement percentage
        if summary['average_scores']['original'] > 0:
            improvement_pct = (
                (summary['average_scores']['improved'] - summary['average_scores']['original']) / 
                summary['average_scores']['original'] * 100
            )
            summary['improvement_percentage'] = improvement_pct
        else:
            summary['improvement_percentage'] = 0
        
        # Error analysis
        orig_errors = sum(len(r.errors) for r in original)
        imp_errors = sum(len(r.errors) for r in improved)
        
        summary['error_analysis'] = {
            'original_errors': orig_errors,
            'improved_errors': imp_errors,
            'error_reduction': orig_errors - imp_errors
        }
        
        return summary
    
    def generate_report(self, results: Dict[str, Any], output_file: str = "sfc_prompt_comparison_report.json"):
        """Generate detailed comparison report"""
        report = {
            'test_metadata': {
                'timestamp': datetime.now().isoformat(),
                'test_cases_count': len(self.test_cases),
                'test_cases': [tc.name for tc in self.test_cases]
            },
            'results': results,
            'recommendations': self._generate_recommendations(results)
        }
        
        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"Report generated: {output_file}")
        return report
    
    def _generate_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []
        summary = results['comparison_summary']
        
        if summary['improvement_percentage'] > 20:
            recommendations.append("✅ Significant improvement detected! Deploy improved prompts.")
        elif summary['improvement_percentage'] > 10:
            recommendations.append("⚠️ Moderate improvement. Consider additional refinements.")
        else:
            recommendations.append("❌ Limited improvement. Review prompt design strategy.")
        
        if summary['error_analysis']['error_reduction'] > 0:
            recommendations.append(f"✅ Error reduction: {summary['error_analysis']['error_reduction']} fewer errors")
        
        return recommendations


def main():
    """Main execution function"""
    print("SFC Prompt Testing Framework")
    print("=" * 40)
    
    # Initialize tester
    tester = SFCPromptTester()
    
    # Determine the correct path based on current working directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(script_dir))
    data_dir = os.path.join(project_root, "data")
    
    # Define prompt files to compare
    # Note: Since original files don't exist, we'll use the enhanced ones for demonstration
    original_prompts = [
        os.path.join(data_dir, "iterative_prompting.txt"),
        os.path.join(data_dir, "prompt_refiner.txt"),
        os.path.join(data_dir, "PromptForUpgrade.txt")
    ]
    
    improved_prompts = [
        os.path.join(data_dir, "iterative_prompting.txt"),
        os.path.join(data_dir, "prompt_refiner.txt"), 
        os.path.join(data_dir, "PromptForUpgrade.txt")
    ]
    
    # Run comparison for each prompt type
    for orig, imp in zip(original_prompts, improved_prompts):
        if os.path.exists(orig) and os.path.exists(imp):
            print(f"\nComparing {orig} vs {imp}")
            
            results = tester.compare_prompts(orig, imp)
            report = tester.generate_report(results, f"report_{os.path.basename(orig)}.json")
            
            # Print quick summary
            summary = results['comparison_summary']
            print(f"Average Score Improvement: {summary['improvement_percentage']:.1f}%")
            print(f"Error Reduction: {summary['error_analysis']['error_reduction']}")
        else:
            print(f"⚠️ Missing files: {orig} or {imp}")
    
    print("\n✅ Testing complete! Check generated report files for detailed analysis.")


if __name__ == "__main__":
    main() 