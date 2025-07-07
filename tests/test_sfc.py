#!/usr/bin/env python3
"""
Unit tests for the SFC (Sequential Function Chart) module.
Tests cover SFC loading, data extraction, validation, and error handling.
"""

import pytest
import tempfile
import os
from unittest.mock import patch, mock_open

from src.antarbhukti.sfc import SFC


class TestSFC:
    """Test suite for SFC class."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.sfc = SFC()
        
    def test_init(self):
        """Test SFC initialization."""
        assert self.sfc.steps == []
        assert self.sfc.transitions == []
        assert self.sfc.variables == []
        assert self.sfc.initial_step == ""
        assert self.sfc.filename == ""

    def test_load_valid_sfc(self):
        """Test loading a valid SFC file."""
        # Load the test SFC file
        test_file = "tests/test_data/simple_sfc.txt"
        self.sfc.load(test_file)
        
        # Verify loaded data
        assert len(self.sfc.steps) == 3
        assert len(self.sfc.transitions) == 2
        assert len(self.sfc.variables) == 3
        assert self.sfc.initial_step == "Start"
        assert self.sfc.filename == test_file
        
        # Verify specific content
        assert self.sfc.steps[0]["name"] == "Start"
        assert self.sfc.steps[0]["function"] == "counter := 0"
        assert self.sfc.transitions[0]["src"] == "Start"
        assert self.sfc.transitions[0]["tgt"] == "Process"
        assert "counter" in self.sfc.variables

    def test_load_file_not_found(self):
        """Test loading a non-existent file."""
        with pytest.raises(FileNotFoundError):
            self.sfc.load("nonexistent_file.txt")

    def test_load_invalid_format(self):
        """Test loading a file with invalid format."""
        invalid_content = "invalid content without proper format"
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(invalid_content)
            temp_file = f.name
        
        try:
            # Should not raise an exception but handle gracefully
            self.sfc.load(temp_file)
            # Should have empty data for invalid format
            assert len(self.sfc.steps) == 0
            assert len(self.sfc.transitions) == 0
        finally:
            os.unlink(temp_file)

    def test_get_methods(self):
        """Test getter methods."""
        self.sfc.load("tests/test_data/simple_sfc.txt")
        
        steps = self.sfc.get_steps()
        transitions = self.sfc.get_transitions()
        variables = self.sfc.get_variables()
        initial_step = self.sfc.get_initial_step()
        
        assert isinstance(steps, list)
        assert isinstance(transitions, list)
        assert isinstance(variables, list)
        assert isinstance(initial_step, str)
        
        assert len(steps) == 3
        assert len(transitions) == 2
        assert len(variables) == 3
        assert initial_step == "Start"

    def test_step_names(self):
        """Test step_names method."""
        self.sfc.load("tests/test_data/simple_sfc.txt")
        
        step_names = self.sfc.step_names()
        expected_names = ["Start", "Process", "End"]
        
        assert step_names == expected_names

    def test_step_functions(self):
        """Test step_functions method."""
        self.sfc.load("tests/test_data/simple_sfc.txt")
        
        step_functions = self.sfc.step_functions()
        
        assert isinstance(step_functions, dict)
        assert step_functions["Start"] == "counter := 0"
        assert step_functions["Process"] == "counter := counter + 1"
        assert step_functions["End"] == "done := True"

    def test_verify_types(self):
        """Test type verification."""
        self.sfc.load("tests/test_data/simple_sfc.txt")
        
        steps_type, transitions_type, variables_type, initial_step_type = self.sfc.verify_types()
        
        assert steps_type is True
        assert transitions_type is True
        assert variables_type is True
        assert initial_step_type is True

    def test_display_extracted_data(self, capsys):
        """Test display_extracted_data method."""
        self.sfc.load("tests/test_data/simple_sfc.txt")
        
        self.sfc.display_extracted_data()
        
        captured = capsys.readouterr()
        assert "STEPS:" in captured.out
        assert "TRANSITIONS:" in captured.out
        assert "Summary:" in captured.out

    def test_save_to_python_file(self):
        """Test saving SFC data to Python file."""
        self.sfc.load("tests/test_data/simple_sfc.txt")
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            output_file = f.name
        
        try:
            self.sfc.save_to_python_file(output_file)
            
            # Verify file was created and contains expected content
            assert os.path.exists(output_file)
            
            with open(output_file, 'r') as f:
                content = f.read()
                
            assert "steps = [" in content
            assert "transitions = [" in content
            assert "variables = " in content
            assert "initial_step = " in content
            
        finally:
            if os.path.exists(output_file):
                os.unlink(output_file)

    def test_verify_data_invalid_steps(self):
        """Test _verify_data with invalid steps."""
        # Use setattr to bypass type checking
        setattr(self.sfc, 'steps', "invalid_steps")
        
        with pytest.raises(ValueError, match="Steps must be a list"):
            self.sfc._verify_data()

    def test_verify_data_invalid_step_dict(self):
        """Test _verify_data with invalid step dictionary."""
        # Use setattr to bypass type checking
        setattr(self.sfc, 'steps', ["invalid_step"])
        
        with pytest.raises(ValueError, match="Step 1 must be a dictionary"):
            self.sfc._verify_data()

    def test_verify_data_invalid_step_values(self):
        """Test _verify_data with invalid step values."""
        # Use setattr to bypass type checking
        setattr(self.sfc, 'steps', [{"name": "Start", "function": 123}])
        
        with pytest.raises(ValueError, match="Step 1: All keys and values must be strings"):
            self.sfc._verify_data()

    def test_verify_data_invalid_transitions(self):
        """Test _verify_data with invalid transitions."""
        self.sfc.steps = [{"name": "Start", "function": "counter := 0"}]
        # Use setattr to bypass type checking
        setattr(self.sfc, 'transitions', "invalid_transitions")
        
        with pytest.raises(ValueError, match="Transitions must be a list"):
            self.sfc._verify_data()

    def test_empty_sfc_file(self):
        """Test loading an empty SFC file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("")  # Empty file
            temp_file = f.name
        
        try:
            self.sfc.load(temp_file)
            
            # Should handle empty file gracefully
            assert len(self.sfc.steps) == 0
            assert len(self.sfc.transitions) == 0
            assert len(self.sfc.variables) == 0
            assert self.sfc.initial_step == ""
            
        finally:
            os.unlink(temp_file)

    def test_sfc_with_missing_sections(self):
        """Test SFC file with missing sections."""
        content = """
        steps = [
            {"name": "Start", "function": "counter := 0"}
        ]
        # Missing transitions, variables, and initial_step
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(content)
            temp_file = f.name
        
        try:
            self.sfc.load(temp_file)
            
            # Should handle missing sections gracefully
            assert len(self.sfc.steps) == 1
            assert len(self.sfc.transitions) == 0
            assert len(self.sfc.variables) == 0
            assert self.sfc.initial_step == ""
            
        finally:
            os.unlink(temp_file)

    def test_load_with_encoding_error(self):
        """Test loading file with encoding issues."""
        with tempfile.NamedTemporaryFile(mode='wb', suffix='.txt', delete=False) as f:
            # Write invalid UTF-8 bytes
            f.write(b'\xff\xfe\x00\x00invalid utf-8')
            temp_file = f.name
        
        try:
            with pytest.raises(ValueError):
                self.sfc.load(temp_file)
        finally:
            os.unlink(temp_file)


if __name__ == "__main__":
    pytest.main([__file__]) 