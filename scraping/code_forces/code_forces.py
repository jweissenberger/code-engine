import os
import requests
from bs4 import BeautifulSoup
import pickle

if __name__ == '__main__':

    code_solutions = []
    full_problem_statements = []
    problem_statment_texts = []
    problem_statment_examples = []

    for problem_set in ['A', 'B', 'C', 'G']:
        for problem_file in os.listdir(f'../../../CodeForces/problems/{problem_set}'):
            if not problem_file.endswith('.py'):
                continue

            f = open(f'../../../CodeForces/problems/{problem_set}/{problem_file}', 'r')
            file = f.read()
            f.close()

            code_solution = []
            in_solution = False
            for line in file.splitlines():
                if line.startswith('https://'):
                    url = line
                if line.startswith('if __name__ == '):
                    in_solution = False
                    break
                if in_solution:
                    code_solution.append(line)
                if line.startswith('def '):
                    in_solution = True
                    code_solution.append(line)
            
            code_solution_string = '\n'.join(code_solution).strip()
            
            # r = requests.get(url)
            # problem = r.text
            # f = open(f'./data/raw_html/{problem_file.replace(".py", "")}.txt', 'w')
            # f.write(problem)
            # f.close()

            f = open(f'../problem_file.txt', 'r')
            problem = f.read()
            f.close()

            soup = BeautifulSoup(problem, 'html.parser')

            soup.find("div", class_="header").decompose()
            problem_statement_div = soup.find("div", class_="problem-statement")
            response = problem_statement_div.text.replace("$$$", "").replace(".ExampleInput", ". Example:\nInput")
            response = response.replace("\le", "<=").replace("\ge", ">=").replace('.Input','.\nInput:').replace('.Output','.\nOutput:')
            response = response[:response.find("\nNote")]
            full_problem_statements.append(response)
            problem_statment_texts.append(response[:response.find(" Example:\n")].strip())
            problem_statment_examples.append(response[response.find(" Example:\n"):].strip())
    
    with open("./data/full_problem_statements.pkl", 'wb') as f:
        pickle.dump(full_problem_statements, f)
    with open("./data/problem_statment_texts.pkl", 'wb') as f:
        pickle.dump(problem_statment_texts, f)
    with open("./data/problem_statment_examples.pkl", 'wb') as f:
        pickle.dump(problem_statment_examples, f)

    