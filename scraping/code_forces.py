import os
import requests

if __name__ == '__main__':

    #print(os.listdir('../../CodeForces/problems/A/'))
    f = open('../../CodeForces/problems/A/AddOddOrSubtractEven.py', 'r')
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
    
    r = requests.get(url)

    print(r.text)
