# SFC Prompt Testing and Validation Guide

## Overview
This guide explains how to use the SFC Prompt Testing Framework to validate and compare prompt improvements for Sequential Function Chart (SFC) generation tasks.

## Quick Start

### 1. Set Up Testing Environment
```bash
# Ensure you have Python 3.7+ installed
python --version

# Install required packages (if not already installed)
pip install openai  # For actual GPT-4 API integration (optional)
```

### 2. Prepare Your Prompt Files
You'll need both original and improved versions of your prompts:

```
data/
├── iterative_prompting.txt          # Improved version
├── prompt_refiner.txt              # Improved version  
├── PromptForUpgrade.txt            # Improved version
├── iterative_prompting_original.txt # Original version
├── prompt_refiner_original.txt     # Original version
└── PromptForUpgrade_original.txt   # Original version
```

### 3. Run the Testing Framework
```bash
# Run the automated testing
python sfc_prompt_tester.py
```

## Understanding the Results

### Test Metrics Explained

#### 1. **Syntax Validity (0-100)**
- **100**: Code parses correctly as valid Python
- **0**: Code has syntax errors
- **What it measures**: Basic code correctness

#### 2. **Structure Score (0-100)**
- **100**: Perfect SFC format compliance
- **75**: Minor formatting issues
- **50**: Missing some required components
- **0**: Completely wrong format
- **What it measures**: SFC dictionary structure adherence

#### 3. **Domain Score (0-100)**
- **100**: All domain-specific requirements met
- **50**: Some requirements missing
- **0**: No domain requirements addressed
- **What it measures**: Task-specific functionality

#### 4. **Overall Score (0-100)**
- Average of the three scores above
- **90+**: Excellent quality
- **70-89**: Good quality
- **50-69**: Acceptable quality
- **<50**: Needs improvement

### Report Interpretation

#### Sample Report Output:
```json
{
  "comparison_summary": {
    "average_scores": {
      "original": 65.5,
      "improved": 89.2
    },
    "improvement_percentage": 36.2,
    "error_analysis": {
      "original_errors": 8,
      "improved_errors": 2,
      "error_reduction": 6
    }
  },
  "recommendations": [
    "✅ Significant improvement detected! Deploy improved prompts.",
    "✅ Error reduction: 6 fewer errors"
  ]
}
```

#### What This Means:
- **36.2% improvement**: Substantial enhancement in prompt quality
- **6 fewer errors**: Significant reduction in issues
- **Recommendation**: Deploy the improved prompts

## Customizing Tests

### Adding New Test Cases

Edit the `_initialize_test_cases()` method in `sfc_prompt_tester.py`:

```python
def _initialize_test_cases(self):
    # Add your custom test case
    custom_sfc = """
    steps = [
        {"name": "YourStep", "function": "your_function"},
        # ... more steps
    ]
    transitions = [
        {"src": "YourStep", "tgt": "NextStep", "guard": "your_condition"},
        # ... more transitions
    ]
    """
    
    self.test_cases.append(TestCase(
        name="your_test_name",
        domain="your_domain",  # factorial, dec2hex_r1, dec2hex_r2, or custom
        sfc1_code=custom_sfc,
        expected_features=["feature1", "feature2"],
        validation_criteria=["criteria1", "criteria2"]
    ))
```

### Modifying Validation Criteria

Edit the `validate_domain_requirements()` method to add your own domain logic:

```python
elif domain == "your_custom_domain":
    if "your_feature" in code.lower():
        score += feature_points
    else:
        issues.append("Missing your required feature")
```

## Integration with GPT-4

### Using Real GPT-4 API

Replace the `simulate_gpt4_response()` method with actual API calls:

```python
import openai

def call_gpt4_api(self, prompt: str, test_case: TestCase) -> str:
    """Make actual GPT-4 API call"""
    client = openai.OpenAI(api_key=self.api_key)
    
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an expert SFC developer."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=2000,
        temperature=0.1
    )
    
    return response.choices[0].message.content
```

## Best Practices

### 1. **Baseline Testing**
- Always test original prompts first to establish baseline
- Run tests multiple times to account for GPT-4 variability
- Document common failure patterns

### 2. **Iterative Improvement**
- Start with small, targeted improvements
- Test each change systematically
- Keep successful prompt versions for comparison

### 3. **Result Analysis**
- Look for patterns in errors across test cases
- Focus on improvements that address multiple issues
- Validate improvements with domain experts

### 4. **Documentation**
- Keep detailed records of what changes were made
- Document the rationale for each improvement
- Track performance over time

## Troubleshooting

### Common Issues

#### 1. **"Missing files" Error**
```
⚠️ Missing files: data/iterative_prompting_original.txt or data/iterative_prompting.txt
```
**Solution**: Ensure both original and improved prompt files exist in the data directory.

#### 2. **Low Improvement Scores**
**Causes**:
- Prompts may not be significantly different
- Test cases may not cover the improved areas
- Validation criteria may need adjustment

**Solutions**:
- Review the specific improvements made
- Add more targeted test cases
- Adjust validation logic for your domain

#### 3. **Syntax Errors in Generated Code**
**Causes**:
- Prompt instructions may be unclear
- GPT-4 may not understand the required format
- Template variables may not be properly formatted

**Solutions**:
- Simplify prompt instructions
- Add more examples in prompts
- Validate template variable formatting

## Success Metrics

### Target Improvement Thresholds
- **Minimum Success**: 15% improvement over baseline
- **Good Success**: 25% improvement over baseline
- **Excellent Success**: 35%+ improvement over baseline

### Quality Targets
- **Syntax Validity**: 95%+ (few or no syntax errors)
- **Structure Score**: 85%+ (good format compliance)
- **Domain Score**: 80%+ (most requirements met)
- **Overall Score**: 85%+ (high quality output)

## Advanced Usage

### Batch Testing with Multiple Prompts
```python
# Test multiple prompt variations
prompt_variations = [
    "data/prompt_v1.txt",
    "data/prompt_v2.txt", 
    "data/prompt_v3.txt"
]

for prompt_file in prompt_variations:
    results = tester.compare_prompts("data/original.txt", prompt_file)
    # Analyze results
```

### Custom Scoring Functions
```python
def custom_score_calculator(response, test_case):
    """Implement your own scoring logic"""
    score = 0
    
    # Your custom validation logic here
    if "specific_pattern" in response:
        score += 50
    
    return score
```

## Conclusion

This testing framework provides a systematic way to:
1. **Measure prompt improvements objectively**
2. **Compare different prompt versions**
3. **Identify areas for further improvement**
4. **Validate that changes actually improve results**

By using this framework, you can ensure that your prompt improvements lead to measurable, consistent improvements in SFC generation quality.

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the test results and error messages
3. Adjust validation criteria for your specific use case
4. Consider adding more test cases for better coverage 