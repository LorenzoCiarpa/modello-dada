from pyscipopt import Model
import numpy as np
from utils import generate_t_kog, generate_p_s, save_optimal_schedule_to_excel

np.random.seed(0)

# Definizione dei parametri
P = 12  # Numero di professori
N = 2  # Numero di aule (uguale al numero di classi)
G = 5  # Numero di giorni
O = 4  # Numero di ore per giorno

# Definizione del parametro t_kog (qui con valori casuali per esempio)

t_kog = generate_t_kog('data/orario.csv', P, G, O)

# Creazione del modello
model = Model("Assegnazione_Aule")

# Definizione delle variabili di decisione
x = {}
for k in range(P):
    for l in range(N):
        for o in range(O):
            for g in range(G):
                x[k, l, o, g] = model.addVar(vtype="B", name=f"x_{k}_{l}_{o}_{g}")

y = {}
for k in range(P):
    for l in range(N):
        y[k, l] = model.addVar(vtype="B", name=f"y_{k}_{l}")

# Funzione obiettivo: minimizzare il numero di aule associate
model.setObjective(sum(y[k, l] for k in range(P) for l in range(N)), sense="minimize")

# Vincolo 1: Assegnazione di un'aula quando c'è lezione
for k in range(P):
    for o in range(O):
        for g in range(G):
            model.addCons(sum(x[k, l, o, g] for l in range(N)) == t_kog[k, o, g])

# Vincolo 2: Utilizzo orario singolo di un'aula
for l in range(N):
    for o in range(O):
        for g in range(G):
            model.addCons(sum(x[k, l, o, g] for k in range(P)) <= 1)

# Vincolo 3: Relazione tra aula e professore
for l in range(N):
    for k in range(P):
        for o in range(O):
            for g in range(G):
                model.addCons(x[k, l, o, g] <= y[k, l])

# Vincolo 4: Copertura delle aule
for l in range(N):
    for k in range(P):
        model.addCons(y[k, l] <= sum(x[k, l, o, g] for o in range(O) for g in range(G)))

# Risoluzione del problema
model.optimize()

# Estrazione e stampa della soluzione
if model.getStatus() == "optimal":
    total_y = sum(model.getVal(y[k, l]) for k in range(P) for l in range(N))
    print(f"Somma totale di tutte le variabili y: {total_y}")

    for g in range(G):
        for o in range(O):
            for k in range(P):
                for l in range(N):
                    if model.getVal(x[k, l, o, g]) > 0.5:
                        print(f"Professore {k} assegnato all'aula {l} nell'ora {o} del giorno {g}")

    for k in range(P):
        for l in range(N):
            if model.getVal(y[k, l]) > 0.5:
                print(f"Aula {l} usata dal professore {k}")

    save_optimal_schedule_to_excel(model, x, P, N, O, G, filename="orario_ottimale-3-obj1.xlsx")
    
else:
    print("Non è stata trovata una soluzione ottimale.")
