import time
import requests
from typing import Union
import json
import warnings
from .execution import check_correctness
from .local_model_inference import local_model_inference


class CodeEngine:

    def __init__(self, user_id="", password=""):

        self.user_id = user_id
        self.password = password
        if self.user_id == "":
            self.environment = "local"
        else:
            self.environment = "prod"

        #TODO: Add warning here that we don't take responsibility for the code that's generated for the service and that it could harm your system if you ask it to write dangerous code
    
    def generate_code(
            self, docstrings: str, test_cases: Union[dict, list], 
            func_name: str="solution", output_type: type=None, input_types: Union[type, dict]=None, 
        ):
        # -> Solution:
        """
        Generates code to solve the prompt

        Inputs:
            Required:
                docstrings: (string) description of what you want the code to do
                test_cases: (dict or list of dicts) test cases to verify that the output function is working properly
                    format: 
                        Single input argument, single test case: 
                        {
                            "name_of_your_input": test_input_object,
                            "output": output_object_the_code_should_create
                        }

                        Mulitple arguments, single test case:
                        {
                            "name_of_your_first_input": test_input_object,
                            "name_of_your_second_input": test_input_object,
                            "output": output_object_the_code_should_create
                        }

                        Mulitple arguments, multiple test cases:
                        [
                            {"name_of_your_first_input": test_input_object_1,
                            "name_of_your_second_input": test_input_object_1,
                            "output": output_object_the_code_should_create},

                            {"name_of_your_first_input": test_input_object_2,
                            "name_of_your_second_input": test_input_object_2,
                            "output": output_object_the_code_should_create}
                        ]
          
            Optional:
                func_name: (string) name of the output function that's going to solve your problem (this can help the service figure out the code to write)
                output_type: (type) type of the output of the function (this can help the service figure out the code to write)
                input_types: (type or dict) types of the input arguments (this can also be inferred from the test cases)
        Ouput:
            Solution object
        """
    
        if type(test_cases) is dict:
            test_cases = [test_cases] # can now assume test_cases will be in a list

        inputs = self._infer_inputs(test_cases)

        if self.environment != "local":
            print('Finding Examples')
            examples = self._find_examples(docstrings)
            print('Generating Prompts')
            prompts = self._generate_prompts(examples, docstrings, inputs, test_cases, func_name, output_type, input_types)
        else:
            examples = None
            prompts = self._generate_prompts(examples, docstrings, inputs, test_cases, func_name, output_type, input_types)

        print('Generating Code')
        result = self._generate_and_test_code(prompts, test_cases, func_name, inputs, max_tries=200, timeout=10.0)

        if not result:
            print("Could not generate a result")
            return None
        else:
            return result


    def _infer_inputs(self, test_cases) -> list:
        """
        Infers the inputs of code baseed on the test cases.
        Asserts that inputs are the same for each test case
        Asserts that 'output' is provided for each test case
        """

        inputs = list(test_cases[0].keys())
        inputs.remove('output')

        for case in test_cases:
            assert "output" in case.keys(), "'output' must be provided for each test case"
            case_inputs = list(case.keys())
            case_inputs.remove('output')

            assert case_inputs == inputs, "Inputs for each test case must match"

        return inputs

    def _find_examples(self, docstrings: str, num_examples: int=10) -> list:
        """
        Searches example database for most relevant examples to aid in code generation
        """
        # currently hit local running bm25 database
        url = "http://127.0.0.1:8000/get_answers"
        data = {"query": docstrings, "n_answers": num_examples}
        r = requests.post(url=url, json=data)
        answers = r.json()["answers"]
        return answers


    def _generate_prompts(self, examples, docstrings, inputs, test_cases, func_name, output_type, input_types) -> list:
        
        
        types = self._infer_input_and_output_types(inputs, output_type, test_cases)
        if not input_types and types != False:
            input_types = types['input_types']
        if not output_type and types != False:
            output_type = types['output_type']

        if not input_types:

            function = f"def {func_name}("
            for case in test_cases:
                for inp in inputs:
                    built_in_check = self._check_for_non_builtin_types(type(case[inp]))
                    if not built_in_check["builtin_type"] and built_in_check["import_statement"] not in function:
                        function = f"{built_in_check['import_statement']}\n\n{function}"
                built_in_check = self._check_for_non_builtin_types(type(case["output"]))
                if not built_in_check["builtin_type"] and built_in_check["import_statement"] not in function:
                    function = f"{built_in_check['import_statement']}\n\n{function}"
                    
            for inp in inputs:
                function += f"{inp}, "
            function = function[:-2] # remove the trailing ,
            function += ")"
        
        else:
            function = f"def {func_name}("
            for inp in inputs:
                built_in_check = self._check_for_non_builtin_types(input_types[inp])
                if built_in_check["builtin_type"]:
                    function += f"{inp}: {input_types[inp].__name__}, "
                else:
                    function += f"{inp}, "
                    if built_in_check["import_statement"] not in function:
                        function = f"{built_in_check['import_statement']}\n\n{function}"

            function = function[:-2] # remove the trailing ,
            function += ")"
        
        if output_type:
            built_in_check = self._check_for_non_builtin_types(output_type)
            if built_in_check["builtin_type"]:
                function += f" -> {output_type.__name__}:\n"
            else:
                function += ":\n"
                if built_in_check["import_statement"] not in function:
                        function = f"{built_in_check['import_statement']}\n\n{function}"
        else:
            function += ":\n"
        
        # add docstrings
        function += f'\t"""{docstrings}"""\n\t' # this way the model starts generating code without formatting

        prompts = [function] # leave one blank prompt in without examples
        if examples is not None:
            for ex in examples:
                prompts.append(f"{ex}\n\n{function}")
        
        return prompts
    
    
    def _check_for_non_builtin_types(self, variable_type: type):
        type_string = str(variable_type)
        
        if '.' in type_string:
            # get the package that it's a part of
            package_name = type_string.split('.')[0].split("'")[-1]

            if package_name == "pandas":
                import_statement = "import pandas as pd"
            elif package_name == "numpy":
                import_statement = "import numpy as np"
            else:
                import_statement = f"import {package_name}"
            return {"builtin_type": False, "import_statement": import_statement}
        else:
            return {"builtin_type": True, "import_statement": None}

        


    
    def _infer_input_and_output_types(self, inputs, output_type, test_cases):
        """
        inputs: list of srings defining the inputs
        test_cases: list of dicts, keys of dicts are the string inputs

        enhancements: 
            infer output type
        """
        
        input_types = {}
        for inp in inputs:
            
            arg_type = type(test_cases[0][inp])
            if '.' in str(arg_type):
                return False  # if there is a . in they type name then it is a non-builtin type (like a dataframe) and just don't worry about it
            for test in test_cases:
                if inp not in test.keys():
                    return False # this is for the edge case of an option argument, or if they forgot to add it

                # make sure the type is the same across all test cases
                next_arg_type = type(test[inp])

                # if they're not all the same, return False and don't do type hints
                if arg_type != next_arg_type:
                    return False

            input_types[inp] = arg_type
        
        # infer output_type
        if output_type is None:
            # check that every type in the test cases is the same
            o_type = type(test_cases[0]["output"])
            if '.' in str(o_type):
                return False
            for test in test_cases:
                if type(test["output"]) != o_type:
                    o_type = None
                    break

            output_type = o_type
        
        return {"input_types": input_types, "output_type": output_type}

    
    def _generate_and_test_code(self, prompts: list, test_cases, function_name, inputs, max_tries: int=200, timeout: float=10.0):
        """
        Takes in a set of prompts and test cases and generates code until a solution passes all of the test cases

        Enhancements:
            batch requets: send multiple prompt for generation in a single request so that we can test multiple solutions at once
            threads: number of threads to do this in parallel with
            information on results: if there's lots of timeouts maybe increaes that, or provide the solution that passed the most test cases
        """

        attemps = set()

        for i in range(max_tries):

            prompt = prompts[i % len(prompts)]

            #TODO: make this configurable based on where we want to call the model
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                code_output = local_model_inference(prompt)

            if code_output in attemps:
                continue
            else:
                attemps.add(code_output)

            executable_test_cases = self._generate_executable_test_cases(test_cases, inputs, function_name)

            for tc in executable_test_cases:
                result = check_correctness(f"{code_output}\n{tc['test_string']}", timeout=timeout, exec_globals=tc['exec_globals'])
                if not result['passed']:
                    break
            
            if result['passed']:
                print('All test cases passed!')
                print(f'\nCode Solution:\n{code_output}\n\n')
                return code_output
        
        return False


    def _generate_executable_test_cases(self, test_cases, inputs, function_name):

        # inputs contains order of the input arguments
        executable_test_cases = []
        for case in test_cases:
            tc = f"assert {function_name}("
            for inp in inputs:
                tc += f"{inp}, "
            tc = tc[:-2] # remove the trailing ,
            if str(type(case['output'])) == "<class 'pandas.core.frame.DataFrame'>":
                tc += f").equals(output)"
            elif str(type(case['output'])) == "<class 'numpy.ndarray'>":
                tc = f"assert np.array_equal({function_name}("
                for inp in inputs:
                    tc += f"{inp}, "
                tc = tc[:-2] # remove the trailing ,
                tc += f", output, equal_nan=True)"
            else:
                tc += f") == output"
            executable_test_cases.append({"test_string": tc, "exec_globals": case})
        
        return executable_test_cases

    def _openai_request(self, prompt: str) -> str:
        """
        Enhancement:
            Make this batch, return 3 solutions
        """
        header = {
            'Authorization': f"Bearer {self.openai_key}",
            'Content-Type': 'application/json'
        }
        data = {
            "prompt": prompt,
            "temperature": 0.8, 
            "max_tokens": 300,
            'stop': ['\n\n\n',  '\nclass', '\ndef', '\n#']
        }
        r = requests.post(url=f"https://api.openai.com/v1/engines/code-davinci-002/completions", headers=header, json=data)
        try:
            out = r.json()['choices'][0]['text']
        except:
            print(r)
            print(r.json())
            time.sleep(30)
            r = requests.post(url=f"https://api.openai.com/v1/engines/code-davinci-002/completions", headers=header, json=data)
            out = r.json()['choices'][0]['text']
        return out


    

    def _parse_environment(self) -> list():
        """
        Does a pip freeze to see all of the packages installed within the environment
        Can use these to narrow down the prompt search to only include solutions with the given packages
        Or could also be used to raise a warning "this solution uses package ___, consider installing it in your virtual environment to help solve this problem"
        """
        raise NotImplementedError
