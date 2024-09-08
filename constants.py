from gurobipy import Model, GRB

# Definizione dei parametri
P = 102  # Numero di professori
N = 53  # Numero di aule (uguale al numero di classi)
G = 5  # Numero di giorni
O = 8  # Numero di ore per giorno
S = 3  # Numero di settori
alpha = 1
beta = 1
gamma = 1

testFolder = 'galilei'
resultFolder = f'results/{testFolder}'


# Creazione del modello
model = Model("Assegnazione_Aule")

# Definizione delle variabili di decisione
x = model.addVars(P, N, O, G, vtype=GRB.BINARY, name="x")
y = model.addVars(P, N, vtype=GRB.CONTINUOUS, name="y")
z_max = model.addVar(vtype=GRB.CONTINUOUS, name="z_max")
u = model.addVars(N, S, vtype=GRB.BINARY, name="u")

vars = {
    'x': x,
    'y': y,
    'u': u,
    'z_max': z_max
}


