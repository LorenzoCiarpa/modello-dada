from pyscipopt import Model
import numpy as np
import os

from utils import generate_t_kog, generate_p_s, generate_p_s_corretto, save_optimal_schedule_to_excel


np.random.seed(0)



# Definizione dei parametri
P = 102  # Numero di professori
N = 53  # Numero di aule (uguale al numero di classi)
G = 1  # Numero di giorni
O = 1  # Numero di ore per giorno
S = 3  # Numero di settori
alpha = 1
beta = 1
gamma = 1

# Definizione del parametro t_kog (qui con valori casuali per esempio)

testFolder = 'galilei'
resultFolder = f'results/{testFolder}'


# Specifica il percorso della cartella

# Controlla se la cartella esiste, se non esiste, creala
if not os.path.exists(resultFolder):
    os.makedirs(resultFolder)
    print(f"Cartella '{resultFolder}' creata.")
else:
    print(f"Cartella '{resultFolder}' esiste già.")


# t_kog = np.random.randint(2, size=(P, O, G))
t_kog = generate_t_kog(f'data/{testFolder}/orario.csv', P, G, O)

# Definizione del set p(s) (qui con valori casuali per esempio)
# p_s = {s: np.random.choice(range(P), size=P//S, replace=False) for s in range(S)}
p_s = generate_p_s_corretto(f'data/{testFolder}/prof-settori.csv')

print(p_s)

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
        y[k, l] = model.addVar(vtype="C", name=f"y_{k}_{l}") #mettere continue

# z = {}
# for k in range(P):
#     z[k] = model.addVar(vtype="I", name=f"z_{k}")

z_max = model.addVar(vtype="C", name=f"z_max")

u = {}
for l in range(N):
    for s in range(S):
        u[l, s] = model.addVar(vtype="B", name=f"u_{l}_{s}")

# h = {}
# for l in range(N):
#     h[l] = model.addVar(vtype="I", name=f"h_{l}")

# Funzione obiettivo: minimizzare il numero di aule associate, la differenza tra aule assegnate e il numero di settori per aula
model.setObjective(
    alpha * sum(sum(y[k, l] for l in range(N)) for k in range(P)) + 
    
    beta * z_max + 
    gamma * sum(sum(u[l, s] for s in range(S)) for l in range(N)),
    sense="minimize"
)

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

# Vincolo 5: Numero di aule associate al professore k
for k in range(P):
    model.addCons(z_max >= sum(y[k, l] for l in range(N)))

# Vincolo 7: Condizione di utilizzo dell'aula l per il settore s
for l in range(N):
    for s in range(S):
        for k in p_s[s]:
            model.addCons(u[l, s] >= y[k, l])


# model.writeProblem('problem.lp')


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


    # for i in range(P):
    #     for j in range(i+1, P):
    #         print(f"Differenza di aule tra professore {i} e professore {j}: {model.getVal(d[i, j])}")

    # for l in range(N):
    #     print(f"Numero di settori associati all'aula {l}: {model.getVal(h[l])}")

    save_optimal_schedule_to_excel(model, x, P, N, O, G, filename=f"{resultFolder}/orario_ottimale-3-obj3.xlsx")

    objective_value = model.getObjVal()
    print(f"Valore della funzione obiettivo: {objective_value}")

else:
    print("Non è stata trovata una soluzione ottimale.")
