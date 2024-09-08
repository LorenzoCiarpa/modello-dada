import pandas as pd
import numpy as np
import pandas as pd
from openpyxl import Workbook
from gurobipy import Model, GRB
import time 
import json
from pathlib import Path

from data.galilei.dizionario_professori import prof_to_idx
from constants import *



def generate_t_kog(orario_file, P, G, O):
    # Leggere il file CSV
    df = pd.read_csv(orario_file)

    # Mappare i giorni della settimana a numeri
    day_map = {
        'lunedi': 0,
        'martedi': 1,
        'mercoledi': 2,
        'giovedi': 3,
        'venerdi': 4
    }

    # Creare la matrice t_kog con zeri
    t_kog = np.zeros((P, O, G), dtype=int)

    # Popolare la matrice t_kog
    for idx, row in df.iterrows():
        # print(f"idx: {idx}, row: {row}")
        if idx == 677:
            print(row)
            
        professore = int(prof_to_idx[row['Professore']]) - 1
        giorno = day_map[row['Giorno']]
        ora = int(row['Ora']) - 1

        # if idx == 677:
        #     print(f"prof: {professore}, giorno: {giorno}, ora: {ora}")
        #     print(f"prof: {type(professore)}, giorno: {type(giorno)}, ora: {type(ora)}")

        t_kog[professore, ora, giorno] = 1

    return t_kog

def generate_t_kog_old(orario_file, P, G, O):
    # Leggere il file CSV
    df = pd.read_csv(orario_file)

    # Mappare i giorni della settimana a numeri
    day_map = {
        'Lunedi': 0,
        'Martedi': 1,
        'Mercoledi': 2,
        'Giovedi': 3,
        'Venerdi': 4
    }

    # Creare la matrice t_kog con zeri
    t_kog = np.zeros((P, O, G), dtype=int)

    # Popolare la matrice t_kog
    for _, row in df.iterrows():
        # print(f"row: {row}")
        professore = int(row['Professore']) - 1
        giorno = day_map[row['Giorno']]
        ora = int(row['Ora']) - 1
        t_kog[professore, ora, giorno] = 1

    return t_kog

def generate_p_s(settori_file):
    # Leggere il file CSV
    df = pd.read_csv(settori_file)

    # Definizione dei parametri
    S = len(df['Settore'].unique())  # Numero di settori

    # Creare il dizionario p_s
    p_s = {s: [] for s in range(0, S)}

    # Popolare il dizionario p_s
    for _, row in df.iterrows():
        settore = int(row['Settore'][-1])  # Supponiamo che il formato sia "settore X"
        professore = int(row['Professore']) - 1
        p_s[settore].append(professore)

    return p_s

def generate_p_s_corretto(settori_file):
    # Leggere il file CSV
    df = pd.read_csv(settori_file)

    # Definizione dei parametri
    S = len(df['Settore'].unique())  # Numero di settori

    # Creare il dizionario p_s
    p_s = {s: [] for s in range(0, S)}

    # Popolare il dizionario p_s
    for _, row in df.iterrows():
        # print(row)
        # print(row['Professore'])
        # print(row['Settore'])
        settore = int(row['Settore']) - 1  # Supponiamo che il formato sia "settore X"
        professore = prof_to_idx[str(row['Professore'])] - 1
        p_s[settore].append(professore)

    return p_s



def save_optimal_schedule_to_excel(model, x, P, N, O, G, filename="orario_ottimale.xlsx"):
    # Creazione di una lista per memorizzare le assegnazioni
    schedule_data = []

    # Estrazione della soluzione ottimale
    for k in range(P):
        for l in range(N):
            for o in range(O):
                for g in range(G):
                    if model.getVal(x[k, l, o, g]) > 0.5:
                        schedule_data.append({
                            "Professore": k + 1,
                            "Aula": l + 1,
                            "Ora": o + 1,
                            "Giorno": g + 1
                        })

    # Creazione del DataFrame
    df = pd.DataFrame(schedule_data)

    # Mappare i numeri dei giorni ai nomi dei giorni
    day_map = {1: 'Lunedi', 2: 'Martedi', 3: 'Mercoledi', 4: 'Giovedi', 5: 'Venerdi'}
    df['Giorno'] = df['Giorno'].map(day_map)

    # Salvataggio del DataFrame in un file Excel
    df.to_excel(filename, index=False)




def myCallbacksSolution(model, where):
    
    if where == GRB.Callback.MIPSOL:
        print(f"where: {where}, MIPSOL: {GRB.Callback.MIPSOL}")
        # Ottieni l'ora corrente
        try:
            # Estrazione e salvataggio delle variabili correnti
            save_partial_solution(model)
        except Exception as e:
            print(f"Errore durante il salvataggio della soluzione parziale: {e}")


def save_partial_solution(model):
    # Creazione di un dizionario per memorizzare i risultati parziali
    x = vars['x']
    y = vars['y']
    u = vars['u']
    z_max = vars['z_max']

    solution = {}
    print("arr1")
    
    # Salvare i valori delle variabili x
    solution['x'] = {}
    for k in range(P):
        for l in range(N):
            for o in range(O):
                for g in range(G):
                    val = model.cbGetSolution(x[k, l, o, g])
                    # if val > 0.5:
                    #     solution['x'][(k, l, o, g)] = val
                    solution['x'][(k, l, o, g)] = val

    solution['x'] = {str(key): value for key, value in solution['x'].items()}

    # Salvare i valori delle variabili y
    solution['y'] = {}
    for k in range(P):
        for l in range(N):
            val = model.cbGetSolution(y[k, l])
            # if val > 0.5:
            #     solution['y'][(k, l)] = val
            solution['y'][(k, l)] = val
    
    solution['y'] = {str(key): value for key, value in solution['y'].items()}

    # Salvare i valori delle variabili u
    solution['u'] = {}
    for l in range(N):
        for s in range(S):
            val = model.cbGetSolution(u[l, s])
            # if val > 0.5:
            #     solution['u'][(l, s)] = val
            solution['u'][(l, s)] = val
    
    solution['u'] = {str(key): value for key, value in solution['u'].items()}

    # Salvare il valore di z_max
    solution['z_max'] = model.cbGetSolution(z_max)

    solution['obj_fun'] = model.cbGet(GRB.Callback.MIPSOL_OBJBST)
    print("arr6")
    
    # Salva su file i risultati parziali

    # Path to the directory
    directory = Path(f"{resultFolder}/3")

    # Count files in the directory
    file_count = len(list(directory.glob('*')))

    print(f'Number of files: {file_count}')

    filename = f"{resultFolder}/3/partial_solution_{file_count}.json"
    # Saving dict to JSON file
    with open(filename, 'w') as json_file:
        json.dump(solution, json_file, indent=4)

    print(f'Data saved to {filename}')


# def my_callback(model, where, vars):
#     if where == GRB.Callback.MIPSOL:
#         save_partial_solution(model, vars)

# def optimize_with_callback(model, vars):
#     model.optimize(lambda model, where: my_callback(model, where, vars))

# # Esempio di utilizzo
# model = grb.Model()
# x = model.addVar()
# y = model.addVar()
# vars = {'x': x, 'y': y}

# optimize_with_callback(model, vars)


# def my_callback_old(model, where):
#     if where == GRB.Callback.MIPNODE:
#         # Ottieni l'ora corrente
#         current_time = time.time()
        
#         # Controlla se è il momento di salvare (ogni 5 minuti, ad esempio)
#         if int(current_time - model._last_save_time) >= 300:
#             model._last_save_time = current_time
#             try:
#                 # Estrazione e salvataggio delle variabili correnti
#                 save_partial_solution_old(model)
#             except Exception as e:
#                 print(f"Errore durante il salvataggio della soluzione parziale: {e}")

# def save_partial_solution_old(model):
#     # Creazione di un dizionario per memorizzare i risultati parziali
#     solution = {}
    
#     # Salvare i valori delle variabili x
#     solution['x'] = {}
#     for k in range(P):
#         for l in range(N):
#             for o in range(O):
#                 for g in range(G):
#                     val = model.cbGetNodeRel(x[k, l, o, g])
#                     # if val > 0.5:
#                     #     solution['x'][(k, l, o, g)] = val
#                     solution['x'][(k, l, o, g)] = val
    
#     # Salvare i valori delle variabili y
#     solution['y'] = {}
#     for k in range(P):
#         for l in range(N):
#             val = model.cbGetNodeRel(y[k, l])
#             # if val > 0.5:
#             #     solution['y'][(k, l)] = val
#             solution['y'][(k, l)] = val
    
#     # Salvare i valori delle variabili u
#     solution['u'] = {}
#     for l in range(N):
#         for s in range(S):
#             val = model.cbGetNodeRel(u[l, s])
#             # if val > 0.5:
#             #     solution['u'][(l, s)] = val
#             solution['u'][(l, s)] = val
    
#     # Salvare il valore di z_max
#     solution['z_max'] = model.cbGetNodeRel(z_max)
#     solution['obj_fun'] = model.cbGet(GRB.Callback.MIPNODE_OBJBST)
    
#     # Salva su file i risultati parziali
#     timestamp = time.strftime("%Y%m%d-%H%M%S")
#     filename = f"{resultFolder}/2/partial_solution_{timestamp}.txt"
#     with open(filename, "w") as file:
#         for var, value in solution.items():
#             file.write(f"{var}: {value}\n")
    
#     print(f"Soluzione parziale salvata in {filename}")



if __name__ == '__main__':
    
    # Definizione dei parametri
    P = 12  # Numero di professori
    G = 5   # Numero di giorni (lunedi a venerdi)
    O = 4   # Numero di ore per giorno

    # Utilizzo delle funzioni
    t_kog = generate_t_kog('data/orario.csv', P, G, O)
    # p_s = generate_p_s('data/settori.csv')

    # Stampa dei risultati per verifica
    print("t_kog:", t_kog)
    # print("p_s:", p_s)

    # save_optimal_schedule_to_excel(model, x, P, N, O, G)
