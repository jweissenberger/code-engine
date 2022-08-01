# Code Engine

Code Engine is a python package that automatically solves your coding problems using Machine Learning.
Instead of posting your problem on a forum and waiting days for an answer, let state of the art ML solve it for you almost instantly. All you need to provide is: 

1. A description of what you want the code to do 
2. A simple test case to verify that the code works properly

```python
from code_engine import CodeEngine

ce = CodeEngine()

docstrings = "This function adds two numbers together"
test_case = {"a": 1, "b": 2, "output": 3}

result = ce.generate_code(docstrings, test_cases=test_case)
>>> Generating Code
>>> All test cases passed!

print(result)
def solution(a: int, b: int):
	"""This function adds two numbers together"""
	return a + b
```

## Abstract

Most code models and ML code completion tools are usually only good for writing boilerplate code and answering simple questions. For anything more complicated, these models are usually only right about 20% of the time (see Codex and Codegen papers). 

But, if you give these models multiple shots at solving the same problem, they become far more successful. This is measured by the pass @ k metric, which tracks if a model is able to solve a coding problem in 'k' attempts. 

The 12 Billion parameter Codex model is only correct 28% of the time on the HumanEval benchmark when you give it 1 shot on each problem, but if you give it 100 attempts, it gets a correct answer for each problem 72% of the time. 

This is the advantage that Code Engine provides. It provides these code models with multiple attempts to solve a given problem and then verifies the generated code against a provided test case.

This allows Code Engine to be far more capable than other ML coding tools and allows it to create production-ready solutions that have been verified by your test cases.


## Premium Service
`coming soon`