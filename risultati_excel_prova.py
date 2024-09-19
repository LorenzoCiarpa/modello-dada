import pandas as pd

from data.galilei.dizionario_professori import prof_to_idx
from read_var import read_init_vars_json

# Mappa giorni e ore a un formato leggibile per le righe
giorni_settimana = ['LUN', 'MAR', 'MER', 'GIO', 'VEN']

day_map = {
    0: 'lunedi',
    1: 'martedi',
    2: 'mercoledi',
    3: 'giovedi',
    4: 'venerdi'
}


idx_to_prof = {
    value : key for key, value in prof_to_idx.items()

}


# Supponiamo di avere le classi già definite manualmente
'''
classi = [
    '1A', '1B', '1C', '1D', '1E', '1F', '1G', '1H', '1ILS', '1M', '1N',
    '2A', '2B', '2C', '2D', '2E', '2F', '2G', '2H', '2ILS', '2LLS', '2M', '2N',
    '3A', '3B', '3C', '3D', '3E', '3F', '3G', '3H', '3ILS', '3M',
    '4A', '4B', '4C', '4D', '4E', '4F', '4G', '4H', '4ILS', '4LLS',
    '5A', '5B', '5C', '5D', '5E', '5F', '5G', '5H', '5ILS', '5LLS'
]
'''

aule = [ f"Aula{i}" for i in range(53)]


# Definiamo i giorni e le ore settimanali (lunedì-ven 1-8 ore)


giorni_ore = ['LUN1', 'LUN2', 'LUN3', 'LUN4', 'LUN5', 'LUN6', 'LUN7', 'LUN8',
              'MAR1', 'MAR2', 'MAR3', 'MAR4', 'MAR5', 'MAR6', 'MAR7', 'MAR8',
              'MER1', 'MER2', 'MER3', 'MER4', 'MER5', 'MER6', 'MER7', 'MER8',
              'GIO1', 'GIO2', 'GIO3', 'GIO4', 'GIO5', 'GIO6', 'GIO7', 'GIO8',
              'VEN1', 'VEN2', 'VEN3', 'VEN4', 'VEN5', 'VEN6', 'VEN7', 'VEN8']
'''
giorni_ore = ['LUN0', 'LUN1', 'LUN2', 'LUN3', 'LUN4', 'LUN5', 'LUN6', 'LUN7',
              'MAR0', 'MAR1', 'MAR2', 'MAR3', 'MAR4', 'MAR5', 'MAR6', 'MAR7',
              'MER0', 'MER1', 'MER2', 'MER3', 'MER4', 'MER5', 'MER6', 'MER7',
              'GIO0', 'GIO1', 'GIO2', 'GIO3', 'GIO4', 'GIO5', 'GIO6', 'GIO7',
              'VEN0', 'VEN1', 'VEN2', 'VEN3', 'VEN4', 'VEN5', 'VEN6', 'VEN7']

'''


variables = read_init_vars_json('./results/galilei/3/partial_solution_23.json')
x_values = variables['x']
x_values = {eval(k): v for k, v in x_values.items()}


# Creiamo un DataFrame vuoto con le righe giorni-ore e colonne come classi
df = pd.DataFrame(index=giorni_ore, columns=aule)
df_orario = pd.read_csv("./data/galilei/orario-bk.csv")



def trova_classe(giorno, ora, professore):
    # Filtra il DataFrame in base ai criteri
    filtro = (df_orario['Giorno'] == day_map[giorno]) & (df_orario['Ora'] == (ora + 1)) & (df_orario['Professore'] == idx_to_prof[professore + 1])
    
    # Recupera le classi che soddisfano il filtro
    classi = df_orario.loc[filtro, 'Classe']
    
    # Verifica se sono state trovate delle classi
    if not classi.empty:
        return classi.values[0]  # Restituisce la prima classe trovata
    else:
        return "None"


for (professore, aula, ora, giorno), value in x_values.items():

    if value == 1.0:  # Consideriamo solo i valori dove il professore insegna
        giorno_ora_label = f"{giorni_settimana[giorno]}{ora + 1}"  # Es: LUN1, MAR3
        # Assegniamo il professore e l'aula alla cella corrispondente
        # Supponiamo che la classe sia in funzione dell'aula (puoi adattarlo se serve)
        classe = aule[aula]  # Questo associa l'aula alla classe
        df.loc[giorno_ora_label, classe] = f"Prof {professore} (Classe {trova_classe(giorno, ora, professore)})"

# Esportiamo il DataFrame in Excel
df.to_excel('./orario_scolastico_new.xlsx', index=True)

print("Orario esportato correttamente in orario_scolastico_new.xlsx")
