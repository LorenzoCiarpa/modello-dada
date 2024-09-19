from gurobipy import Model, GRB

# Definizione dei parametri
P = 102  # Numero di professori
N = 53  # Numero di aule (uguale al numero di classi)
C = 53  # Numero di classi (uguale al numero di classi)
G = 5  # Numero di giorni
O = 8  # Numero di ore per giorno
S = 7  # Numero di settori
F = 3  # Numero di piani

alpha = 1 / 100
beta = 1 / 2
gamma = 1 / 265

testFolder = 'galilei'
resultFolder = f'results/{testFolder}'
runNumber = 6
orarioFile = 'orario-bk.csv'
settoreFile = 'new_Professore_Settore.csv'


# Creazione del modello
model = Model("Assegnazione_Aule")

# Definizione delle variabili di decisione
x = model.addVars(P, N, O, G, C, vtype=GRB.BINARY, name="x")
y = model.addVars(P, N, vtype=GRB.CONTINUOUS, name="y")
z_max = model.addVar(vtype=GRB.CONTINUOUS, name="z_max")
u = model.addVars(N, S, vtype=GRB.BINARY, name="u")
w = model.addVars(F, C, G, vtype=GRB.CONTINUOUS, name="w")

vars = {
    'x': x,
    'y': y,
    'u': u,
    'w': w,
    'z_max': z_max
}


