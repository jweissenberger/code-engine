# Code Engine

```python
from code_engine import CodeEngine

ce = CodeEngine()

docstrings = "This function adds two numbers together"
inputs = ["a", "b"]
test_case = [{"a": 1, "b": 2, "output": 3}]

result = ce.generate_code(docstrings, inputs, test_cases=test_case)
>>> Finding Examples
>>> Generating Prompts
>>> Generating Code
>>> Running Test Cases
>>> All test cases passed!

print(results)
def solution(a: int, b: int):
	"""This function adds two numbers together"""
	return (a + b)
```