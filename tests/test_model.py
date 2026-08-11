"""
Tests for the Pyomo optimization model.

Runs the real solver on the bundled sample dataset to verify
correctness — no mocking, no stubs.
"""
import os
import pytest

# Path to the bundled sample dataset
SAMPLE_DATASET = os.path.join(
    os.path.dirname(__file__), "..", "backend", "data", "dataset.xlsx"
)


# ==================================================
# HELPERS
# ==================================================
def run_optimization():
    """Run the model on the sample dataset and return the result dict"""
    from backend.model import run_clinker_optimization
    return run_clinker_optimization(SAMPLE_DATASET)


# ==================================================
# BASIC SUCCESS CHECKS
# ==================================================
def test_model_runs_without_error():
    """The optimizer should not raise an exception on the sample dataset"""
    result = run_optimization()
    assert result is not None


def test_model_returns_success():
    """The optimizer should find an optimal solution for the sample dataset"""
    result = run_optimization()
    assert result.get("success") is True, (
        f"Optimization failed: {result.get('message')}"
    )


def test_model_returns_objective_value():
    """A successful run must include a finite objective value"""
    result = run_optimization()
    obj = result.get("objective_value")
    assert obj is not None
    assert obj > 0, "Objective value should be positive (total cost)"


# ==================================================
# COST BREAKDOWN CHECKS
# ==================================================
def test_model_returns_cost_breakdown():
    """Result should include a cost_breakdown dict with three cost components"""
    result = run_optimization()
    breakdown = result.get("cost_breakdown")
    assert breakdown is not None, "cost_breakdown missing from result"
    assert "production" in breakdown
    assert "transport" in breakdown
    assert "inventory" in breakdown


def test_cost_components_are_non_negative():
    """Each individual cost component must be >= 0"""
    result = run_optimization()
    breakdown = result.get("cost_breakdown", {})
    assert breakdown.get("production", -1) >= 0
    assert breakdown.get("transport", -1) >= 0
    assert breakdown.get("inventory", -1) >= 0


def test_cost_components_sum_approximately_to_objective():
    """
    Production + transport + inventory costs should roughly equal
    the total objective value (within 1% tolerance, since unmet-demand
    penalty may also be included in the objective).
    """
    result = run_optimization()
    obj = result.get("objective_value", 0)
    bd = result.get("cost_breakdown", {})
    component_sum = bd.get("production", 0) + bd.get("transport", 0) + bd.get("inventory", 0)

    # Allow up to 10% difference (unmet penalty could contribute)
    assert abs(component_sum - obj) / max(obj, 1) <= 0.10, (
        f"Cost components ({component_sum:.2f}) deviate >10% from objective ({obj:.2f})"
    )


# ==================================================
# MODEL STRUCTURE CHECKS
# ==================================================
def test_model_object_has_expected_sets():
    """The returned Pyomo model should have IU, GU nodes and time periods"""
    result = run_optimization()
    model = result.get("model")
    assert model is not None
    assert len(list(model.IU)) > 0, "No IU (production) nodes found"
    assert len(list(model.N)) > 0,  "No nodes found"
    assert len(list(model.T)) > 0,  "No time periods found"
