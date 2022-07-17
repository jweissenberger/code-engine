from transformers.generation_stopping_criteria import StoppingCriteria
import torch
import json
import pandas as pd
import  requests
from execution import check_correctness
from transformers import AutoTokenizer, AutoModelForCausalLM
import random

class CodeOnlyWithinFunction(StoppingCriteria):
    """
    This is the stopping criteria for code generation models such that they only generate code
    that starts each line with a tab. This restrics the models from generating code outside
    of a function.
    """

    def __call__(self, input_ids: torch.LongTensor, scores: torch.FloatTensor, **kwargs) -> bool:
        """
        Args:
            input_ids (`torch.LongTensor` of shape `(batch_size, sequence_length)`):
                Indices of input sequence tokens in the vocabulary.

                Indices can be obtained using [`BertTokenizer`]. See [`PreTrainedTokenizer.encode`] and
                [`PreTrainedTokenizer.__call__`] for details.

                [What are input IDs?](../glossary#input-ids)
            scores (`torch.FloatTensor` of shape `(batch_size, config.vocab_size)`):
                Prediction scores of a language modeling head. These can be scores for each vocabulary token before SoftMax
                or scores for each vocabulary token after SoftMax.
            kwargs:
                Additional stopping criteria specific kwargs.

        Return:
            `bool`. `False` indicates we should continue, `True` indicates we should stop.
        """

        # decode
        splits = tokenizer.decode(input_ids[0]).split('\n')

        for i in reversed(range(len(splits))):
            if splits[i] == '' or len(splits[i]) == 0:
                continue
            if splits[i].startswith('def '):
                # this is the case where we have gotten back to the function definion and can allow lines without tabs
                return False
            if not splits[i][0].isspace():
                # stop generation
                return True
        
        return False


def find_examples(docstrings: str, num_examples: int=10) -> list:
    """
    Searches example database for most relevant examples to aid in code generation
    """
    # currently hit local running bm25 database
    url = "http://127.0.0.1:8000/get_answers"
    data = {"query": docstrings, "n_answers": num_examples}
    r = requests.post(url=url, json=data)
    answers = r.json()["answers"]
    return answers

def model_inference(prompt):
    # TODO: add parameters for temp, topk p etc
    input_ids = tokenizer(prompt, return_tensors="pt").input_ids

    generated_ids = model.generate(input_ids, max_length=1024, temperature=0.2, stopping_criteria=[cf], pad_token_id=2)
    return tokenizer.decode(generated_ids[0], skip_special_tokens=True)

def clean_up_model_output(model_output):
    splits = model_output.split('\n')
    for i in reversed(range(len(splits))):
        if splits[i] == '' or len(splits[i]) == 0:
            continue
        if splits[i][0].isspace():
            splits = splits[:i+1]
            break
    return '\n'.join(splits)

def find_examples(docstrings: str, num_examples: int=10) -> list:
    """
    Searches example database for most relevant examples to aid in code generation
    """
    # currently hit local running bm25 database
    url = "http://127.0.0.1:8000/get_answers"
    data = {"query": docstrings, "n_answers": num_examples}
    r = requests.post(url=url, json=data)
    answers = r.json()["answers"]
    return answers


def extract_docstrings(full_prompt):
    return full_prompt.strip().split('"""')[-2].strip().split('>>>')[0].strip()


tokenizer = AutoTokenizer.from_pretrained("../codegen/350-mono-tokenizer")
model = AutoModelForCausalLM.from_pretrained("../codegen/350-mono-model")

if __name__ == "__main__":


    test_name = "Code-gen-350"
    model_name = "codegen_350M"
    num_tries_per_question = 200
    num_search_documents = 5


    f = open('/Users/jackweissenberger/Documents/human-eval/data/HumanEval.jsonl', 'r')
    file = f.readlines()
    f.close()

    cf = CodeOnlyWithinFunction()

    results = []

    for i in range(len(file)):

        q = json.loads(file[i])

        # get docstrings
        docstrigns = extract_docstrings(q['prompt'])

        # search for examples
        examples = find_examples(docstrigns, num_examples=num_search_documents)

        for k in num_tries_per_question:

            example = random.choice(examples)

            example_and_prompt = f"{example}\n\n{q['prompt']}"

            model_output = model_inference(example_and_prompt)
            model_output = clean_up_model_output(model_output)

            output_with_test_case = f"{model_output}\n\n{q['test']}"

            timeout = 15.0
            result = check_correctness(output_with_test_case, timeout)

            row = {
                "question": i,
                "attempt": k,
                "passed": result['passed'],
                "result": result['result'],
                "test_name": test_name,
                "model_name": model_name
            }
            results.append(row)

            pd.DataFrame(results).to_csv(f'{test_name}.csv', index=False)
    
    #TODO: Calculate pass@K value
