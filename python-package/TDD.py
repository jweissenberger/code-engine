

class TDD:

    def __init__(self, user_id="", password=""):

        self.user_id = user_id
        self.password = password

        #TODO: Add warning here that we don't take responsibility for the code that's generated for the service and that it could harm your system if you ask it to write dangerous code
    
    def generate_code(self, prompt: str, inputs: list(), outputs: list(), output_type="string", generate_testcase=False) -> str():
        """
        Generates code to solve the prompt

        Inputs:
            prompt: (string) natural language describing the desired code solution
            inputs: (list) list of inputs for test cases
            outputs: (list) list of outputs for test cases
            output_type: (string) string describing the desired output type. Options: "string", "pytest_file"
        Ouput:
            solution: (string) string with the code solution
        """
        examples = self._find_examples(prompt)
        prompts = self._generate_prompts(examples, prompt)
        solution = self._generate_and_test_code(prompts, inputs, outputs)

        return solution



    def _find_examples(self, prompt: str) -> list():
        """
        Searches example database for most relevant examples to aid in code generation
        """
        raise NotImplementedError


    def _generate_prompts(self, examples: list(), prompt: str) -> list():
        """
        Given a users prompt and a list of examples, generates a set of prompts for the code model to use

        returns a list of prompts
        """
        raise NotImplementedError
    
    def _generate_and_test_code(self, prompts, inputs, outputs, max_tries=200):
        """
        Takes in a set of prompts and test cases and generates code until a solution passes all of the test cases

        Enhancements: 
            timeout: maximum amount of time to let this run, return the code that passes the most test cases at the end
            threads: number of threads to do this in parallel with
        """

        for i in range(max_tries):



    def _parse_environment(self) -> list():
        """
        Does a pip freeze to see all of the packages installed within the environment
        Can use these to narrow down the prompt search
        """
        raise NotImplementedError
