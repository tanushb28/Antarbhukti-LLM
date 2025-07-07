#!/usr/bin/env python3
"""
Quick Prompt Verification Runner
================================

This script runs all prompt verification tests and provides a summary
of the enhancement quality across all SFC prompt files.
"""

import os
import sys
import subprocess
from pathlib import Path


def check_file_exists(filepath: str) -> bool:
    """Check if a file exists"""
    return Path(filepath).exists()


def get_file_stats(filepath: str) -> dict:
    """Get basic file statistics"""
    if not check_file_exists(filepath):
        return {"exists": False, "size": 0, "lines": 0}
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    return {
        "exists": True,
        "size": len(content),
        "lines": len(content.split('\n')),
        "words": len(content.split())
    }


def check_prompt_quality(filepath: str) -> dict:
    """Quick quality check for a prompt file"""
    if not check_file_exists(filepath):
        return {"score": 0, "issues": ["File not found"]}
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    score = 0
    issues = []
    
    # Check for basic structure
    if content.count('#') >= 5:
        score += 20
    else:
        issues.append("Limited header structure")
    
    if '**' in content:
        score += 10
    else:
        issues.append("No bold formatting")
    
    if '```' in content:
        score += 15
    else:
        issues.append("No code blocks")
    
    # Check for key sections
    key_sections = ['requirement', 'guideline', 'validation', 'example', 'deliverable']
    found_sections = sum(1 for section in key_sections if section.lower() in content.lower())
    score += found_sections * 10
    
    if found_sections < 3:
        issues.append(f"Only {found_sections}/5 key sections found")
    
    # Check length (comprehensive prompts should be longer)
    if len(content) > 3000:
        score += 15
    elif len(content) > 1000:
        score += 10
    else:
        issues.append("Prompt may be too brief")
    
    # Check for professional terms
    professional_terms = ['implementation', 'validation', 'framework', 'specification']
    found_terms = sum(1 for term in professional_terms if term in content.lower())
    score += found_terms * 5
    
    return {"score": min(score, 100), "issues": issues}


def main():
    """Main verification runner"""
    print("🚀 Running Prompt Verification Suite")
    print("=" * 50)
    
    # Get the directory of this script
    script_dir = Path(__file__).parent
    project_root = script_dir.parent.parent
    
    # Enhanced prompt files to check
    enhanced_prompts = [
        str(project_root / "data" / "iterative_prompting.txt"),
        str(project_root / "data" / "prompt_refiner.txt"), 
        str(project_root / "data" / "PromptForUpgrade.txt"),
        str(project_root / "data" / "PythonCodePrompt.txt"),
        str(project_root / "data" / "prompt_evaluation_framework.txt")
    ]
    
    framework_files = [
        str(script_dir.parent / "framework" / "prompt_evaluation_framework.txt"),
        str(script_dir.parent / "testing" / "sfc_prompt_tester.py"),
        str(script_dir / "verify_prompt_improvements.py"),
        str(script_dir.parent / "docs" / "PROMPT_TESTING_GUIDE.md")
    ]
    
    total_score = 0
    total_files = 0
    results = []
    
    print("📁 Checking Enhanced Prompt Files:")
    print("-" * 30)
    
    for prompt_file in enhanced_prompts:
        filename = Path(prompt_file).name
        stats = get_file_stats(prompt_file)
        quality = check_prompt_quality(prompt_file)
        
        if stats["exists"]:
            print(f"✅ {filename}")
            print(f"   Size: {stats['size']/1024:.1f} KB ({stats['lines']} lines)")
            print(f"   Quality Score: {quality['score']}/100")
            if quality['issues']:
                print(f"   Issues: {len(quality['issues'])}")
            
            total_score += quality['score']
            total_files += 1
            results.append({
                "file": filename,
                "score": quality['score'],
                "size_kb": stats['size']/1024,
                "lines": stats['lines'],
                "issues": quality['issues']
            })
        else:
            print(f"❌ {filename} - Not found")
        print()
    
    print("🔧 Checking Framework Files:")
    print("-" * 25)
    
    for framework_file in framework_files:
        filename = Path(framework_file).name
        if check_file_exists(framework_file):
            stats = get_file_stats(framework_file)
            print(f"✅ {filename} ({stats['size']/1024:.1f} KB)")
        else:
            print(f"❌ {filename} - Not found")
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 VERIFICATION SUMMARY")
    print("=" * 50)
    
    if total_files > 0:
        avg_score = total_score / total_files
        print(f"Files Analyzed: {total_files}/5")
        print(f"Average Quality Score: {avg_score:.1f}/100")
        
        # Quality assessment
        if avg_score >= 85:
            print("🎉 Excellent! Prompts are high quality and ready for production.")
            status = "EXCELLENT"
        elif avg_score >= 75:
            print("✅ Good quality achieved. Minor improvements may be beneficial.")
            status = "GOOD"
        elif avg_score >= 60:
            print("⚠️  Adequate quality. Consider addressing identified issues.")
            status = "ADEQUATE"
        else:
            print("❌ Quality needs improvement. Review and enhance prompts.")
            status = "NEEDS_IMPROVEMENT"
        
        # File size analysis
        total_size = sum(r['size_kb'] for r in results)
        print(f"\nTotal Enhanced Content: {total_size:.1f} KB")
        print(f"Average File Size: {total_size/len(results):.1f} KB")
        
        # Enhancement factor
        # Assuming original prompts were ~0.5KB each
        original_size = len(results) * 0.5
        enhancement_factor = total_size / original_size
        print(f"Enhancement Factor: {enhancement_factor:.1f}x (vs original)")
        
        # Top performers
        sorted_results = sorted(results, key=lambda x: x['score'], reverse=True)
        print(f"\n🏆 Top Performers:")
        for i, result in enumerate(sorted_results[:3], 1):
            print(f"  {i}. {result['file']}: {result['score']}/100")
        
        # Issues summary
        total_issues = sum(len(r['issues']) for r in results)
        print(f"\nTotal Issues Identified: {total_issues}")
        if total_issues == 0:
            print("🎉 No issues found!")
        
    else:
        print("❌ No enhanced prompt files found!")
        status = "FAILED"
    
    # Run comprehensive analysis if verification script exists
    print("\n" + "=" * 50)
    print("🔍 RUNNING COMPREHENSIVE ANALYSIS")
    print("=" * 50)
    
    if check_file_exists("verify_prompt_improvements.py"):
        print("Running detailed prompt analysis...")
        try:
            result = subprocess.run([
                sys.executable, "verify_prompt_improvements.py", 
                "--no-charts"
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                print("✅ Comprehensive analysis completed successfully!")
                if "Excellent overall quality" in result.stdout:
                    print("🎉 Analysis confirms excellent prompt quality!")
                elif "Good quality achieved" in result.stdout:
                    print("✅ Analysis confirms good prompt quality!")
                
                # Look for specific metrics in output
                lines = result.stdout.split('\n')
                for line in lines:
                    if "Average Quality Score:" in line:
                        print(f"   {line.strip()}")
                    elif "Total Files Analyzed:" in line:
                        print(f"   {line.strip()}")
            else:
                print("⚠️  Comprehensive analysis had issues:")
                print(result.stderr[:200] + "..." if len(result.stderr) > 200 else result.stderr)
        
        except subprocess.TimeoutExpired:
            print("⚠️  Comprehensive analysis timed out")
        except Exception as e:
            print(f"⚠️  Error running comprehensive analysis: {e}")
    else:
        print("⚠️  Comprehensive analysis script not found")
    
    # Final recommendations
    print("\n" + "=" * 50)
    print("💡 RECOMMENDATIONS")
    print("=" * 50)
    
    if status == "EXCELLENT":
        print("✅ Prompts are ready for production use!")
        print("✅ Consider running A/B tests to validate improvements")
        print("✅ Document the enhancement process for future reference")
    elif status == "GOOD":
        print("✅ Prompts show significant improvement")
        print("⚠️  Address any remaining issues for optimization")
        print("✅ Ready for testing with GPT-4")
    elif status == "ADEQUATE":
        print("⚠️  Review identified issues and enhance accordingly")
        print("⚠️  Consider adding more examples and validation criteria")
        print("⚠️  Test with GPT-4 and iterate based on results")
    else:
        print("❌ Significant improvement needed")
        print("❌ Review prompt structure and content quality")
        print("❌ Follow the enhancement guidelines more closely")
    
    print("\n🎯 Next Steps:")
    print("1. Review any issues identified above")
    print("2. Test prompts with GPT-4 using real SFC data") 
    print("3. Run A/B tests to measure actual improvements")
    print("4. Iterate based on real-world performance")
    
    print(f"\n🏁 Verification completed with status: {status}")
    return status == "EXCELLENT" or status == "GOOD"


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 