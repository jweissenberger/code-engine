from transformers.generation_stopping_criteria import StoppingCriteria
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import os


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

def model_inference(prompt, temperature=None, top_k=None, top_p=None):
    input_ids = tokenizer(prompt, return_tensors="pt").input_ids

    generated_ids = model.generate(input_ids, do_sample=True, max_length=len(input_ids)+300, temperature=temperature, stopping_criteria=[cf], pad_token_id=2)
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


def local_model_inference(prompt: str, temperature=0.5) -> str:
    model_output = model_inference(prompt, temperature=temperature)
    model_output = clean_up_model_output(model_output)
    return model_output


tokenizer = AutoTokenizer.from_pretrained("Salesforce/codegen-350M-mono")
model = AutoModelForCausalLM.from_pretrained("Salesforce/codegen-350M-mono")
cf = CodeOnlyWithinFunction()
os.environ["TOKENIZERS_PARALLELISM"] = "False"