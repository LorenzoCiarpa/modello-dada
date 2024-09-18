import pandas as pd
import numpy as np
from gurobipy import Model, GRB
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
            
        professore = int(prof_to_idx[row['Professore']]) - 1
        giorno = day_map[row['Giorno']]
        ora = int(row['Ora']) - 1


        t_kog[professore, ora, giorno] = 1

    return t_kog

def generate_p_s_corretto(settori_file):
    # Leggere il file CSV
    df = pd.read_csv(settori_file)

    # Definizione dei parametri
    S = len(df['Settore'].unique())  # Numero di settori

    # Creare il dizionario p_s
    p_s = {s: [] for s in range(0, S)}

    # Popolare il dizionario p_s
    for _, row in df.iterrows():

        settore = int(row['Settore']) - 1  # Supponiamo che il formato sia "settore X"
        professore = prof_to_idx[str(row['Professore'])] - 1
        p_s[settore].append(professore)

    return p_s





def myCallbacksSolution(model, where):
    
    if where == GRB.Callback.MIPSOL:
        print(f"where: {where}, MIPSOL: {GRB.Callback.MIPSOL}")
        try:
            # Estrazione e salvataggio delle variabili correnti
            save_partial_solution(model)

        except Exception as e:
            print(f"Errore durante il salvataggio della soluzione parziale: {e}")


def save_partial_solution(model):
    x = vars['x']
    y = vars['y']
    u = vars['u']
    z_max = vars['z_max']

    solution = {}
    
    # Salvare i valori delle variabili x
    solution['x'] = {}
    for k in range(P):
        for l in range(N):
            for o in range(O):
                for g in range(G):
                    val = model.cbGetSolution(x[k, l, o, g])
                    solution['x'][(k, l, o, g)] = val

    solution['x'] = {str(key): value for key, value in solution['x'].items()}

    # Salvare i valori delle variabili y
    solution['y'] = {}
    for k in range(P):
        for l in range(N):
            val = model.cbGetSolution(y[k, l])
            solution['y'][(k, l)] = val
    
    solution['y'] = {str(key): value for key, value in solution['y'].items()}

    # Salvare i valori delle variabili u
    solution['u'] = {}
    for l in range(N):
        for s in range(S):
            val = model.cbGetSolution(u[l, s])
            solution['u'][(l, s)] = val
    
    solution['u'] = {str(key): value for key, value in solution['u'].items()}

    # Salvare il valore di z_max
    solution['z_max'] = model.cbGetSolution(z_max)

    solution['obj_fun'] = model.cbGet(GRB.Callback.MIPSOL_OBJBST)

     # Salvare il gap
    best_solution = model.cbGet(GRB.Callback.MIPSOL_OBJBST)  # Best found solution
    best_bound = model.cbGet(GRB.Callback.MIPSOL_OBJBND)     # Best bound (lower/upper)
    mip_gap = abs(best_solution - best_bound) / max(1e-10, abs(best_solution))
    solution['mip_gap'] = mip_gap
    
    # Salvare il tempo impiegato
    runtime = model.cbGet(GRB.Callback.RUNTIME)
    solution['runtime'] = runtime

    
    # Salva su file i risultati parziali

    # Path to the directory
    directory = Path(f"{resultFolder}/{runNumber}")

    # Count files in the directory
    file_count = len(list(directory.glob('*')))

    # print(f'Number of files: {file_count}')

    filename = f"{resultFolder}/{runNumber}/partial_solution_{file_count}.json"
    # Saving dict to JSON file
    with open(filename, 'w') as json_file:
        json.dump(solution, json_file, indent=4)

    print(f'Data saved to {filename}')


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
