

class TDD:

    def __init__(self, user_id="", password=""):

        self.user_id = user_id
        self.password = password
    
    def generate_code(self, prompt: str, inputs: list(), outputs: list(), output_type="string"):
        """
        
        """
        examples = self.find_examples(prompt)
        prompts = self.generate_promopts(examples, prompt)

    def find_examples(self, prompt):
        """"""
        raise NotImplementedError

