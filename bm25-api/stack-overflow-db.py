import pandas as pd
import html
import re
from rank_bm25 import BM25Okapi

class BM25_stack_overflow_db:

    def __init__(self):
        df = pd.read_csv('/Users/jackweissenberger/Documents/code-generation/scraping/stack_overflow_kaggle/data/formatted_dataset.csv')
        self.qs = []
        self.corpus = []
        self.q2a = {}

        # TODO: comment lines not in code blocks in answers
        for i in range(df.shape[0]):
            title = self._clean_html(df.Title.iloc[i])
            question = self._clean_html(df.Question.iloc[i])
            corp_entry = f"{title}\n{question}"
            self.corpus.append(corp_entry)

            question = title + ' ' + question
            question = self._format(question)
            question = self._remove_code_blocks(question)

            self.qs.append(question.split(' '))

            answer = self._clean_html(df.Answer.iloc[i]).replace('  ', ' ').strip()
            self.q2a[corp_entry] = answer
        
        self.bm25 = BM25Okapi(self.qs)
    
    def _remove_code_blocks(string):
        for i in range(30):
            if "<pre><code>" not in string:
                break
            sub = string[string.index("<pre><code>"): string.index("</code></pre>")+13]
            string = string.replace(string, "")
        return string
            

    def _clean_html(html_string):
        html_string = re.sub(r'<.+?>', '', html_string) # removes all tags
        # ^ needs to happen before below because there are no < or > chaaracters in raw html
        html_string = html.unescape(html_string)
        html_string = html_string.replace('\r', '')
        return html_string.strip()

    def _format(string):

        things_to_remove = [
            ('\n', " "), ('.', ""), ('?', ""), ('!', ""), ('(', ""), (')', ""), ('[', ""), (']', ""), ('_', " "), 
            ("'", ""), ('"', ''), (",", ''), ("{", ""), ("}", "")
        ]

        for e in things_to_remove:
            string = string.replace(e[0], e[1])
        
        string = string.replace('  ', ' ').strip().lower()
        return string
    
    def get_documents(self, query, n=1):
        tokenized_query = self._format(query).split(' ')
        documents = self.bm25.get_top_n(tokenized_query, self.corpus, n=n)