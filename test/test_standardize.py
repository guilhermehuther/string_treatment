import os
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
import sys
sys.path.insert(0, os.path.join(CURRENT_DIR, '..', 'src'))
import json
import tempfile
import shutil
import pytest

from string_treatment import standardize

class TestStandardize:
    """Pytest test class for the standardize function."""
    
    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Set up test fixtures before each test method."""

        with open(f"{CURRENT_DIR}/city_example_input.json") as f:
            self.input_data = json.load(f)["input"]
        
        self.temp_dir = tempfile.mkdtemp()
        
        yield
        
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

        return

    def test_json_output_length_equals_input_length(self):
        """Test that the length of output_data equals the length of input_data."""

        print("\n=== Testing JSON output length equals input length ===")
        
        input_data = set(self.input_data)
        output_data = standardize(words=self.input_data)

        len_input_data = len(input_data)
        len_output_data = len(output_data)

        print(f"Input data length: {len_input_data}")
        print(f"Output data length: {len_output_data}")
        
        assert len_output_data == len_input_data, \
            f"Output length ({len_output_data}) should equal input length ({len_input_data})"
        
        for item in self.input_data:
            assert item in output_data, f"Input item '{item}' not found in output"
        
        print("✓ PASS: Output length equals input length")

        return

    def test_empty_list(self):
        """Test standardize function with empty list (data = []). Should raise ValueError."""

        print("\n=== Testing empty list ===")
        
        data = []
        with pytest.raises(ValueError) as e:
            standardize(words=data)

        print(f"Caught error: {e.value}")
        
        print("✓ PASS: Empty list correctly raises ValueError")

    def test_elements_list(self):
        """Test standardize function with various element lists using subtests."""

        print("\n=== Testing single element list and various cases with subtests ===")

        test_cases = [
            ["Test", "Test", "Test"],
            ["Test1", "Test1", "Test2"],
            ["Test"],
            [
                "São Paulo@#$", "São Paulo 123",
                "São Paulo-", "São Paulo_",
                "123 Paulo_", "123", "----", 
                "xyz - zyx", ".", ","
            ]
        ]

        for case in test_cases:
            standardize(words=case)

        print("✓ PASS: All subtests for elements list passed.")

        return

    def test_only_punctuation_raises(self):
        """Test that a list of only punctuation raises an error."""

        data = [".", "...", "///", "--+#'"]

        with pytest.raises(ValueError):
            standardize(words=data)

        return

    def test_distinct_city_names_identity(self):
        """Test that distinct city names map to themselves."""

        data = [
            "SãoPaulo", 
            "RioDeJaneiro", 
            "Brasília", 
            "Salvador", 
            "Fortaleza"
        ]
        
        result = standardize(words=data)
        
        assert len(result) == len(data)
        
        for item in data:
            assert result[item] == item, f"Item '{item}' should map to itself, got '{result[item]}'"

        return

    def test_different_thresholds(self):
        """Test with different threshold values."""
        print("\n=== Testing different thresholds ===")
        
        data = ["São Paulo", "sao paulo", "Rio de Janeiro", "rio de janeiro"]
        
        standardize(words=data, threshold=95)
        standardize(words=data, threshold=70)
        
        print("✓ PASS: Different thresholds processed correctly")
        
        return

    def test_graph_output(self):
        """Test with graph output functionality."""
        print("\n=== Testing graph output ===")
        
        data = ["São Paulo", "sao paulo", "Rio de Janeiro", "rio de janeiro"]
        
        result = standardize(words=data, output_graph_path=self.temp_dir)
        
        assert isinstance(result, dict), f"Expected dict, got {type(result)}"
        
        graph_files = [f for f in os.listdir(self.temp_dir) if f.endswith('.html')]
        assert len(graph_files) > 0, f"No graph files created in {self.temp_dir}"
        
        print("✓ PASS: Graph output functionality works correctly")

        return

    def test_all(self):
        """Test the original functionality from the script."""
        print("\n=== Testing original functionality ===")
        
        output_data = standardize(
            words=self.input_data,
            output_graph_path=CURRENT_DIR
        )
        with open(f"{CURRENT_DIR}/city_example_output.json", "w") as f:
            json.dump({"output": output_data}, f)

        len_set_input_data = len(set(self.input_data))

        graph_files = [f for f in os.listdir(CURRENT_DIR) if f.endswith('.html')]
        
        assert isinstance(output_data, dict), "output should be a dict"
        assert len(output_data) == len_set_input_data, \
            f"Output length ({len(output_data)}) should equal input length ({len_set_input_data})"
        assert len(graph_files) > 0, "Graph files should be created"

        print(f"✓ PASS: Original functionality works correctly")
            
        return
