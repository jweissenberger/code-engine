import time
import requests
from typing import Union

class Solution:

    def __init__(self, executable_string: str, test_case_results: dict, passed: bool):
        self.executable_string = executable_string
        self.test_case_results = test_case_results
    
    def __call__(self, *args, **kwargs):
        # execute the actual output function with the given arguments
        raise NotImplementedError 
    
    def __str__(self):
        return self.executable_string
    
    def generate_pytest(self):
        raise NotImplementedError
    
    def write_to_file(self):
        raise NotImplementedError

    

class CodeEngine:

    def __init__(self, user_id="", password=""):

        self.user_id = user_id
        self.password = password

        #TODO: Add warning here that we don't take responsibility for the code that's generated for the service and that it could harm your system if you ask it to write dangerous code
    
    def generate_code(
            self, docstrings: str, inputs:Union[str, list], test_cases: Union[dict, list], 
            func_name: str="solution", output_type: type=None, input_types: Union[type, dict]=None, 
        ) -> Solution:
        """
        Generates code to solve the prompt

        Inputs:
            Required:
                docstrings: (string) description of what you want the code to do
                inputs: (string or list of strings) strings for the input names of the function
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
        assert type(inputs) is list or type(inputs) is str, "inputs must be a string or a list of strings"
        if type(inputs) is str:
            inputs = [inputs] # can now assume inputs will always be in a list
        if type(test_cases) is dict:
            test_cases = [test_cases] # can now assume test_cases will be in a list

        examples = self._find_examples(docstrings)
        prompts = self._generate_prompts(examples, docstrings, inputs, test_cases, func_name, output_type, input_types)
        passed, solution, results = self._generate_and_test_code(prompts, inputs,)

        if passed:
            return solution
        else:
            print("Failed to generate a working solution")
            return results



    def _find_examples(self, docstrings: str, num_examples: int=10) -> list:
        """
        Searches example database for most relevant examples to aid in code generation
        """
        # currently hit local running bm25 database
        url = "http://127.0.0.1:8000/get_answers"
        data = {"query": docstrings, "n_answers": num_examples}
        r = requests.post(url=url, json=data)
        answers = r.json()["answers"]
        raise answers


    def _generate_prompts(self, examples, docstrings, inputs, test_cases, func_name, output_type, input_types) -> list:
        
        if not input_types:
            input_types = self._infer_input_types(inputs, test_cases)

        function = f"def {func_name}({inputs})"
        
        raise NotImplementedError
    
    def _infer_input_types(self, inputs, test_cases):
        
        input_types = {}
        for inp in inputs:
            # make sure the type is the same across all test cases
            all_same = True
            if not test_cases.get(inp):
                return False # this is for the edge case of an option argument, I am getting to far ahead of myself

            for case in test_cases

            # if they're not all the same, return False and don't do type hints
            if not all_same:
                return False


    
    def _generate_and_test_code(self, prompts: list, inputs: list, outputs: list, max_tries: int=200):
        """
        Takes in a set of prompts and test cases and generates code until a solution passes all of the test cases

        Enhancements:
            batch requets: send multiple prompt for generation in a single request so that we can test multiple solutions at once
            timeout: maximum amount of time to let this run, return the code that passes the most test cases at the end
            threads: number of threads to do this in parallel with
        """

        for i in range(max_tries):

            prompt = prompts[i % len(prompts)]
            code_output = self._code_model_generation(prompt)
            all_pass, results, formatted_code = self._check_test_cases(code_output, prompt, inputs, outputs)
            if all_pass:
                break
        
        return all_pass, formatted_code, results


    
    def _check_test_cases(code_output, prompt, inputs, outputs):

        # TODO: check if packages called outside of this package can be callable by this code

        # see if any functions from the prompt were called in the code_output

        # parse out the name of the input paramter to the fuction
        
        results = []
        all_pass = True
        for i in range(len(inputs)):
            output = ""
            # put intput into the code
            input_test_case = f"input = {str(inputs[i])}"
            formatted_code = ""
            try:
                start = time.time()
                formatted_code = self._format_code(prompt, input_test_case, code_output)
                exec(formatted_code)
                finish = time.time()
            except Exception as e:
                finish = time.time()
                all_pass = False
                results.append({"result": "Failure", "reason": e, "execution_time": finish-start})
            if output == outputs[i]:
                results.append({"result": "Pass", "execution_time": finish-start})
            else:
                all_pass = False
                results.append({"result": "Failure", "reason": f"failed test case {i}", "execution_time": finish-start})
        
        return all_pass, results, formatted_code


    def _format_code() -> str:
        """
        Put the prompt, test_case and code_output together

        might need to create two outputs here one with the input (to test the test case) and one without the output to return to the start of the function if it passes
        """
        raise NotImplementedError
        
    
    def _code_model_generation(prompt: str()) -> str():
        # generate code based on prompt
        raise NotImplementedError



    def _parse_environment(self) -> list():
        """
        Does a pip freeze to see all of the packages installed within the environment
        Can use these to narrow down the prompt search to only include solutions with the given packages
        Or could also be used to raise a warning "this solution uses package ___, consider installing it in your virtual environment to help solve this problem"
        """
        raise NotImplementedError
