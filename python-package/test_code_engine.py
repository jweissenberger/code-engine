from code_engine import CodeEngine
from execution import check_correctness
import pandas as pd


def test_infer_input_types():
    ce = CodeEngine()

    inputs = ["first"]
    test_case = [{"first": [1,2,3], "output": [1,2]}]
    output_type = None
    types = ce._infer_input_and_output_types(inputs, output_type, test_case)
    assert types == {"input_types": {"first": list}, "output_type": list}

    inputs = ["first", "second"]
    test_case = [{"first": [1,2,3], "second": 100, "output": [1,2]}]
    types = ce._infer_input_and_output_types(inputs, output_type, test_case)
    assert types == {"input_types": {"first": list, "second": int}, "output_type": list}

    inputs = ["first", "second"]
    test_case = [{"first": [1,2,3], "second": 100, "output": [1,2]},
                {"first": ["hello"], "second": 24, "output": [1,2]}]
    types = ce._infer_input_and_output_types(inputs, output_type, test_case)
    assert types == {"input_types": {"first": list, "second": int}, "output_type": list}


def test_generate_prompts():
    ce = CodeEngine()

    examples = ["a = a**2"]
    docstrings = "Square a integer in python"
    inputs = ["a"]
    test_cases = [{"a": 2, "output": 4}]
    func_name = "square_that_variable"
    output_type = int
    input_types = None

    prompts = ce._generate_prompts(examples, docstrings, inputs, test_cases, func_name, output_type, input_types)
    result = ['def square_that_variable(a: int) -> int:\n\t"""Square a integer in python"""\n\t', 
    'a = a**2\n\ndef square_that_variable(a: int) -> int:\n\t"""Square a integer in python"""\n\t']
    assert prompts == result

    examples = ["a = a**2", "b=b**"]
    docstrings = "Square a integer in python"
    inputs = ["a", "b"]
    test_cases = [{"a": 2, "b": "yo", "output": 4}]
    func_name = "square_that_variable"
    output_type = int
    input_types = None

    prompts = ce._generate_prompts(examples, docstrings, inputs, test_cases, func_name, output_type, input_types)
    result =['def square_that_variable(a: int, b: str) -> int:\n\t"""Square a integer in python"""\n\t', 
    'a = a**2\n\ndef square_that_variable(a: int, b: str) -> int:\n\t"""Square a integer in python"""\n\t', 
    'b=b**\n\ndef square_that_variable(a: int, b: str) -> int:\n\t"""Square a integer in python"""\n\t']
    assert prompts == result

    examples = ["a = a**2"]
    docstrings = "Square a integer in python"
    inputs = ["a", "b"]
    test_cases = [{"a": 2, "b": pd.DataFrame({'name': ['jack', 'jack', 'will'], 'age': [24, 24, 25]}), "output": 4}]
    func_name = "square_that_variable"
    output_type = int
    input_types = None

    prompts = ce._generate_prompts(examples, docstrings, inputs, test_cases, func_name, output_type, input_types)
    result = ['import pandas as pd\n\ndef square_that_variable(a, b) -> int:\n\t"""Square a integer in python"""\n\t', 
    'a = a**2\n\nimport pandas as pd\n\ndef square_that_variable(a, b) -> int:\n\t"""Square a integer in python"""\n\t']
    assert prompts == result


def test_generate_executable_test_cases():
    ce = CodeEngine()

    test_cases = [{'a': 2, 'output': 2}]
    inputs = ['a']
    function_name = "return_number"

    desired_output = ["assert return_number(2) == 2"]
    result = ce._generate_executable_test_cases(test_cases, inputs, function_name)
    assert result == desired_output

    test_cases = [{'a': 2, 'b': 3, 'output': 5},
                {'a': 3, 'b': 3, 'output': 6},
                {'a': 1, 'b': 3, 'output': 4}
                ]
    inputs = ['a', 'b']
    function_name = "add_numbers"

    desired_output = ["assert add_numbers(2, 3) == 5", "assert add_numbers(3, 3) == 6", "assert add_numbers(1, 3) == 4"]
    result = ce._generate_executable_test_cases(test_cases, inputs, function_name)
    assert result == desired_output

def test_check_correctness():
    code_and_test_case = "def add_two_nums(a,b):\n\treturn a+b\n\nassert add_two_nums(1,2) == 3"
    timeout = 5.0
    result = check_correctness(code_and_test_case, timeout)
    assert result == {'passed': True, 'result': 'passed'}

    code_and_test_case = "import time\ndef add_two_nums(a,b):\n\ttime.sleep(2)\n\treturn a+b\n\nassert add_two_nums(1,2) == 3"
    timeout = 0.01
    result = check_correctness(code_and_test_case, timeout)
    assert result == {'passed': False, 'result': 'timed out'}

    code_and_test_case = "def add_two_nums(a,b):\n\treturn a-b\n\nassert add_two_nums(1,2) == 3"
    timeout = 5.0
    result = check_correctness(code_and_test_case, timeout)
    assert result == {'passed': False, 'result': 'failed: '}



if __name__ == "__main__":
    test_generate_prompts()
