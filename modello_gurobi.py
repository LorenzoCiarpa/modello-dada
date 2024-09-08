from gurobipy import Model, GRB
import numpy as np
import os
import time
from pathlib import Path
import json
from constants import *
from utils import generate_t_kog, generate_p_s, generate_p_s_corretto, save_optimal_schedule_to_excel, myCallbacksSolution
from read_var import read_init_vars_json

np.random.seed(0)



if not os.path.exists(resultFolder):
    os.makedirs(resultFolder)
    print(f"Cartella '{resultFolder}' creata.")
else:
    print(f"Cartella '{resultFolder}' esiste già.")

t_kog = generate_t_kog(f'data/{testFolder}/orario-bk.csv', P, G, O)
p_s = generate_p_s_corretto(f'data/{testFolder}/prof-settori.csv')

print(p_s)



# Funzione obiettivo: minimizzare il numero di aule associate, la differenza tra aule assegnate e il numero di settori per aula
model.setObjective(
    alpha * sum(y[k, l] for k in range(P) for l in range(N)) + 
    beta * z_max + 
    gamma * sum(u[l, s] for l in range(N) for s in range(S)),
    GRB.MINIMIZE
)

# Vincolo 1: Assegnazione di un'aula quando c'è lezione
model.addConstrs(
    (x.sum(k, '*', o, g) == t_kog[k, o, g] for k in range(P) for o in range(O) for g in range(G)),
    name="v1"
)

# Vincolo 2: Utilizzo orario singolo di un'aula
model.addConstrs(
    (x.sum('*', l, o, g) <= 1 for l in range(N) for o in range(O) for g in range(G)),
    name="v2"
)

# Vincolo 3: Relazione tra aula e professore
model.addConstrs(
    (x[k, l, o, g] <= y[k, l] for k in range(P) for l in range(N) for o in range(O) for g in range(G)),
    name="v3"
)

# Vincolo 4: Copertura delle aule
model.addConstrs(
    (y[k, l] <= x.sum(k, l, '*', '*') for k in range(P) for l in range(N)),
    name="v4"
)

# Vincolo 5: Numero di aule associate al professore k
model.addConstrs(
    (z_max >= y.sum(k, '*') for k in range(P)),
    name="v5"
)

# Vincolo 7: Condizione di utilizzo dell'aula l per il settore s
model.addConstrs(
    (u[l, s] >= y[k, l] for l in range(N) for s in range(S) for k in p_s[s]),
    name="v7"
)

# Salvare il modello
# model.write('problem.lp')

# Impostazione del tempo iniziale per il salvataggio periodico
model._last_save_time = time.time()

#Inizializzazione warm start
variables = read_init_vars_json('./results/galilei/3/partial_solution_9.json')
x_start = variables['x']
y_start = variables['y']
u_start = variables['u']
z_max_start = variables['z_max']

for idx in x_start.keys():
    k,l,o,g = idx.replace('(', '').replace(')', '').split(',')
    k,l,o,g = int(k), int(l), int(o), int(g)
    x[k,l,o,g].Start = x_start[idx]

for idx in y_start.keys():
    k,l = idx.replace('(', '').replace(')', '').split(',')
    k,l = int(k), int(l)
    y[k,l].Start = y_start[idx]

for idx in u_start.keys():
    k,l = idx.replace('(', '').replace(')', '').split(',')
    k,l = int(k), int(l)
    u[k,l].Start = u_start[idx]

z_max = z_max_start

# Avvio dell'ottimizzazione con il callback
model.optimize(myCallbacksSolution)

# # Estrazione e stampa della soluzione
# if model.status == GRB.OPTIMAL:
#     total_y = sum(y[k, l].x for k in range(P) for l in range(N))
#     print(f"Somma totale di tutte le variabili y: {total_y}")

#     for g in range(G):
#         for o in range(O):
#             for k in range(P):
#                 for l in range(N):
#                     if x[k, l, o, g].x > 0.5:
#                         print(f"Professore {k} assegnato all'aula {l} nell'ora {o} del giorno {g}")

#     for k in range(P):
#         for l in range(N):
#             if y[k, l].x > 0.5:
#                 print(f"Aula {l} usata dal professore {k}")

#     # save_optimal_schedule_to_excel(model, x, P, N, O, G, filename=f"{resultFolder}/orario_ottimale-3-obj3.xlsx")

#     objective_value = model.ObjVal
#     print(f"Valore della funzione obiettivo: {objective_value}")

# else:
#     print("Non è stata trovata una soluzione ottimale.")


# Estrazione e salvataggio dei valori delle variabili al termine dell'ottimizzazione
if model.status == GRB.OPTIMAL:
    # Creazione di un dizionario per memorizzare i risultati
    solution = {}
    
    # Salvare i valori delle variabili x
    solution['x'] = {(k, l, o, g): x[k, l, o, g].x 
                     for k in range(P) for l in range(N) for o in range(O) for g in range(G)
                     if x[k, l, o, g].x > 0.5}
    
    # Salvare i valori delle variabili y
    solution['y'] = {(k, l): y[k, l].x 
                     for k in range(P) for l in range(N)
                     if y[k, l].x > 0.5}
    
    # Salvare i valori delle variabili u
    solution['u'] = {(l, s): u[l, s].x 
                     for l in range(N) for s in range(S)
                     if u[l, s].x > 0.5}
    
    # Salvare il valore di z_max
    solution['z_max'] = z_max.x
    
    # Stampa o salva su file i risultati
    print("Valori delle variabili salvati con successo!")
    
    # Ad esempio, per salvare su un file
    with open(f"{resultFolder}/solution.txt", "w") as file:
        for var, value in solution.items():
            file.write(f"{var}: {value}\n")
else:
    print("Non è stata trovata una soluzione ottimale.")
