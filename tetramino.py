"""
Auteur: Rocca Manuel
Matricule: 000596086
Date: 17/12/2023
Ce code permet de jouer au tétramino simplifié dépendant d'un fichier "carte".
"""

#Importation des modules
import sys
from getkey import getkey
import os

#Définition des constantes globales
nom_fichier = sys.argv[1]

#Définition des fonctions
def create_grid(w, h):
    """
    Crée la matrice de jeu avec la sous grille dans laquelle il faut placer les tétraminos.
    Cette fonction prend les dimensions souhaitées en paramètre, et return la matrice de jeu.
    """
    matrix = [[" "*2]*(3*w+2) for _ in range (3*h+2)]
    for j in range(w):
        matrix[h][w+j+1] = "--"
        matrix[2*h+1][w+j+1] = "--"
    for i in range(h):
        matrix[h+1+i][w] = " |"
        matrix[h+1+i][2*w+1] = "| "
    return matrix
    

def import_card(file_path):
    """
    Importe la dimension de la grille et les tétraminos à partir du fichier donné.
    Cette fonction prend le nom du fichier en paramètre et return un tuple comprenant,\
    un tuple avec les dimensions de la matrice de jeu et une liste contenant\
    les tétraminos(chaque élément est un tétramino, un tétramino est une liste avec ses positions initiales, sa couleur et son décalage).
    """
    with open(file_path, "r", encoding = "utf-8") as carte:
        dimensions = carte.readline().strip().split(',')
        tup_dimensions = (int(dimensions[0]), int(dimensions[1]))#initialisation des dimensions
        liste, i = [], 0
        for ligne in carte:#initialisation des tétraminos
            liste.append([[],0,(0,0)])
            coord_tetra = ligne.strip().split(";")
            for j in range(len(coord_tetra)-4):
                liste[i][0].append((int(coord_tetra[j][1]), int(coord_tetra[j][4])))
            data = ligne.strip().split(";;")
            liste[i][1] = data[1]
            i += 1
    return (tup_dimensions, liste)


def setup_tetraminos(tetraminos, grid):
    """
    Place les tétraminos dans la matrice de jeu.
    Cette fonction prend les tétraminos en paramètre et la matrice de jeu\
    et place chacun des tétraminos dans la grille avec un décalage initial\
    qui permet de placer les tétraminos dans des zones différentes selon leur numéro.
    """
    largeur = (len(grid[0]) - 2) // 3 
    hauteur = (len(grid) - 2) // 3 
    numero = '1 '
    decalage_y, decalage_x = 0, 0
    for liste_elems in tetraminos:
        for positions in liste_elems[0]:
            x, y = positions
            grid[y+decalage_y][x+decalage_x] = '\x1b['+ liste_elems[1] + 'm' + numero + '\x1b[0m'
        liste_elems[2] = (decalage_x, decalage_y)#initialisation du décalage initial pour chaque tétramino
        numero = str(int(numero)+1) + ' '
        index = int(numero)
        if index <= 4:
            index = index - 1
        decalage_x = index % 3 * (largeur + 1)
        decalage_y = (index // 3) * (hauteur + 1)
    return grid, tetraminos

def place_tetraminos(tetraminos, grid):
    """
    Place les tétraminos dans la matrice de jeu selon leur nouvelle position\
    (le tétramino affiche "XX" si il est sur une position invalide).
    """
    num_tetra = 1
    w = (len(grid[0]) - 2) // 3 
    h = (len(grid) - 2) // 3 
    grid = create_grid(w, h)#vide la grille
    for tetramino in tetraminos:
        num = str(num_tetra) + " "
        for position in tetramino[0]:
            x, y = position
            x += tetramino[2][0]
            y += tetramino[2][1]
            if grid[y][x] in ["--", " |", "| "] or "[0m" in grid[y][x]:#si la position est valide
                grid[y][x] =  '\x1b['+ str(tetramino[1]) + 'm' + "XX" + '\x1b[0m'
            else:
                grid[y][x] =  '\x1b['+ str(tetramino[1]) + 'm' + num + '\x1b[0m'
        num_tetra += 1
    return grid


def rotate_tetramino(tetramino, clockwise = True):
    """
    Modifie les positions initiales du tétramino pris en paramètre\
    pour permettre sa rotation horaire ou anti-horaire en fonction du paramètre "clockwise".
    """
    for position in range(len(tetramino[0])):
        if clockwise:
            x_tplusun = - tetramino[0][position][1]
            y_tplusun = tetramino[0][position][0]
        elif not clockwise:
            x_tplusun = tetramino[0][position][1]
            y_tplusun = - tetramino[0][position][0]
        tetramino[0][position] = (x_tplusun, y_tplusun)
    
    return tetramino


def check_move(tetramino, grid):
    """
    Renvoie True si la position du tétramino est valide et False sinon.
    """
    res = True
    for position in tetramino[0]:
        x = position[0] + tetramino[2][0]
        y = position[1] + tetramino[2][1]
        if "XX" in grid[y][x]:
            res = False
    return res


def check_win(grid):
    """
    Renvoie True si la grille centrale est complétée et False sinon\
    en vérifiant s'il n'y a pas de case vide dans cette grille.
    """
    res = True
    largeur = (len(grid[0]) - 2) // 3 
    hauteur = (len(grid) - 2) // 3 
    for i in range(largeur):
        for j in range(hauteur):
            if grid[hauteur+1+j][largeur+1+i] == "  ":
                res = False
    return res


def verif_tetra(element):
    """
    Renvoie True si l'élément est un tétramino et False sinon.
    """
    res = True
    if element in ["  ", "--", "| ", " |"]:
        res = False
    return res


def verif_type_tetra(tetramino):
    """
    Renvoie True si le tétramino a une position valide et False sinon.
    """
    res = True
    verif = tetramino[10:12]#correspond au segment du string du tétramino qui affiche le numéro ou "XX"
    if verif == "XX":
        res = False
    return res


def print_grid(grid, no_number = False):
    """
    Print le texte d'accueuil et de consignes et la matrice de jeu.
    Les tétraminos sont imprimés avec ou sans leur numéro en fonction du paramètre no_number.
    """
    print("Bienvenue dans le jeu du Tétramino\nVotre but est de placer tous les \
tétraminos dans la grille centrale.\nSélectionnez le tétramino que vous \
souhaitez déplacer (1 à 8).\nPour le déplacement, appuyez sur 'i' pour déplacer la \
pièce vers le haut, 'k' pour le bas, 'j' pour la gauche et 'l' pour la droite.\nPour \
les rotations, appuyez sur 'o' pour faire tourner la pièce dans le sens des aiguilles \
d’une montre et sur 'u' pour le sens inverse.\nFinalement, pour valider la position, appuyez sur 'v'.")
    largeur_tot = len(grid[0])
    for _ in range(largeur_tot+1):
        print("--", end = "")
    print()
    for i in grid:
        print("|", end = "")
        for j in range(len(i)):
            if no_number:
                if verif_tetra(i[j]):
                    if not verif_type_tetra(i[j]):
                        print(f"{i[j][:10]}{'XX'}{i[j][12:]}", end = "")   
                    else:
                        print(f"{i[j][:10]}{'  '}{i[j][12:]}", end = "")
                else:
                    print(i[j], end = "")
            else:
                print(i[j], end = "")
        print("|", end = "")
        print()
    for _ in range(largeur_tot+1):
        print("--", end = "")
    print()

def clear_console():
    """
    Cette fonction est appelée pour clear la console.
    Prend en compte le nom de l'os
    """
    if os.name == "posix":
        os.system("clear")
    else:
        os.system("cls")
        
        
        
def main():
    """
    Fonction principale qui initialise le jeu et fait tourner le jeu
    """
    taille, tetras = import_card(nom_fichier)#initialisation
    w, h = taille
    mat = create_grid(w, h)
    mat, tetras = setup_tetraminos(tetras, mat)
    print_grid(mat)
    mouv_vertical, mouv_horizontal, key = 0, 0, "a"#initialisation de variables pour éviter les UnboundLocalError
    while not check_win(mat):#jeu
        while not isinstance(key, int):
            try:
                key = int(getkey().decode("utf-8"))
            except ValueError:
                pass
        tetra = tetras[key-1]
        while not key == "v":#tant que la position n'est pas confirmée
            clear_console()
            print_grid(mat, True)
            key = getkey().decode("utf-8")
            
            if key == "v" and not check_move(tetra, mat):#vérification de la validité de la position du tétramino
                key = 0                                  #si position non-valide, impossible de quitter la boucle
            
            elif key in ["i", "k"]:
                max_y = max(position[1] for position in tetra[0])
                if key == "i" and tetra[2][1] > 0:
                    mouv_vertical = tetra[2][1] - 1
                elif key == "k" and tetra[2][1] + max_y < len(mat) - 1:
                    mouv_vertical = tetra[2][1] + 1
                tetra[2] = (tetra[2][0], mouv_vertical)
                mat = place_tetraminos(tetras, mat)
            
            elif key in ["j", "l"]:
                max_x = max(position[0] for position in tetra[0])
                if key == "j" and tetra[2][0] > 0:
                    mouv_horizontal = tetra[2][0] - 1
                elif key == "l" and tetra[2][0] + max_x < len(mat[0]) - 1:
                    mouv_horizontal = tetra[2][0] + 1
                tetra[2] = (mouv_horizontal, tetra[2][1])
                mat = place_tetraminos(tetras, mat)
            
            elif key in ["o", "u"]:
                sens = True if key == "o" else False
                rotate_tetramino(tetra, sens)
                mat = place_tetraminos(tetras, mat)
        clear_console()
        print_grid(mat)
        
    clear_console()
    print_grid(mat, True)           
    print("Vous avez gagné!")


if __name__ == "__main__":
    main()