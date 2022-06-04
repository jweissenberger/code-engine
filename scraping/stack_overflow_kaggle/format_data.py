import pandas as pd
import html
import re

# data from: https://www.kaggle.com/datasets/stackoverflow/pythonquestions?resource=download&select=Questions.csv

if __name__ == '__main__':
    ans = pd.read_csv('./data/archive/Answers.csv', on_bad_lines='skip', encoding = "ISO-8859-1")
    ans["time"] = pd.to_datetime(ans['CreationDate'],infer_datetime_format=True)
    years = []
    for i in range(ans.shape[0]):
        years.append(ans.time.iloc[i].year)
    ans['year'] = years

    qs = pd.read_csv('./data/archive/Questions.csv', on_bad_lines='skip', encoding = "ISO-8859-1")

    # drop all answers before 2012
    ans = ans[ans.year > 2011]

    # get the best answer for each question
    idx = ans.groupby(['ParentId'])['Score'].transform(max) == ans['Score']
    ans = ans[idx]
    # some answers have the same score, so drop duplicates
    ans = ans.drop_duplicates(subset=['ParentId', 'Score'])

    # drop all questions that don't have an answer
    ans_ids = set(ans.ParentId.tolist())
    qs = qs[qs['Id'].isin(ans_ids)]

    # drop all answers that don't have a  question
    qs_ids = set(qs.Id.tolist())
    ans = ans[ans['ParentId'].isin(qs_ids)]

    total = pd.merge(
            qs[["Title", "Body", "Id"]].rename(columns={"Body": "Question"}), 
            ans[["Body", "ParentId"]].rename(columns={"ParentId": "Id", "Body": "Answer"}), 
            how="left", 
            on="Id"
        )

    total.to_csv("./data/formatted_dataset.csv", index=False)