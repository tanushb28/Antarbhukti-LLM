#!/usr/bin/env python3
"""
Unit tests for the Verifier module.
Tests cover Petri net containment verification, path analysis, and Z3 integration.
"""

from unittest.mock import Mock, patch

import pytest

from src.antarbhukti.sfc import SFC
from src.antarbhukti.sfc_verifier import Verifier


class TestVerifier:
    """Test suite for Verifier class."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.verifier = Verifier()

    def test_init(self):
        """Test Verifier initialization."""
        assert self.verifier.cutpoints1 == []
        assert self.verifier.cutpoints2 == []
        assert self.verifier.paths1 == []
        assert self.verifier.paths2 == []
        assert self.verifier.matches1 == []
        assert self.verifier.unmatched1 == []
        assert self.verifier.contained is False

    def test_infix_to_sexpr_basic(self):
        """Test basic infix to S-expression conversion."""
        # Test logical operators
        assert "and" in self.verifier.infix_to_sexpr("a && b")
        assert "or" in self.verifier.infix_to_sexpr("a || b")
        assert "not" in self.verifier.infix_to_sexpr("!a")

        # Test comparison operators - should convert to S-expression format
        result = self.verifier.infix_to_sexpr("x == 5")
        assert "=" in result  # S-expression uses "=" not "=="

        result = self.verifier.infix_to_sexpr("x != 5")
        # S-expression uses "(not (= x 5))"
        assert "not" in result and "=" in result

        # Test modulus operator
        result = self.verifier.infix_to_sexpr("x % 2")
        assert "mod" in result  # S-expression uses "mod" not "%"

    def test_infix_to_sexpr_complex(self):
        """Test complex infix to S-expression conversion."""
        # Test complex expression
        expr = "a && b || c"
        result = self.verifier.infix_to_sexpr(expr)
        assert isinstance(result, str)

        # Test with numbers
        expr = "counter >= 3"
        result = self.verifier.infix_to_sexpr(expr)
        assert isinstance(result, str)

    def test_infix_to_sexpr_invalid(self):
        """Test infix to S-expression conversion with invalid input."""
        # Test with invalid syntax
        invalid_expr = "a &&& b"
        result = self.verifier.infix_to_sexpr(invalid_expr)
        # Should return the original expression if parsing fails
        assert result == invalid_expr

    def test_sfc_to_petrinet(self):
        """Test SFC to Petri net conversion."""
        # Create a simple SFC
        sfc = SFC()
        sfc.load("tests/test_data/simple_sfc.txt")

        # Convert to Petri net
        pn = self.verifier.sfc_to_petrinet(sfc)

        # Verify Petri net structure
        assert "places" in pn
        assert "functions" in pn
        assert "transitions" in pn
        assert "transition_guards" in pn
        assert "input_arcs" in pn
        assert "output_arcs" in pn
        assert "initial_marking" in pn

        # Verify content
        assert len(pn["places"]) == 3
        assert len(pn["transitions"]) == 2
        assert pn["initial_marking"] == ["Start"]

        # Check place names
        assert "Start" in pn["places"]
        assert "Process" in pn["places"]
        assert "End" in pn["places"]

    def test_find_cut_points_simple(self):
        """Test cut point finding with simple Petri net."""
        sfc = SFC()
        sfc.load("tests/test_data/simple_sfc.txt")
        pn = self.verifier.sfc_to_petrinet(sfc)

        cutpoints = self.verifier.find_cut_points(pn)

        # Should find at least initial and final states
        assert isinstance(cutpoints, list)
        assert len(cutpoints) >= 2
        assert "Start" in cutpoints  # Initial state
        assert "End" in cutpoints  # Final state

    def test_parse_z3_assignments_simple(self):
        """Test Z3 assignment parsing."""
        # Test simple assignment
        expr = "(= counter 5)"
        result = self.verifier.parse_z3_assignments(expr)
        assert isinstance(result, dict)
        assert "counter" in result
        assert result["counter"] == "5"

    def test_parse_z3_assignments_complex(self):
        """Test Z3 assignment parsing with complex expressions."""
        # Test compound assignment
        expr = "(and (= counter 5) (= done true))"
        result = self.verifier.parse_z3_assignments(expr)
        assert isinstance(result, dict)
        assert "counter" in result
        assert "done" in result

    def test_parse_z3_assignments_true(self):
        """Test Z3 assignment parsing with 'true' expression."""
        expr = "true"
        result = self.verifier.parse_z3_assignments(expr)
        assert result == {}

    def test_are_data_transformations_equivalent(self):
        """Test data transformation equivalence checking."""
        # Test equivalent transformations
        subst1 = "(= counter 5)"
        subst2 = "(= counter 5)"
        allowed_vars = ["counter"]

        result = self.verifier.are_data_transformations_equivalent(
            subst1, subst2, allowed_vars
        )
        assert result is True

        # Test non-equivalent transformations
        subst1 = "(= counter 5)"
        subst2 = "(= counter 3)"

        result = self.verifier.are_data_transformations_equivalent(
            subst1, subst2, allowed_vars
        )
        assert result is False

    def test_check_pn_containment_simple(self):
        """Test Petri net containment checking with simple models."""
        # Load two SFC models
        sfc1 = SFC()
        sfc1.load("tests/test_data/simple_sfc.txt")
        pn1 = self.verifier.sfc_to_petrinet(sfc1)

        sfc2 = SFC()
        sfc2.load("tests/test_data/modified_sfc.txt")
        pn2 = self.verifier.sfc_to_petrinet(sfc2)

        # Perform containment check
        result = self.verifier.check_pn_containment(sfc1, pn1, sfc2, pn2)

        # Verify results are stored
        assert isinstance(result, bool)
        assert isinstance(self.verifier.cutpoints1, list)
        assert isinstance(self.verifier.cutpoints2, list)
        assert isinstance(self.verifier.paths1, list)
        assert isinstance(self.verifier.paths2, list)
        assert isinstance(self.verifier.matches1, list)
        assert isinstance(self.verifier.unmatched1, list)

    def test_get_analysis_results(self):
        """Test getting analysis results."""
        # Run a simple analysis first
        sfc1 = SFC()
        sfc1.load("tests/test_data/simple_sfc.txt")
        pn1 = self.verifier.sfc_to_petrinet(sfc1)

        sfc2 = SFC()
        sfc2.load("tests/test_data/modified_sfc.txt")
        pn2 = self.verifier.sfc_to_petrinet(sfc2)

        self.verifier.check_pn_containment(sfc1, pn1, sfc2, pn2)

        # Get analysis results
        results = self.verifier.get_analysis_results()

        # Verify all expected keys are present
        expected_keys = [
            "cutpoints1",
            "cutpoints2",
            "paths1",
            "paths2",
            "matches1",
            "unmatched1",
            "contained",
        ]
        for key in expected_keys:
            assert key in results

    def test_is_contained(self):
        """Test containment status checking."""
        # Initially should be False
        assert self.verifier.is_contained() is False

        # After setting contained status
        self.verifier.contained = True
        assert self.verifier.is_contained() is True

    def test_get_unmatched_paths(self):
        """Test getting unmatched paths."""
        # Initially should be empty
        assert self.verifier.get_unmatched_paths() == []

        # After setting unmatched paths
        test_path = {"src": "A", "tgt": "B", "cond": "test"}
        self.verifier.unmatched1 = [test_path]
        assert self.verifier.get_unmatched_paths() == [test_path]

    def test_get_matched_paths(self):
        """Test getting matched paths."""
        # Initially should be empty
        assert self.verifier.get_matched_paths() == []

        # After setting matched paths
        test_match = ({"src": "A", "tgt": "B"}, {"src": "A", "tgt": "B"})
        self.verifier.matches1 = [test_match]
        assert self.verifier.get_matched_paths() == [test_match]

    def test_empty_sfc_conversion(self):
        """Test converting empty SFC to Petri net."""
        sfc = SFC()
        # Don't load any data, keep it empty

        pn = self.verifier.sfc_to_petrinet(sfc)

        # Should handle empty SFC gracefully
        assert pn["places"] == []
        assert len(pn["transitions"]) == 0
        assert pn["initial_marking"] == [""]

    def test_sfc_with_multiple_transitions(self):
        """Test SFC with multiple transitions from same source."""
        sfc = SFC()
        sfc.load("tests/test_data/modified_sfc.txt")

        pn = self.verifier.sfc_to_petrinet(sfc)
        cutpoints = self.verifier.find_cut_points(pn)

        # Should identify branch points as cut points
        assert isinstance(cutpoints, list)
        assert len(cutpoints) >= 2

    @patch("src.antarbhukti.sfc_verifier.z3")
    def test_z3_integration_mocked(self, mock_z3):
        """Test Z3 integration with mocked Z3 solver."""
        # Mock Z3 solver behavior
        mock_solver = Mock()
        mock_z3.Solver.return_value = mock_solver
        mock_solver.check.return_value = mock_z3.sat

        # Test that methods using Z3 can be called without errors
        expr = "counter >= 3"
        result = self.verifier.infix_to_sexpr(expr)
        assert isinstance(result, str)

    def test_petri_net_structure_validation(self):
        """Test Petri net structure validation."""
        sfc = SFC()
        sfc.load("tests/test_data/simple_sfc.txt")
        pn = self.verifier.sfc_to_petrinet(sfc)

        # Verify all required fields are present
        required_fields = [
            "places",
            "functions",
            "transitions",
            "transition_guards",
            "input_arcs",
            "output_arcs",
            "initial_marking",
        ]
        for field in required_fields:
            assert field in pn, f"Missing required field: {field}"

        # Verify data types
        assert isinstance(pn["places"], list)
        assert isinstance(pn["functions"], dict)
        assert isinstance(pn["transitions"], list)
        assert isinstance(pn["transition_guards"], dict)
        assert isinstance(pn["input_arcs"], list)
        assert isinstance(pn["output_arcs"], list)
        assert isinstance(pn["initial_marking"], list)

    def test_transition_guard_extraction(self):
        """Test extraction of transition guards."""
        sfc = SFC()
        sfc.load("tests/test_data/simple_sfc.txt")
        pn = self.verifier.sfc_to_petrinet(sfc)

        # Check that guards are properly extracted
        assert isinstance(pn["transition_guards"], dict)
        for transition_id, guard in pn["transition_guards"].items():
            assert isinstance(transition_id, str)
            assert isinstance(guard, str)


if __name__ == "__main__":
    pytest.main([__file__])
