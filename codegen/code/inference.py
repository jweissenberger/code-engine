from transformers import AutoTokenizer
import torch
import os


def model_fn(model_dir):
  tokenizer = AutoTokenizer.from_pretrained(model_dir)
  model = torch.load(os.path.join(model_dir, "codegen-350-mono.pt"))
  return model, tokenizer

def predict_fn(data, model_and_tokenizer):
    # destruct model and tokenizer
    model, tokenizer = model_and_tokenizer
    
    text = data.pop("inputs", data)
    max_length = data.pop("max_length", 250)
    top_k = data.pop("top_k", None)
    top_p = data.pop("top_p", None)
    no_repeat_ngram_size = data.pop("no_repeat_ngram_size", None)
    temperature = data.pop("temperature", None)
    num_beams = data.pop("num_beams", None)
    # TODO: Add support for num_return_sequences

    input_ids = tokenizer(text, return_tensors="pt").input_ids

    generated_ids = model.generate(
            input_ids, 
            max_length=len(len(input_ids[0])) + max_length,
            top_k=top_k,
            top_p=top_p,
            no_repeat_ngram_size=no_repeat_ngram_size,
            temperature=temperature,
            num_beams=num_beams,
            pad_token_id=2
        )

    output = tokenizer.decode(generated_ids[0], skip_special_tokens=True)
    
    return {"output": output}