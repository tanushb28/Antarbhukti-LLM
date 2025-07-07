import re
import ast
from typing import List, Dict, Tuple, Optional

class SFC:
    """Sequential Function Chart (SFC) class for extracting and managing SFC data."""
    
    def __init__(self):
        self.steps: List[Dict[str, str]] = []
        self.transitions: List[Dict[str, str]] = []
        self.variables: List[str] = []
        self.initial_step: str = ""
        self.filename: str = ""
    
    def load(self, filename: str):
        """
        Extract steps and transitions from an SFC file.
        
        Args:
            filename: Path to the SFC text file
            
        Returns:
            Tuple containing (steps, transitions) where both are List[Dict[str, str]]
            
        Raises:
            FileNotFoundError: If the specified file doesn't exist
            ValueError: If the file format is invalid or parsing fails
        """
        
        try:
            # Read the SFC file
            with open(filename, 'r', encoding='utf-8') as file:
                content = file.read()
            self.filename = filename
            
            # Extract steps - List[Dict[str, str]]
            steps_match = re.search(r'steps\d*\s*=\s*(\[.*?\])', content, re.DOTALL)
            if steps_match:
                self.steps = ast.literal_eval(steps_match.group(1))
            else:
                self.steps = []
                print("Warning: No steps found in the file")
            
            # Extract transitions - List[Dict[str, str]]  
            transitions_match = re.search(r'transitions\d*\s*=\s*(\[.*?\])', content, re.DOTALL)
            if transitions_match:
                self.transitions = ast.literal_eval(transitions_match.group(1))
            else:
                self.transitions = []
                print("Warning: No transitions found in the file")

            # Extract variables - List[Dict[str, str]]
            variables_match = re.search(r'variables\s*=\s*(\[.*?\])', content)
            if variables_match:
                self.variables = ast.literal_eval(variables_match.group(1))
            else:
                self.variables = []
            
             # Extract initial step
            initial_step_match = re.search(r'initial_step\s*=\s*["\']([^"\']+)["\']', content)
            if initial_step_match:
                self.initial_step = initial_step_match.group(1)
                
            # Verify the extracted data
            self._verify_data()
            
        except FileNotFoundError:
            raise FileNotFoundError(f"File '{filename}' not found")
        except Exception as e:
            raise ValueError(f"Error parsing SFC file '{filename}': {str(e)}")
    
    def _verify_data(self) -> None:
        """Verify that extracted data has the correct types."""
        
        # Verify steps type
        if not isinstance(self.steps, list):
            raise ValueError("Steps must be a list")
        
        for i, step in enumerate(self.steps):
            if not isinstance(step, dict):
                raise ValueError(f"Step {i+1} must be a dictionary")
            for key, value in step.items():
                if not isinstance(key, str) or not isinstance(value, str):
                    raise ValueError(f"Step {i+1}: All keys and values must be strings")
        
        # Verify transitions type
        if not isinstance(self.transitions, list):
            raise ValueError("Transitions must be a list")
            
        for i, transition in enumerate(self.transitions):
            if not isinstance(transition, dict):
                raise ValueError(f"Transition {i+1} must be a dictionary")
            for key, value in transition.items():
                if not isinstance(key, str) or not isinstance(value, str):
                    raise ValueError(f"Transition {i+1}: All keys and values must be strings")
    
    def display_extracted_data(self) -> None:
        """Display the extracted SFC data in a formatted way."""
        
        print(f"📁 Extracted from file: {self.filename}")
        print("="*60)
        
        print("STEPS:")
        if self.steps:
            for i, step in enumerate(self.steps):
                print(f"  {i+1}. {step}")
        else:
            print("  No steps found")
        
        print("\nTRANSITIONS:")
        if self.transitions:
            for i, transition in enumerate(self.transitions):
                print(f"  {i+1}. {transition}")
        else:
            print("  No transitions found")
        
        if self.variables:
            print(f"\nVARIABLES: {self.variables}")
        
        if self.initial_step:
            print(f"INITIAL STEP: {self.initial_step}")
        
        print(f"\n📊 Summary:")
        print(f"   Steps: {len(self.steps)} items (type: {type(self.steps)})")
        print(f"   Transitions: {len(self.transitions)} items (type: {type(self.transitions)})")
    
    def get_steps(self) -> List[Dict[str, str]]:
        """Get the extracted steps."""
        return self.steps
    
    def get_transitions(self) -> List[Dict[str, str]]:
        """Get the extracted transitions."""
        return self.transitions
    
    def get_variables(self) -> List[str]:
        """Get the extracted variables."""
        return self.variables
    
    def get_initial_step(self) -> str:
        """Get the initial step."""
        return self.initial_step
    
    def step_names(self):
         return [step["name"] for step in self.steps]
    def step_functions(self):
         return {step["name"]: step["function"] for step in self.steps}
    def verify_types(self) -> Tuple[bool, bool, bool, bool]:
        """Verify the types of the extracted data."""
        
        steps_type = isinstance(self.steps, list) and all(isinstance(item, dict) and all(isinstance(k, str) and isinstance(v, str) for k, v in item.items()) for item in self.steps)
        transitions_type = isinstance(self.transitions, list) and all(isinstance(item, dict) and all(isinstance(k, str) and isinstance(v, str) for k, v in item.items()) for item in self.transitions)
        variables_type = isinstance(self.variables, list) and all(isinstance(item, dict) and all(isinstance(k, str) and isinstance(v, str) for k, v in item.items()) for item in self.variables)
        initial_step_type = isinstance(self.initial_step, str)
        
        return steps_type, transitions_type, variables_type, initial_step_type
    
    def save_to_python_file(self, output_filename: str) -> None:
        """Save the extracted data to a Python file."""
        
        with open(output_filename, 'w', encoding='utf-8') as file:
            file.write("# Generated SFC data\n")
            file.write(f"# Extracted from: {self.filename}\n\n")
            
            file.write("steps = [\n")
            for step in self.steps:
                file.write(f"    {step},\n")
            file.write("]\n\n")
            
            file.write("transitions = [\n")
            for transition in self.transitions:
                file.write(f"    {transition},\n")
            file.write("]\n\n")
            
            if self.variables:
                file.write(f"variables = {self.variables}\n\n")
            
            if self.initial_step:
                file.write(f"initial_step = '{self.initial_step}'\n")
        
        print(f"Data saved to: {output_filename}")

# Example usage and testing
if __name__ == "__main__":
    # Create SFC instance
    sfc = SFC()
    
    try:
        # Extract data from file
        sfc.load("dec2hex.txt")
        steps = sfc.get_steps()
        transitions = sfc.get_transitions()
        # Display the results
        sfc.display_extracted_data()
        
        # Access individual components
        print(f"\n Direct access:")
        print(f"Number of steps: {len(sfc.get_steps())}")
        print(f"Number of transitions: {len(sfc.get_transitions())}")
        print(f"Variables: {sfc.get_variables()}")
        print(f"Initial step: {sfc.get_initial_step()}")
        
        # Save to Python file
        sfc.save_to_python_file("extracted_sfc_data.py")
        
        # Type verification
        print(f"\n✅ Type verification:")
        (s,t,v,i)=sfc.verify_types()
        print(f"Steps is List[Dict[str, str]]: {s}")
        print(f"Transitions is List[Dict[str, str]]: {t}")
        print(f"Variables is List[str]: {v}")
        print(f"Initial step is str: {i}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
