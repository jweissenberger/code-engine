import pandas as pd
import html
import re
from rank_bm25 import BM25Okapi
import pickle


def remove_code_blocks(string):
    if "<code class=python>" in string:
        string = string.replace('<code class=python>', "<code>")
    if "</code><pre>" in string:
        string = string.replace("</code><pre>", "</code></pre>")
    for i in range(30):
        if "<pre><code>" not in string or ("<pre><code>" in string and "</pre></code>" not in string):
            break
        try:
            sub = string[string.index("<pre><code>"): string.index("</code></pre>")+13]
        except Exception as e:
            print("in remove code block")
            print(string)
            print(e)
        string = string.replace(sub, "")
    return string
            

def clean_html(html_string):
    html_string = re.sub(r'<.+?>', '', html_string) # removes all tags
    # ^ needs to happen before below because there are no < or > chaaracters in raw html
    html_string = html.unescape(html_string)
    html_string = html_string.replace('\r', '')
    return html_string.strip()

def format(string):

    things_to_remove = [
        ('\n', " "), ('.', ""), ('?', ""), ('!', ""), ('(', ""), (')', ""), ('[', ""), (']', ""), ('_', " "), 
        ("'", ""), ('"', ''), (",", ''), ("{", ""), ("}", "")
    ]

    for e in things_to_remove:
        string = string.replace(e[0], e[1])
    
    string = string.replace('  ', ' ').strip().lower()
    return string

def format_answer(string):
    """
    Because these need to be executable: comment out lines without code and leave code blocks uncommented
    """
    # fix edge cases:
    string = string.replace("</code>\n</pre>", "</code></pre>").replace("</pre></code>", "</code></pre>")

    # get code blocks before removing tags
    start = 0
    uncommented_code_blocks = []
    for i in range(30):
        if "<pre><code>" not in string[start:]:
            break
        front = string.index("<pre><code>", start)
        back = string.index("</code></pre>", start)+13
        sub = string[front: back]
        start = back
        uncommented_code_blocks.append(sub)

    # add # on every line
    string = f"\n{string}".replace('\n', '\n#')

    # get code blocks after (should be equal lengths)
    commented_code_blocks = []
    start = 0
    for i in range(30):
        if "#<pre><code>" not in string[start:]:
            break
        front = string.index("#<pre><code>", start)
        back = string.index("</code></pre>", start)+13
        sub = string[front: back]
        start = back
        commented_code_blocks.append(sub)


    # replace commented code blocks with uncommented code blocks
    for i in range(len(commented_code_blocks)):
        string = string.replace(commented_code_blocks[i], uncommented_code_blocks[i])

    # remove the "#" on lines where theres no characters
    output = []
    for line in string.split('\n'):
        if line == "#":
            output.append("")
        else:
            output.append(line)
    string = "\n".join(output)

    # remove html
    string = clean_html(string)

    return string


if __name__ == '__main__':
    print('Reading File')
    df = pd.read_csv('/Users/jackweissenberger/Documents/code-generation/scraping/stack_overflow_kaggle/data/formatted_dataset.csv')
    qs = []
    corpus = []
    q2a = {}

    for i in range(df.shape[0]):
        if i % 20_000 == 0:
            print(i)
        title = clean_html(df.Title.iloc[i])
        question = clean_html(df.Question.iloc[i])
        corp_entry = f"{title}\n{question}"
        corpus.append(corp_entry)

        question = title + ' ' + question
        question = format(question)
        question = remove_code_blocks(question)

        qs.append(question.split(' '))

        try:
            answer = format_answer(df.Answer.iloc[i])
        except Exception as e:
            print(df.Answer.iloc[i])
            print('\n\n', e)
            exit()

        q2a[corp_entry] = answer
    
    bm25 = BM25Okapi(qs)

    print('Finished formatting, saving')

    # pickle: corpus, bm25 and q2a
    with open('./bm25-files/corpus.pkl', 'wb') as f:
        pickle.dump(corpus, f)
    
    with open('./bm25-files/q2a.pkl', 'wb') as f:
        pickle.dump(q2a, f)

    with open('./bm25-files/bm25.pkl', 'wb') as f:
        pickle.dump(bm25, f)
    
    print("DONE")