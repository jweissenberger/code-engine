data = [
    {
        'prompt': "#dropt duplicates from column 'text' from the dataframe",
        'examples': [
            "# To remove duplicates on specific column(s), use subset.\ndf.drop_duplicates(subset=['brand'])",
            "# To remove duplicates and keep last occurrences, use keep.\ndf.drop_duplicates(subset=['brand', 'style'], keep='last')"
            ],
        'answer': "df.drop_duplicates(subset=['text'])"
    },
    {
        'prompt': "rows = [{'company': 'amazon', 'revenue': 100}, {'company': 'facebook', 'revenue': 200}]\n# create a dataframe from list",
        'examples':[
            "d = {'col1': [1, 2], 'col2': [3, 4]}\ndf = pd.DataFrame(d)",
            "data = [{'col1': 1, 'col2': 3}, {'col1': 2, 'col2': 4}]\ndf = pd.DataFrame(data)"
        ],
        'answer': "df = pd.DataFrame(rows)"
    }
]