from fastapi import FastAPI
from pydantic import BaseModel
import pickle

app = FastAPI()

class DocRequest(BaseModel):
    query: str
    n_answers: int = 3

@app.post("/get_answers")
async def get_answers(docRequest: DocRequest):
    docRequest = docRequest.dict()
    query = docRequest['query']
    n = docRequest['n_answers']

    tokenized_query = tokenize(query)

    question_documents = bm25.get_top_n(tokenized_query, corpus, n=n)

    answers = []
    for doc in question_documents:
        answers.append(q2a[doc])

    return {"answers": answers}


def tokenize(string: str) -> list:
    string = format(string)
    string = string.split(' ')
    return string


def format(string):

    things_to_remove = [
        ('\n', " "), ('.', ""), ('?', ""), ('!', ""), ('(', ""), (')', ""), ('[', ""), (']', ""), ('_', " "), 
        ("'", ""), ('"', ''), (",", ''), ("{", ""), ("}", "")
    ]

    for e in things_to_remove:
        string = string.replace(e[0], e[1])
    
    string = string.replace('  ', ' ').strip().lower()
    return string

print('Loading BM25 Info')
with open('../scraping/stack_overflow_kaggle/bm25-files/corpus.pkl', 'rb') as f:
    corpus = pickle.load(f)
    
with open('../scraping/stack_overflow_kaggle/bm25-files/q2a.pkl', 'rb') as f:
    q2a = pickle.load(f)

with open('../scraping/stack_overflow_kaggle/bm25-files/bm25.pkl', 'rb') as f:
    bm25 = pickle.load(f)
print('Ready to go')

