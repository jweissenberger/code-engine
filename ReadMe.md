# Code Engine

Code Engine is a python package that automatically solves your coding problems using Machine Learning.
Instead of posting your problem on a forum and waiting days for an answer, let state of the art ML solve it for you almost instantly. All you need to provide is: 

1. A description of what you want the code to do 
2. The inputs of the code
3. A simple test case to verify that the code works properly

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

print(result)
def solution(a: int, b: int):
	"""This function adds two numbers together"""
	return (a + b)
```