from code_engine import CodeEngine


def test_infer_input_types():
    ce = CodeEngine()

    inputs = ["first"]
    test_case = [{"first": [1,2,3]}]
    input_types = ce._infer_input_types(inputs, test_case)
    assert input_types == {"first": list}

    inputs = ["first", "second"]
    test_case = [{"first": [1,2,3], "second": 100}]
    input_types = ce._infer_input_types(inputs, test_case)
    assert input_types == {"first": list, "second": int}

    inputs = ["first", "second"]
    test_case = [{"first": [1,2,3], "second": 100},
                {"first": ["hello"], "second": 24}]
    input_types = ce._infer_input_types(inputs, test_case)
    assert input_types == {"first": list, "second": int}


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

if __name__ == "__main__":
    test_generate_prompts()