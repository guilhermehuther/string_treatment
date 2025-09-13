import json
import os
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

from src.string_treatment import standardize

with open(f"{CURRENT_DIR}/tests/city_example_input.json") as f:
    input_data = json.load(f)["input"]

output_data = standardize(
    words=input_data
)

with open(f"{CURRENT_DIR}/tests/city_example_output.json", "w") as f:
    json.dump(
        {"output": output_data}, 
        f, 
        ensure_ascii=False, 
        indent=4
    )

output_graph = standardize(
    words=input_data,
    output_graph_path=f"{CURRENT_DIR}/tests"
)
