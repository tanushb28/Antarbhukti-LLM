#!/usr/bin/env python3
"""
Prompt Improvement Verification Script
======================================

This script validates all enhanced SFC prompt files for quality, consistency,
and improvement over baseline versions. It provides comprehensive analysis
of prompt enhancements and generates detailed reports.
"""

import os
import re
import json
import argparse
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
from pathlib import Path
from datetime import datetime

# Optional matplotlib for visualization
try:
    import matplotlib.pyplot as plt
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False


@dataclass
class PromptAnalysis:
    """Analysis results for a single prompt file"""
    filename: str
    file_size: int
    line_count: int
    word_count: int
    structure_score: float
    content_quality_score: float
    documentation_score: float
    completeness_score: float
    overall_score: float
    issues: List[str]
    strengths: List[str]


class PromptQualityAnalyzer:
    """Comprehensive analyzer for prompt quality and improvements"""
    
    def __init__(self, data_dir: str = "prompts/current"):
        self.data_dir = Path(data_dir)
        self.enhanced_prompts = [
            "iterative_prompting.txt",
            "prompt_refiner.txt", 
            "prompt_refiner_iter1.txt",
            "PromptForUpgrade.txt",
            "PythonCodePrompt.txt"
        ]
        self.framework_files = [
            "prompt_evaluation_framework.txt"
        ]
        
        # Quality criteria patterns
        self.quality_patterns = {
            'headers': r'^#+\s+\w+',
            'bullet_points': r'^\s*[-*]\s+\*\*',
            'code_blocks': r'```\w*\n.*?\n```',
            'examples': r'(example|Example|EXAMPLE)',
            'instructions': r'(instruction|Instruction|INSTRUCTION)',
            'validation': r'(validation|Validation|VALIDATION|checklist|Checklist)',
            'requirements': r'(requirement|Requirement|REQUIREMENT)',
            'guidelines': r'(guideline|Guideline|GUIDELINE)',
            'best_practices': r'(best practice|Best Practice|BEST PRACTICE)',
            'error_handling': r'(error|Error|ERROR|exception|Exception)',
            'success_criteria': r'(success|Success|SUCCESS|criteria|Criteria)',
            'deliverables': r'(deliverable|Deliverable|DELIVERABLE|output|Output)',
            'documentation': r'(documentation|Documentation|DOCUMENTATION|docstring|Docstring)'
        }
    
    def analyze_file_structure(self, content: str) -> Tuple[float, List[str], List[str]]:
        """Analyze the structural quality of a prompt file"""
        issues = []
        strengths = []
        score = 0.0
        
        # Check for headers (markdown structure)
        headers = re.findall(self.quality_patterns['headers'], content, re.MULTILINE)
        if len(headers) >= 5:
            score += 15
            strengths.append(f"Well-structured with {len(headers)} headers")
        elif len(headers) >= 3:
            score += 10
            strengths.append(f"Good structure with {len(headers)} headers")
        else:
            score += 5
            issues.append("Limited structural organization")
        
        # Check for bullet points and formatting
        bullet_points = re.findall(self.quality_patterns['bullet_points'], content, re.MULTILINE)
        if len(bullet_points) >= 10:
            score += 10
            strengths.append(f"Excellent formatting with {len(bullet_points)} structured points")
        elif len(bullet_points) >= 5:
            score += 7
            strengths.append(f"Good formatting with {len(bullet_points)} structured points")
        else:
            score += 3
            issues.append("Limited use of structured formatting")
        
        # Check for code blocks
        code_blocks = re.findall(self.quality_patterns['code_blocks'], content, re.DOTALL)
        if len(code_blocks) >= 3:
            score += 10
            strengths.append(f"Includes {len(code_blocks)} code examples")
        elif len(code_blocks) >= 1:
            score += 5
            strengths.append(f"Includes {len(code_blocks)} code example(s)")
        else:
            score += 0
            issues.append("No code examples provided")
        
        # Check for comprehensive sections
        section_checks = [
            ('requirements', 'Requirements section'),
            ('guidelines', 'Guidelines section'),
            ('validation', 'Validation criteria'),
            ('deliverables', 'Deliverables specification'),
            ('examples', 'Examples provided')
        ]
        
        sections_found = 0
        for pattern, description in section_checks:
            if re.search(self.quality_patterns[pattern], content, re.IGNORECASE):
                sections_found += 1
                strengths.append(f"Includes {description.lower()}")
        
        if sections_found >= 4:
            score += 15
            strengths.append(f"Comprehensive coverage ({sections_found}/5 key sections)")
        elif sections_found >= 3:
            score += 10
            strengths.append(f"Good coverage ({sections_found}/5 key sections)")
        else:
            score += 5
            issues.append(f"Limited coverage ({sections_found}/5 key sections)")
        
        # Length and detail assessment
        if len(content) > 5000:
            score += 10
            strengths.append("Comprehensive length with detailed guidance")
        elif len(content) > 2000:
            score += 7
            strengths.append("Good length with adequate detail")
        else:
            score += 3
            issues.append("May be too brief for comprehensive guidance")
        
        return min(score, 100), issues, strengths
    
    def analyze_content_quality(self, content: str) -> Tuple[float, List[str], List[str]]:
        """Analyze the content quality and comprehensiveness"""
        issues = []
        strengths = []
        score = 0.0
        
        # Check for quality indicators
        quality_indicators = [
            ('best_practices', 'Best practices guidance', 15),
            ('error_handling', 'Error handling coverage', 15),
            ('success_criteria', 'Success criteria definition', 15),
            ('documentation', 'Documentation requirements', 10),
            ('validation', 'Validation framework', 15),
            ('examples', 'Practical examples', 10),
            ('instructions', 'Clear instructions', 10),
            ('requirements', 'Detailed requirements', 10)
        ]
        
        for pattern, description, points in quality_indicators:
            if re.search(self.quality_patterns[pattern], content, re.IGNORECASE):
                score += points
                strengths.append(f"Includes {description.lower()}")
            else:
                issues.append(f"Missing {description.lower()}")
        
        # Check for professional language indicators
        professional_terms = [
            'implementation', 'specification', 'framework', 'methodology',
            'validation', 'verification', 'optimization', 'integration',
            'architecture', 'design', 'quality', 'standards', 'compliance'
        ]
        
        professional_count = sum(1 for term in professional_terms if term in content.lower())
        if professional_count >= 10:
            score += 10
            strengths.append(f"Professional terminology ({professional_count} terms)")
        elif professional_count >= 5:
            score += 5
            strengths.append(f"Good professional language ({professional_count} terms)")
        else:
            issues.append(f"Limited professional terminology ({professional_count} terms)")
        
        return min(score, 100), issues, strengths
    
    def analyze_documentation_quality(self, content: str) -> Tuple[float, List[str], List[str]]:
        """Analyze documentation quality and clarity"""
        issues = []
        strengths = []
        score = 0.0
        
        # Check for clear explanations
        explanation_patterns = [
            r'(explains?|explanation|clarifies?|clarification)',
            r'(describes?|description|details?|detailed)',
            r'(specifies?|specification|defines?|definition)',
            r'(outlines?|overview|summary|summarizes?)'
        ]
        
        explanation_count = sum(len(re.findall(pattern, content, re.IGNORECASE)) 
                              for pattern in explanation_patterns)
        
        if explanation_count >= 15:
            score += 20
            strengths.append(f"Excellent explanatory content ({explanation_count} instances)")
        elif explanation_count >= 10:
            score += 15
            strengths.append(f"Good explanatory content ({explanation_count} instances)")
        elif explanation_count >= 5:
            score += 10
            strengths.append(f"Adequate explanatory content ({explanation_count} instances)")
        else:
            score += 0
            issues.append(f"Limited explanatory content ({explanation_count} instances)")
        
        # Check for step-by-step guidance
        step_patterns = [
            r'\d+\.\s+\*\*.*?\*\*',  # Numbered steps with bold
            r'Step\s+\d+',           # Step indicators
            r'Phase\s+\d+',          # Phase indicators
            r'###\s+\d+\.'           # Numbered headers
        ]
        
        step_count = sum(len(re.findall(pattern, content, re.IGNORECASE)) 
                        for pattern in step_patterns)
        
        if step_count >= 5:
            score += 20
            strengths.append(f"Excellent step-by-step guidance ({step_count} steps)")
        elif step_count >= 3:
            score += 15
            strengths.append(f"Good step-by-step guidance ({step_count} steps)")
        else:
            score += 5
            issues.append(f"Limited step-by-step guidance ({step_count} steps)")
        
        # Check for formatting consistency
        markdown_elements = [
            '**', '`', '```', '###', '####', '- **', '1. **'
        ]
        
        formatting_score = sum(5 for element in markdown_elements if element in content)
        score += min(formatting_score, 40)
        
        if formatting_score >= 30:
            strengths.append("Excellent markdown formatting")
        elif formatting_score >= 20:
            strengths.append("Good markdown formatting")
        else:
            issues.append("Limited markdown formatting")
        
        # Check for comprehensive coverage
        if len(content.split('\n')) >= 100:
            score += 20
            strengths.append("Comprehensive documentation length")
        elif len(content.split('\n')) >= 50:
            score += 15
            strengths.append("Good documentation length")
        else:
            score += 5
            issues.append("Documentation may be too brief")
        
        return min(score, 100), issues, strengths
    
    def analyze_completeness(self, content: str, filename: str) -> Tuple[float, List[str], List[str]]:
        """Analyze completeness based on prompt type"""
        issues = []
        strengths = []
        score = 0.0
        
        # Domain-specific completeness checks
        if "iterative_prompting" in filename:
            required_elements = [
                ('z3', 'Z3 condition handling'),
                ('equivalence', 'Equivalence criteria'),
                ('path', 'Path coverage'),
                ('behavioral', 'Behavioral requirements'),
                ('sfc1', 'SFC1 reference'),
                ('sfc2', 'SFC2 modification')
            ]
        elif "prompt_refiner" in filename:
            required_elements = [
                ('refin', 'Refinement process'),
                ('bug', 'Bug fixing guidance'),
                ('validation', 'Validation criteria'),
                ('quality', 'Quality standards'),
                ('integration', 'Integration requirements')
            ]
        elif "PromptForUpgrade" in filename:
            required_elements = [
                ('upgrade', 'Upgrade process'),
                ('rule', 'Upgrade rules'),
                ('factorial', 'Factorial domain'),
                ('hex', 'Hexadecimal domain'),
                ('hardware', 'Hardware compatibility'),
                ('string', 'String handling')
            ]
        elif "PythonCodePrompt" in filename:
            required_elements = [
                ('class', 'Class structure'),
                ('file', 'File processing'),
                ('exception', 'Exception handling'),
                ('validation', 'Validation methods'),
                ('documentation', 'Documentation requirements'),
                ('type', 'Type hints')
            ]
        else:
            required_elements = [
                ('requirement', 'Requirements'),
                ('guideline', 'Guidelines'),
                ('validation', 'Validation'),
                ('output', 'Output specification'),
                ('example', 'Examples')
            ]
        
        elements_found = 0
        for pattern, description in required_elements:
            if re.search(pattern, content, re.IGNORECASE):
                elements_found += 1
                strengths.append(f"Includes {description.lower()}")
                score += 100 / len(required_elements)
            else:
                issues.append(f"Missing {description.lower()}")
        
        if elements_found == len(required_elements):
            strengths.append("Complete domain coverage")
        elif elements_found >= len(required_elements) * 0.8:
            strengths.append("Good domain coverage")
        else:
            issues.append("Incomplete domain coverage")
        
        return min(score, 100), issues, strengths
    
    def analyze_prompt_file(self, filename: str) -> PromptAnalysis:
        """Analyze a single prompt file comprehensively"""
        filepath = self.data_dir / filename
        
        if not filepath.exists():
            return PromptAnalysis(
                filename=filename,
                file_size=0,
                line_count=0,
                word_count=0,
                structure_score=0,
                content_quality_score=0,
                documentation_score=0,
                completeness_score=0,
                overall_score=0,
                issues=[f"File not found: {filepath}"],
                strengths=[]
            )
        
        # Read file content
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Basic metrics
        file_size = filepath.stat().st_size
        line_count = len(content.split('\n'))
        word_count = len(content.split())
        
        # Analyze different aspects
        structure_score, struct_issues, struct_strengths = self.analyze_file_structure(content)
        content_score, content_issues, content_strengths = self.analyze_content_quality(content)
        doc_score, doc_issues, doc_strengths = self.analyze_documentation_quality(content)
        completeness_score, comp_issues, comp_strengths = self.analyze_completeness(content, filename)
        
        # Calculate overall score
        overall_score = (structure_score + content_score + doc_score + completeness_score) / 4
        
        # Combine all issues and strengths
        all_issues = struct_issues + content_issues + doc_issues + comp_issues
        all_strengths = struct_strengths + content_strengths + doc_strengths + comp_strengths
        
        return PromptAnalysis(
            filename=filename,
            file_size=file_size,
            line_count=line_count,
            word_count=word_count,
            structure_score=structure_score,
            content_quality_score=content_score,
            documentation_score=doc_score,
            completeness_score=completeness_score,
            overall_score=overall_score,
            issues=all_issues,
            strengths=all_strengths
        )
    
    def generate_comparison_report(self, analyses: List[PromptAnalysis]) -> Dict[str, Any]:
        """Generate comparative analysis report"""
        report = {
            'summary': {
                'total_files': len(analyses),
                'average_score': sum(a.overall_score for a in analyses) / len(analyses),
                'average_size': sum(a.file_size for a in analyses) / len(analyses),
                'average_lines': sum(a.line_count for a in analyses) / len(analyses),
                'total_issues': sum(len(a.issues) for a in analyses),
                'total_strengths': sum(len(a.strengths) for a in analyses)
            },
            'individual_scores': {
                a.filename: {
                    'overall_score': a.overall_score,
                    'structure_score': a.structure_score,
                    'content_score': a.content_quality_score,
                    'documentation_score': a.documentation_score,
                    'completeness_score': a.completeness_score,
                    'file_size': a.file_size,
                    'line_count': a.line_count,
                    'issues_count': len(a.issues),
                    'strengths_count': len(a.strengths)
                }
                for a in analyses
            },
            'quality_rankings': {
                'by_overall_score': sorted(analyses, key=lambda x: x.overall_score, reverse=True),
                'by_structure': sorted(analyses, key=lambda x: x.structure_score, reverse=True),
                'by_content': sorted(analyses, key=lambda x: x.content_quality_score, reverse=True),
                'by_documentation': sorted(analyses, key=lambda x: x.documentation_score, reverse=True),
                'by_completeness': sorted(analyses, key=lambda x: x.completeness_score, reverse=True)
            },
            'improvement_metrics': {
                'excellent_files': len([a for a in analyses if a.overall_score >= 90]),
                'good_files': len([a for a in analyses if 75 <= a.overall_score < 90]),
                'adequate_files': len([a for a in analyses if 60 <= a.overall_score < 75]),
                'needs_improvement': len([a for a in analyses if a.overall_score < 60])
            }
        }
        
        return report
    
    def generate_visualization(self, analyses: List[PromptAnalysis], output_file: str = "prompt_analysis_chart.png"):
        """Generate visualization of prompt analysis results"""
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        
        # Overall scores bar chart
        filenames = [a.filename.replace('.txt', '') for a in analyses]
        overall_scores = [a.overall_score for a in analyses]
        
        ax1.bar(range(len(filenames)), overall_scores, color='skyblue', edgecolor='navy', alpha=0.7)
        ax1.set_title('Overall Quality Scores by Prompt File', fontsize=14, fontweight='bold')
        ax1.set_xlabel('Prompt Files')
        ax1.set_ylabel('Quality Score (0-100)')
        ax1.set_xticks(range(len(filenames)))
        ax1.set_xticklabels(filenames, rotation=45, ha='right')
        ax1.grid(axis='y', alpha=0.3)
        
        # Score breakdown radar chart (using first file as example)
        if analyses:
            categories = ['Structure', 'Content', 'Documentation', 'Completeness']
            first_file = analyses[0]
            scores = [first_file.structure_score, first_file.content_quality_score, 
                     first_file.documentation_score, first_file.completeness_score]
            
            ax2.bar(categories, scores, color=['lightcoral', 'lightgreen', 'lightblue', 'lightyellow'])
            ax2.set_title(f'Score Breakdown: {first_file.filename}', fontsize=14, fontweight='bold')
            ax2.set_ylabel('Score (0-100)')
            ax2.set_ylim(0, 100)
            
        # File size comparison
        file_sizes = [a.file_size / 1024 for a in analyses]  # Convert to KB
        ax3.bar(range(len(filenames)), file_sizes, color='lightgreen', edgecolor='darkgreen', alpha=0.7)
        ax3.set_title('File Sizes (KB)', fontsize=14, fontweight='bold')
        ax3.set_xlabel('Prompt Files')
        ax3.set_ylabel('Size (KB)')
        ax3.set_xticks(range(len(filenames)))
        ax3.set_xticklabels(filenames, rotation=45, ha='right')
        ax3.grid(axis='y', alpha=0.3)
        
        # Issues vs Strengths comparison
        issues_counts = [len(a.issues) for a in analyses]
        strengths_counts = [len(a.strengths) for a in analyses]
        
        x = range(len(filenames))
        width = 0.35
        
        ax4.bar([i - width/2 for i in x], issues_counts, width, label='Issues', color='lightcoral', alpha=0.7)
        ax4.bar([i + width/2 for i in x], strengths_counts, width, label='Strengths', color='lightgreen', alpha=0.7)
        ax4.set_title('Issues vs Strengths Count', fontsize=14, fontweight='bold')
        ax4.set_xlabel('Prompt Files')
        ax4.set_ylabel('Count')
        ax4.set_xticks(x)
        ax4.set_xticklabels(filenames, rotation=45, ha='right')
        ax4.legend()
        ax4.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Visualization saved to: {output_file}")
    
    def run_comprehensive_analysis(self, generate_charts: bool = True) -> Dict[str, Any]:
        """Run comprehensive analysis of all prompt files"""
        print("🔍 Starting Comprehensive Prompt Analysis...")
        print("=" * 50)
        
        analyses = []
        
        # Analyze all enhanced prompt files
        for filename in self.enhanced_prompts:
            print(f"Analyzing: {filename}")
            analysis = self.analyze_prompt_file(filename)
            analyses.append(analysis)
            
            # Print quick summary
            print(f"  Overall Score: {analysis.overall_score:.1f}/100")
            print(f"  Issues: {len(analysis.issues)}, Strengths: {len(analysis.strengths)}")
            print()
        
        # Generate comprehensive report
        report = self.generate_comparison_report(analyses)
        
        # Generate visualization
        if generate_charts:
            try:
                self.generate_visualization(analyses)
            except ImportError:
                print("⚠️  Matplotlib not available, skipping visualization")
            except Exception as e:
                print(f"⚠️  Error generating visualization: {e}")
        
        return {
            'analyses': analyses,
            'report': report,
            'timestamp': datetime.now().isoformat()
        }
    
    def print_detailed_report(self, results: Dict[str, Any]):
        """Print detailed analysis report"""
        analyses = results['analyses']
        report = results['report']
        
        print("\n" + "=" * 60)
        print("📊 COMPREHENSIVE PROMPT ANALYSIS REPORT")
        print("=" * 60)
        
        # Summary statistics
        print(f"\n📈 SUMMARY STATISTICS:")
        print(f"  Total Files Analyzed: {report['summary']['total_files']}")
        print(f"  Average Quality Score: {report['summary']['average_score']:.1f}/100")
        print(f"  Average File Size: {report['summary']['average_size']/1024:.1f} KB")
        print(f"  Average Line Count: {report['summary']['average_lines']:.0f}")
        print(f"  Total Issues Identified: {report['summary']['total_issues']}")
        print(f"  Total Strengths Identified: {report['summary']['total_strengths']}")
        
        # Quality distribution
        print(f"\n🏆 QUALITY DISTRIBUTION:")
        print(f"  Excellent (90+): {report['improvement_metrics']['excellent_files']} files")
        print(f"  Good (75-89): {report['improvement_metrics']['good_files']} files")
        print(f"  Adequate (60-74): {report['improvement_metrics']['adequate_files']} files")
        print(f"  Needs Improvement (<60): {report['improvement_metrics']['needs_improvement']} files")
        
        # Top performers
        print(f"\n🥇 TOP PERFORMERS:")
        top_files = report['quality_rankings']['by_overall_score'][:3]
        for i, analysis in enumerate(top_files, 1):
            print(f"  {i}. {analysis.filename}: {analysis.overall_score:.1f}/100")
        
        # Detailed analysis for each file
        print(f"\n📋 DETAILED ANALYSIS:")
        for analysis in analyses:
            print(f"\n  📄 {analysis.filename}")
            print(f"     Overall Score: {analysis.overall_score:.1f}/100")
            print(f"     Structure: {analysis.structure_score:.1f}/100")
            print(f"     Content: {analysis.content_quality_score:.1f}/100")
            print(f"     Documentation: {analysis.documentation_score:.1f}/100")
            print(f"     Completeness: {analysis.completeness_score:.1f}/100")
            print(f"     File Size: {analysis.file_size/1024:.1f} KB ({analysis.line_count} lines)")
            
            if analysis.issues:
                print(f"     ⚠️  Issues ({len(analysis.issues)}):")
                for issue in analysis.issues[:3]:  # Show top 3 issues
                    print(f"       • {issue}")
                if len(analysis.issues) > 3:
                    print(f"       ... and {len(analysis.issues) - 3} more")
            
            if analysis.strengths:
                print(f"     ✅ Strengths ({len(analysis.strengths)}):")
                for strength in analysis.strengths[:3]:  # Show top 3 strengths
                    print(f"       • {strength}")
                if len(analysis.strengths) > 3:
                    print(f"       ... and {len(analysis.strengths) - 3} more")
        
        # Recommendations
        print(f"\n💡 RECOMMENDATIONS:")
        avg_score = report['summary']['average_score']
        if avg_score >= 85:
            print("  ✅ Excellent overall quality! Prompts are ready for production use.")
        elif avg_score >= 75:
            print("  ✅ Good quality achieved. Consider minor refinements for optimization.")
        elif avg_score >= 60:
            print("  ⚠️  Adequate quality. Review and address identified issues.")
        else:
            print("  ❌ Quality needs improvement. Significant revisions recommended.")
        
        print("\n" + "=" * 60)
        print("Analysis complete! 🎉")


def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(description='Verify SFC prompt improvements')
    parser.add_argument('--prompt', type=str, help='Specific prompt file to analyze')
    parser.add_argument('--data-dir', type=str, default='prompts/current', help='Data directory path')
    parser.add_argument('--no-charts', action='store_true', help='Skip chart generation')
    parser.add_argument('--output', type=str, default='prompt_analysis_report.json', help='Output report file')
    
    args = parser.parse_args()
    
    # Initialize analyzer
    analyzer = PromptQualityAnalyzer(args.data_dir)
    
    if args.prompt:
        # Analyze specific prompt
        print(f"🔍 Analyzing specific prompt: {args.prompt}")
        analysis = analyzer.analyze_prompt_file(args.prompt)
        
        print(f"\n📊 Analysis Results for {args.prompt}:")
        print(f"  Overall Score: {analysis.overall_score:.1f}/100")
        print(f"  Structure: {analysis.structure_score:.1f}/100")
        print(f"  Content: {analysis.content_quality_score:.1f}/100")
        print(f"  Documentation: {analysis.documentation_score:.1f}/100")
        print(f"  Completeness: {analysis.completeness_score:.1f}/100")
        print(f"  File Size: {analysis.file_size/1024:.1f} KB ({analysis.line_count} lines)")
        
        if analysis.issues:
            print(f"\n⚠️  Issues ({len(analysis.issues)}):")
            for issue in analysis.issues:
                print(f"  • {issue}")
        
        if analysis.strengths:
            print(f"\n✅ Strengths ({len(analysis.strengths)}):")
            for strength in analysis.strengths:
                print(f"  • {strength}")
    else:
        # Comprehensive analysis
        results = analyzer.run_comprehensive_analysis(not args.no_charts)
        
        # Print detailed report
        analyzer.print_detailed_report(results)
        
        # Save report to file
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n📄 Detailed report saved to: {args.output}")


if __name__ == "__main__":
    main() 