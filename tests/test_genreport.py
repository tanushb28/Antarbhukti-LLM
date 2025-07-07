#!/usr/bin/env python3
"""
Unit tests for the GenReport module.
Tests cover report generation, visualization, and file operations.
"""

import os
import tempfile
from unittest.mock import Mock, patch

import pytest

from antarbhukti.genreport import GenReport
from antarbhukti.sfc import SFC


class TestGenReport:
    """Test suite for GenReport class."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.gen_report = GenReport()
        self.sfc = SFC()
        self.sfc.load("tests/test_data/simple_sfc.txt")

    def test_init(self):
        """Test GenReport initialization."""
        assert isinstance(self.gen_report, GenReport)

    def test_sfc_to_dot(self):
        """Test SFC to DOT format conversion."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".dot", delete=False) as f:
            dot_file = f.name

        try:
            self.gen_report.sfc_to_dot(self.sfc, dot_file)

            # Verify file was created
            assert os.path.exists(dot_file)

            # Verify content
            with open(dot_file, "r") as f:
                content = f.read()

            assert "digraph SFC" in content
            assert "rankdir=LR" in content
            assert "Start" in content
            assert "Process" in content
            assert "End" in content

        finally:
            if os.path.exists(dot_file):
                os.unlink(dot_file)

    def test_petrinet_to_dot(self):
        """Test Petri net to DOT format conversion."""
        # Create a simple Petri net structure
        pn = {
            "places": ["Start", "Process", "End"],
            "functions": {
                "Start": "counter := 0",
                "Process": "counter := counter + 1",
                "End": "done := True",
            },
            "transitions": ["t_0", "t_1"],
            "transition_guards": {"t_0": "init", "t_1": "counter >= 3"},
            "input_arcs": [("Start", "t_0"), ("Process", "t_1")],
            "output_arcs": [("t_0", "Process"), ("t_1", "End")],
            "initial_marking": ["Start"],
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".dot", delete=False) as f:
            dot_file = f.name

        try:
            self.gen_report.petrinet_to_dot(pn, dot_file)

            # Verify file was created
            assert os.path.exists(dot_file)

            # Verify content
            with open(dot_file, "r") as f:
                content = f.read()

            assert "digraph PN" in content
            assert "rankdir=LR" in content
            assert "Start" in content
            assert "t_0" in content
            assert "t_1" in content

        finally:
            if os.path.exists(dot_file):
                os.unlink(dot_file)

    @patch("subprocess.run")
    def test_dot_to_png_success(self, mock_run):
        """Test successful DOT to PNG conversion."""
        mock_run.return_value = Mock(returncode=0)

        dot_file = "test.dot"
        png_file = "test.png"

        self.gen_report.dot_to_png(dot_file, png_file)

        # Verify subprocess was called with correct arguments
        mock_run.assert_called_once_with(
            ["dot", "-Tpng", dot_file, "-o", png_file], check=True
        )

    @patch("subprocess.run")
    def test_dot_to_png_failure(self, mock_run, capsys):
        """Test DOT to PNG conversion failure."""
        mock_run.side_effect = Exception("Graphviz not found")

        dot_file = "test.dot"
        png_file = "test.png"

        self.gen_report.dot_to_png(dot_file, png_file)

        # Verify error message was printed
        captured = capsys.readouterr()
        assert "Error running Graphviz" in captured.out

    def test_html_escape(self):
        """Test HTML escaping functionality."""
        # Test basic HTML characters
        result = self.gen_report.html_escape("<script>alert('xss')</script>")
        assert "&lt;" in result
        assert "&gt;" in result
        assert "&amp;" not in result or "script" in result

        # Test with quotes
        result = self.gen_report.html_escape('Say "hello"')
        assert "&quot;" in result

        # Test with ampersand
        result = self.gen_report.html_escape("A & B")
        assert "&amp;" in result

    def test_img_to_base64_existing_file(self):
        """Test converting existing image to base64."""
        # Create a temporary file with some content
        with tempfile.NamedTemporaryFile(mode="wb", suffix=".png", delete=False) as f:
            f.write(b"\x89PNG\r\n\x1a\n")  # PNG header
            test_file = f.name

        try:
            result = self.gen_report.img_to_base64(test_file)

            # Verify result is base64 string
            assert isinstance(result, str)
            assert len(result) > 0

            # Verify it's valid base64
            import base64

            try:
                decoded = base64.b64decode(result)
                assert decoded.startswith(b"\x89PNG")
            except Exception:
                pytest.fail("Result is not valid base64")

        finally:
            if os.path.exists(test_file):
                os.unlink(test_file)

    def test_img_to_base64_nonexistent_file(self):
        """Test converting non-existent image to base64."""
        result = self.gen_report.img_to_base64("nonexistent.png")
        assert result is None

    def test_sfc_to_dot_with_complex_functions(self):
        """Test SFC to DOT conversion with complex step functions."""
        # Create SFC with complex functions
        sfc = SFC()
        sfc.steps = [
            {"name": "Init", "function": "counter := 0; result := 'none'"},
            {"name": "Calculate", "function": "result := counter * 2 + 1"},
            {"name": "Finish", "function": "done := True; output := result"},
        ]
        sfc.transitions = [
            {"src": "Init", "tgt": "Calculate", "guard": "start = True"},
            {"src": "Calculate", "tgt": "Finish", "guard": "counter > 0"},
        ]
        sfc.initial_step = "Init"

        with tempfile.NamedTemporaryFile(mode="w", suffix=".dot", delete=False) as f:
            dot_file = f.name

        try:
            self.gen_report.sfc_to_dot(sfc, dot_file)

            # Verify file was created and contains complex functions
            assert os.path.exists(dot_file)

            with open(dot_file, "r") as f:
                content = f.read()

            assert "counter := 0" in content
            assert "result := counter * 2 + 1" in content
            assert "done := True" in content

        finally:
            if os.path.exists(dot_file):
                os.unlink(dot_file)

    def test_sfc_to_dot_with_initial_step_highlighting(self):
        """Test SFC to DOT conversion with initial step highlighting."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".dot", delete=False) as f:
            dot_file = f.name

        try:
            self.gen_report.sfc_to_dot(self.sfc, dot_file)

            # Verify initial step is highlighted
            with open(dot_file, "r") as f:
                content = f.read()

            # Should have fillcolor for initial step
            assert "fillcolor=lightblue" in content

        finally:
            if os.path.exists(dot_file):
                os.unlink(dot_file)

    def test_petrinet_to_dot_with_guards(self):
        """Test Petri net to DOT conversion with transition guards."""
        pn = {
            "places": ["A", "B"],
            "functions": {"A": "x := 1", "B": "y := 2"},
            "transitions": ["t1"],
            "transition_guards": {"t1": "x > 0 && y < 5"},
            "input_arcs": [("A", "t1")],
            "output_arcs": [("t1", "B")],
            "initial_marking": ["A"],
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".dot", delete=False) as f:
            dot_file = f.name

        try:
            self.gen_report.petrinet_to_dot(pn, dot_file)

            # Verify guard is included
            with open(dot_file, "r") as f:
                content = f.read()

            assert "x > 0 && y < 5" in content

        finally:
            if os.path.exists(dot_file):
                os.unlink(dot_file)

    def test_petrinet_to_dot_with_initial_marking(self):
        """Test Petri net to DOT conversion with initial marking highlighting."""
        pn = {
            "places": ["Start", "End"],
            "functions": {"Start": "init", "End": "finish"},
            "transitions": ["t1"],
            "transition_guards": {"t1": "True"},
            "input_arcs": [("Start", "t1")],
            "output_arcs": [("t1", "End")],
            "initial_marking": ["Start"],
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".dot", delete=False) as f:
            dot_file = f.name

        try:
            self.gen_report.petrinet_to_dot(pn, dot_file)

            # Verify initial marking is highlighted
            with open(dot_file, "r") as f:
                content = f.read()

            assert "fillcolor=lightgray" in content

        finally:
            if os.path.exists(dot_file):
                os.unlink(dot_file)

    def test_empty_sfc_to_dot(self):
        """Test SFC to DOT conversion with empty SFC."""
        empty_sfc = SFC()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".dot", delete=False) as f:
            dot_file = f.name

        try:
            self.gen_report.sfc_to_dot(empty_sfc, dot_file)

            # Should handle empty SFC gracefully
            assert os.path.exists(dot_file)

            with open(dot_file, "r") as f:
                content = f.read()

            assert "digraph SFC" in content
            # Should have minimal content for empty SFC
            assert "init" in content  # Initial node

        finally:
            if os.path.exists(dot_file):
                os.unlink(dot_file)

    def test_html_escape_with_various_inputs(self):
        """Test HTML escaping with various input types."""
        # Test with None
        result = self.gen_report.html_escape(None)
        assert result == "None"

        # Test with number
        result = self.gen_report.html_escape(42)
        assert result == "42"

        # Test with boolean
        result = self.gen_report.html_escape(True)
        assert result == "True"

        # Test with empty string
        result = self.gen_report.html_escape("")
        assert result == ""

    @patch("builtins.open", side_effect=IOError("Permission denied"))
    def test_img_to_base64_io_error(self, mock_open):
        """Test img_to_base64 with IO error."""
        result = self.gen_report.img_to_base64("test.png")
        assert result is None

    def test_sfc_to_dot_default_filename(self):
        """Test SFC to DOT conversion with default filename."""
        try:
            self.gen_report.sfc_to_dot(self.sfc)

            # Should create file with default name
            assert os.path.exists("sfc.dot")

        finally:
            if os.path.exists("sfc.dot"):
                os.unlink("sfc.dot")

    def test_petrinet_to_dot_default_filename(self):
        """Test Petri net to DOT conversion with default filename."""
        pn = {
            "places": ["A"],
            "functions": {"A": "test"},
            "transitions": ["t1"],
            "transition_guards": {"t1": "True"},
            "input_arcs": [],
            "output_arcs": [],
            "initial_marking": ["A"],
        }

        try:
            self.gen_report.petrinet_to_dot(pn)

            # Should create file with default name
            assert os.path.exists("pn.dot")

        finally:
            if os.path.exists("pn.dot"):
                os.unlink("pn.dot")


if __name__ == "__main__":
    pytest.main([__file__])
