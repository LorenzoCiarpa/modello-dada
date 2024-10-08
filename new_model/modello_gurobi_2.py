#IMPORT LIBRARIES
from gurobipy import Model, GRB
import numpy as np
import os

#INIT SEEDS
np.random.seed(0)

#IMPORT FUNCTIONS
from constants import *
from utils import generate_t_kogc, generate_p_s_corretto, generate_l_f, myCallbacksSolution
from read_var import read_init_vars_json



#CREATE SAVING FOLDER
if not os.path.exists(resultFolder):
    os.makedirs(resultFolder)
    print(f"Cartella '{resultFolder}' creata.")
else:
    print(f"Cartella '{resultFolder}' esiste già.")


#INIT PARAMETERS
t_kog = generate_t_kogc(f'data/{testFolder}/{orarioFile}', P, G, O)
p_s = generate_p_s_corretto(f'data/{testFolder}/{settoreFile}')
l_f = generate_l_f()




# Funzione obiettivo: minimizzare il numero di aule associate, la differenza tra aule assegnate e il numero di settori per aula
model.setObjective(
    alpha * sum(y[k, l] for k in range(P) for l in range(N)) + 
    beta * z_max + 
    gamma * sum(w[f, c, g] for f in range(F) for c in range(C) for g in range(G)),
    # gamma * w.sum('*', '*', '*')
    GRB.MINIMIZE
)

# Vincolo 1: Assegnazione di un'aula quando c'è lezione
model.addConstrs(
    (x.sum(k, '*', o, g, c) == t_kog[k, o, g, c] for k in range(P) for o in range(O) for g in range(G) for c in range(C)),
    name="v1"
)

# Vincolo 2: Utilizzo orario singolo di un'aula
model.addConstrs(
    (x.sum('*', l, o, g, '*') <= 1 for l in range(N) for o in range(O) for g in range(G)),
    name="v2"
)

# Vincolo 3: Relazione tra aula e professore
model.addConstrs(
    (x[k, l, o, g, c] <= y[k, l] for k in range(P) for l in range(N) for o in range(O) for g in range(G) for c in range(C)),
    name="v3"
)

# Vincolo 4: Copertura delle aule
model.addConstrs(
    (y[k, l] <= x.sum(k, l, '*', '*', '*') for k in range(P) for l in range(N)),
    name="v4"
)

# Vincolo 5: Numero di aule associate al professore k
model.addConstrs(
    (z_max >= y.sum(k, '*') for k in range(P)),
    name="v5"
)

# Vincolo 6: Condizione di utilizzo dell'aula l per il settore s
model.addConstrs(
    (u[l, s] >= y[k, l] for l in range(N) for s in range(S) for k in p_s[s]),
    name="v6"
)

# Vincolo 7: Condizione di vincolo che un aula è assegnata ad un solo settore
model.addConstrs(
    (u.sum(l, '*') == 1 for l in range(N)),
    name="v7"
)

# Vincolo 8: Collegamento piani frequentati da una classe in un giorno
model.addConstrs(
    (w[f, c, g] >= x[k, l, o, g, c] for f in range(F) for k in range(P) for l in l_f[f] for o in range(O) for g in range(G) for c in range(C)),
    name="v8"
)

# Salvare il modello
model.write('./problem_formulations/problem_new_2.lp')

'''
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
'''

# Avvio dell'ottimizzazione con il callback
model.optimize(myCallbacksSolution)


# Estrazione e salvataggio dei valori delle variabili al termine dell'ottimizzazione
if model.status == GRB.OPTIMAL:
    # Creazione di un dizionario per memorizzare i risultati
    solution = {}
    
    # Salvare i valori delle variabili x
    solution['x'] = {(k, l, o, g, c): x[k, l, o, g, c].x 
                     for k in range(P) for l in range(N) for o in range(O) for g in range(G) for c in range(C)
                     if x[k, l, o, g, c].x > 0.5}
    
    # Salvare i valori delle variabili y
    solution['y'] = {(k, l): y[k, l].x 
                     for k in range(P) for l in range(N)
                     if y[k, l].x > 0.5}
    
    # Salvare i valori delle variabili u
    solution['u'] = {(l, s): u[l, s].x 
                     for l in range(N) for s in range(S)
                     if u[l, s].x > 0.5}
    
    # Salvare i valori delle variabili w
    solution['w'] = {(f, c, g): w[f, c, g].x 
                     for f in range(F) for c in range(C) for g in range(G)
                     if w[f, c, g].x > 0.5}
    
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
