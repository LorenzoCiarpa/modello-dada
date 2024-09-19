classi = {
    '1A': 1, '1B': 2, '1C': 3, '1D': 4, '1E': 5, '1F': 6, '1G': 7, '1H': 8, '1ILS': 9, '1M': 10, '1N': 11,
    '2A': 12, '2B': 13, '2C': 14, '2D': 15, '2E': 16, '2F': 17, '2G': 18, '2H': 19, '2ILS': 20, '2LLS': 21, '2M': 22, '2N': 23,
    '3A': 24, '3B': 25, '3C': 26, '3D': 27, '3E': 28, '3F': 29, '3G': 30, '3H': 31, '3ILS': 32, '3M': 33,
    '4A': 34, '4B': 35, '4C': 36, '4D': 37, '4E': 38, '4F': 39, '4G': 40, '4H': 41, '4ILS': 42, '4LLS': 43,
    '5A': 44, '5B': 45, '5C': 46, '5D': 47, '5E': 48, '5F': 49, '5G': 50, '5H': 51, '5ILS': 52, '5LLS': 53
}


# Lista dei numeri delle aule da 1 a 53
aule = list(range(1, 54))

# Divisione delle aule tra i piani
l1 = aule[:17]   # Prime 17 aule per il piano 1
l2 = aule[17:35] # Successive 18 aule per il piano 2
l3 = aule[35:]   # Ultime 18 aule per il piano 3

'''
# Risultato
print("Piano 1:", l1)
print("Piano 2:", l2)
print("Piano 3:", l3)

'''
