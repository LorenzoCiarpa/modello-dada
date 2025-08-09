import re
import json
import numpy as np

# Definisci i range degli indici per ogni variabile
k_range = range(102)  # 0 to 101
l_range = range(53)   # 0 to 52
o_range = range(8)    # 0 to 7
G_range = range(5)    # 0 to 4
S_range = range(3)    # 0 to 2

# Inizializza i dizionari con tutti i valori a 0.0
# x_values = {(k, l, o, G): 0.0 for k in k_range for l in l_range for o in o_range for G in G_range}
# y_values = {(k, l): 0.0 for k in k_range for l in l_range}
# u_values = {(l, S): 0.0 for l in l_range for S in S_range}

x_values = {}
y_values = {}
u_values = {}
z_max_value = 0.0  # Inizializza z_max a 0.0

# Leggi il file

def read_init_vars(path = './results/galilei/partial_solution_20240831-105435.txt'):
    with open(path, 'r') as file:
        for line in file:
            # Parse variabili x
            x_match = re.match(r"x:\s*{(.+)}", line.strip())
            if x_match:
                x_items = x_match.group(1).split(", (")
                for item in x_items:
                    indices, value = item.split(": ")
                    k, l, o, G = map(int, re.findall(r"\d+", indices))

                    # print(f"item: {item}")
                    # print(f"indices : {k, l, o, G}")

                    x_values[(k, l, o, G)] = float(value)  # Imposta a 1.0 indipendentemente dal valore originale

                    # x_values[(k, l, o, G)] = 1 if float(value) > 0.0 else 0.0  # Imposta a 1.0 indipendentemente dal valore originale

            # Parse variabili y
            y_match = re.match(r"y:\s*{(.+)}", line.strip())
            if y_match:
                y_items = y_match.group(1).split(", (")
                for item in y_items:
                    indices, value = item.split(": ")
                    k, l = map(int, re.findall(r"\d+", indices))

                    # print(f"item: {item}")
                    # print(f"indices : {k, l}")

                    y_values[(k, l)] = float(value)  # Imposta a 1.0 indipendentemente dal valore originale
                    # y_values[(k, l)] = 1 if float(value) > 0.0 else 0.0  # Imposta a 1.0 indipendentemente dal valore originale

            # Parse variabili u
            u_match = re.match(r"u:\s*{(.+)}", line.strip())
            if u_match:
                u_items = u_match.group(1).split(", (")
                for item in u_items:
                    indices, value = item.split(": ")
                    l, S = map(int, re.findall(r"\d+", indices))

                    # print(f"item: {item}")
                    # print(f"indices : {l, S}")

                    u_values[(l, S)] = float(value)  # Imposta a 1.0 indipendentemente dal valore originale
                    # u_values[(l, S)] = 1 if float(value) > 0.0 else 0.0  # Imposta a 1.0 indipendentemente dal valore originale

            # # Parse variabile z_max
            z_max_match = re.match(r"z_max:\s*(\d+.\d+)", line.strip())
            if z_max_match:
                z_items = z_max_match.group(1).split(": ")
                print(f"z_items: {z_items}")
                z_max_value = float(z_items[0])  # Imposta a 1.0 indipendentemente dal valore originale

        return x_values, y_values, u_values, z_max_value

def read_init_vars_json(path):
    with open(path, 'r') as file:
        vars = json.load(file)

        return vars


if __name__ == '__main__':
    # x_values, y_values, u_values, z_values = read_init_vars('./results/galilei/2/partial_solution_20240903-075039.txt')
    variables = read_init_vars_json('./results/galilei/4/partial_solution_23.json')
    x_values = variables['x']
    y_values = variables['y']
    u_values = variables['u']
    z_max_values = variables['z_max']

    # y_values = {eval(k): v for k, v in y_values.items()}

    # print(z_max_values)
    # print(x_values.keys())

    # for idx in x_values.keys():
    #     k,l,o,g = idx.replace('(', '').replace(')', '').split(',')
    #     print(k,l,o,g)


    # print(x_values[5, 12, 0, 1])
    # print(y_values[5, 12])

    # Le variabili ora contengono i valori corretti:
    # - x_values[(k, l, o, G)] per la variabile x
    # - y_values[(k, l)] per la variabile y
    # - u_values[(l, S)] per la variabile u
    # - z_max_value per la variabile z_max


    # print(f"z_max: {z_max_value}")
    # print(y_values)



    #GET OBJECTIVE FUNCTIONS PARTS

    y_sum = 0
    for i in range(102):
        for j in range(53):
            y_sum += y_values[f"{i,j}"]

    u_sum = 0
    for i in range(53):
        for j in range(3):
            u_sum += u_values[f"{i,j}"]

    print(f"y_sum: {y_sum}")
    print(f"u_sum: {u_sum}")
    print(f"z_max: {z_max_values}")

    y_max = []

    for i in range(102):
        somma = 0
        for j in range(53):
            somma += y_values[f"{i,j}"]
        y_max.append(somma)

    print(y_max)    
    print(min(y_max))

    print(f"obj_fun: {y_sum + z_max_values}")

    y_max = np.array(y_max)
    print(y_max.argmin())


    from data.galilei.dizionario_professori import prof_to_idx 
    import pandas as pd
    from constants import *

    df = pd.read_csv(f'data/{testFolder}/{settoreFile}')
    
    # Recupera le classi che soddisfano il filtro

    idx_to_prof = {v: k for k, v in prof_to_idx.items()}
    prof_classi = {}

    for idx, elem in enumerate(y_max):
        filtro = (df['Professore'] == idx_to_prof[idx + 1]) 
        settore = df.loc[filtro, 'Settore']
        

        prof_classi[idx_to_prof[idx+1]] = str([elem, settore.values[0]])

    print(prof_classi)
    with open('prof_classi.json', 'w') as json_file:
        json.dump(prof_classi, json_file, indent=4)









    # # for l in range(53):
    #     if x_values[6, l, 0, 2] == 1:
    #         print(f"aula: {l}")

    # print(y_values[0, 0])
    # print(u_values[0, 1])

    # for k in range(1, 102):
    #     if x_values[k, 0, 0, 4] !=0 :
    #         print(f"aula: {l}")

    # print(f"somma : {somma}")

