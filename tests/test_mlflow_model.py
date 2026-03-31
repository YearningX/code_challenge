"""
Test Cases for MLflow Model

OPTIMIZED (2026-03-31): Comprehensive test suite for MLflow PyFunc model
including unit tests, integration tests, and serving tests.

Features:
- Input validation tests
- Multi-format input tests
- Error handling tests
- Model loading and serving tests
- Performance tests
"""

import os
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import mlflow
import pandas as pd
from mlflow.pyfunc import PythonModel

from me_ecu_agent.config import PerformanceConfig
from me_ecu_agent.error_handling import (
    ErrorCode,
    ValidationError,
    create_input_validator,
    create_error_handler
)
from me_ecu_agent.mlflow_model import ECUAgentMLflowModel


class TestInputValidator(unittest.TestCase):
    """Test input validation functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.config = PerformanceConfig()
        self.validator = create_input_validator(self.config)

    def test_valid_query(self):
        """Test validation of valid query."""
        query = "What is the operating temperature of ECU-750?"
        result = self.validator.validate_query(query)
        self.assertEqual(result, query)

    def test_empty_query(self):
        """Test rejection of empty query."""
        with self.assertRaises(ValidationError) as context:
            self.validator.validate_query("")
        self.assertIn("empty", str(context.exception).lower())

    def test_whitespace_only_query(self):
        """Test rejection of whitespace-only query."""
        with self.assertRaises(ValidationError):
            self.validator.validate_query("   \n\t   ")

    def test_query_too_long(self):
        """Test rejection of excessively long query."""
        long_query = "test" * 1000  # 4000 characters
        with self.assertRaises(ValidationError) as context:
            self.validator.validate_query(long_query)
        self.assertIn("maximum length", str(context.exception).lower())

    def test_non_string_input(self):
        """Test rejection of non-string input."""
        with self.assertRaises(ValidationError):
            self.validator.validate_query(123)

    def test_query_sanitization(self):
        """Test query sanitization (whitespace trimming)."""
        query = "  What is ECU-850?  "
        result = self.validator.validate_query(query)
        self.assertEqual(result, "What is ECU-850?")


class TestErrorHandler(unittest.TestCase):
    """Test error handling functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.error_handler = create_error_handler()

    def test_validation_error_handling(self):
        """Test handling of validation errors."""
        error = ValidationError("Invalid query", {"field": "query"})
        response = self.error_handler.handle_error(error, "test query")

        self.assertEqual(response["status"], "error")
        self.assertEqual(response["query"], "test query")
        self.assertIn("error", response)
        self.assertEqual(response["error"]["code"], ErrorCode.VALIDATION_ERROR.value)

    def test_generic_exception_handling(self):
        """Test handling of generic exceptions."""
        error = Exception("Unexpected error")
        response = self.error_handler.handle_error(error)

        self.assertEqual(response["status"], "error")
        self.assertEqual(response["error"]["code"], ErrorCode.UNKNOWN_ERROR.value)

    def test_error_statistics(self):
        """Test error statistics tracking."""
        # Generate some errors
        for _ in range(3):
            self.error_handler.handle_error(ValidationError("Test error"))
        for _ in range(2):
            self.error_handler.handle_error(Exception("Generic error"))

        stats = self.error_handler.get_error_statistics()
        self.assertEqual(stats["total_requests"], 5)
        self.assertGreater(stats["error_rate"], 0)
        self.assertIn("errors_by_type", stats)


class TestMLflowModelInputNormalization(unittest.TestCase):
    """Test input normalization in MLflow model."""

    def setUp(self):
        """Set up test fixtures."""
        self.model = ECUAgentMLflowModel()

    def test_string_input(self):
        """Test normalization of string input."""
        result = self.model._normalize_input("What is ECU-750?")
        self.assertEqual(result, ["What is ECU-750?"])

    def test_dict_input(self):
        """Test normalization of dictionary input."""
        result = self.model._normalize_input({"query": "What is ECU-850?"})
        self.assertEqual(result, ["What is ECU-850?"])

    def test_dict_with_question_key(self):
        """Test normalization of dictionary with 'question' key."""
        result = self.model._normalize_input({"question": "What is ECU-800?"})
        self.assertEqual(result, ["What is ECU-800?"])

    def test_list_input(self):
        """Test normalization of list input."""
        queries = ["What is ECU-750?", "What is ECU-850?"]
        result = self.model._normalize_input(queries)
        self.assertEqual(result, queries)

    def test_dataframe_input(self):
        """Test normalization of DataFrame input."""
        df = pd.DataFrame({
            "query": ["What is ECU-750?", "What is ECU-850?"]
        })
        result = self.model._normalize_input(df)
        self.assertEqual(result, ["What is ECU-750?", "What is ECU-850?"])

    def test_dataframe_with_question_column(self):
        """Test DataFrame with 'question' column."""
        df = pd.DataFrame({
            "question": ["What is ECU-750?"]
        })
        result = self.model._normalize_input(df)
        self.assertEqual(result, ["What is ECU-750?"])

    def test_unsupported_input_type(self):
        """Test rejection of unsupported input type."""
        with self.assertRaises(ValueError):
            self.model._normalize_input(123)


class TestMLflowModelValidation(unittest.TestCase):
    """Test model validation functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.model = ECUAgentMLflowModel()

    def test_valid_query_validation(self):
        """Test validation of valid query."""
        query = "What is the operating temperature?"
        result = self.model._validate_input(query)
        self.assertEqual(result, query)

    def test_empty_query_validation(self):
        """Test rejection of empty query."""
        with self.assertRaises(ValueError):
            self.model._validate_input("")

    def test_too_long_query_validation(self):
        """Test rejection of too long query."""
        long_query = "x" * 2000
        with self.assertRaises(ValueError):
            self.model._validate_input(long_query)


class TestMLflowModelPrediction(unittest.TestCase):
    """Test MLflow model prediction functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.model = ECUAgentMLflowModel()
        self.mock_graph = Mock()
        self.model.graph = self.mock_graph

    def test_predict_without_load_context(self):
        """Test prediction without loading context raises error."""
        model = ECUAgentMLflowModel()
        with self.assertRaises(RuntimeError):
            model.predict(None, "What is ECU-750?")

    @patch('me_ecu_agent.mlflow_model.HumanMessage')
    def test_single_query_prediction(self, mock_human_msg):
        """Test prediction with single query."""
        # Setup mocks
        mock_human_msg.return_value = Mock(content="test query")
        self.mock_graph.invoke.return_value = {
            "messages": [Mock(content="Test response")]
        }

        # Execute prediction
        result = self.model.predict(None, "What is ECU-750?")

        # Verify
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0], "Test response")

    def test_batch_query_prediction(self):
        """Test prediction with multiple queries."""
        self.mock_graph.invoke.return_value = {
            "messages": [Mock(content="Response")]
        }

        queries = ["Query 1", "Query 2"]
        result = self.model.predict(None, queries)

        self.assertEqual(len(result), 2)
        self.assertEqual(self.mock_graph.invoke.call_count, 2)

    def test_prediction_with_error(self):
        """Test prediction handles errors gracefully."""
        self.mock_graph.invoke.side_effect = Exception("Test error")

        result = self.model.predict(None, "What is ECU-750?")

        self.assertIsInstance(result, list)
        self.assertIn("error", str(result[0]).lower())


class TestMLflowModelPerformance(unittest.TestCase):
    """Test MLflow model performance characteristics."""

    def setUp(self):
        """Set up test fixtures."""
        self.model = ECUAgentMLflowModel()
        self.mock_graph = Mock()
        self.model.graph = self.mock_graph

    def test_prediction_latency(self):
        """Test prediction completes within timeout."""
        import time

        def mock_invoke(*args, **kwargs):
            time.sleep(0.1)  # Simulate processing
            return {"messages": [Mock(content="Response")]}

        self.mock_graph.invoke = mock_invoke

        start_time = time.time()
        self.model.predict(None, "What is ECU-750?")
        latency = time.time() - start_time

        # Should complete in reasonable time (< 5 seconds for single query)
        self.assertLess(latency, 5.0)

    def test_batch_processing_performance(self):
        """Test batch processing doesn't degrade significantly."""
        import time

        def mock_invoke(*args, **kwargs):
            return {"messages": [Mock(content="Response")]}

        self.mock_graph.invoke = mock_invoke

        # Test single query
        start_time = time.time()
        self.model.predict(None, "Query 1")
        single_time = time.time() - start_time

        # Test batch of 5 queries
        queries = [f"Query {i}" for i in range(5)]
        start_time = time.time()
        self.model.predict(None, queries)
        batch_time = time.time() - start_time

        # Batch should not take 5x longer (some parallelism possible)
        # But we expect linear for sequential processing
        # Add minimum threshold for very fast operations
        expected_max = max(single_time * 5 * 1.5, 0.1)  # At least 100ms
        self.assertLess(batch_time, expected_max)


class TestMLflowModelIntegration(unittest.TestCase):
    """Integration tests for MLflow model."""

    @unittest.skip("Requires full model setup")
    def test_model_loading_and_prediction(self):
        """Test complete model loading and prediction flow."""
        # This test requires actual vector stores and documents
        # Skip in normal unit test runs
        pass

    @unittest.skip("Requires MLflow server")
    def test_model_serving(self):
        """Test model serving via MLflow."""
        # This test requires MLflow server
        # Skip in normal unit test runs
        pass


def run_tests():
    """Run all tests."""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestInputValidator))
    suite.addTests(loader.loadTestsFromTestCase(TestErrorHandler))
    suite.addTests(loader.loadTestsFromTestCase(TestMLflowModelInputNormalization))
    suite.addTests(loader.loadTestsFromTestCase(TestMLflowModelValidation))
    suite.addTests(loader.loadTestsFromTestCase(TestMLflowModelPrediction))
    suite.addTests(loader.loadTestsFromTestCase(TestMLflowModelPerformance))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("="*60)

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    exit(0 if success else 1)
