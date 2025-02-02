#!/usr/bin/env python3

import argparse
from lib.boucle import boucle,valider
from locale import LC_TIME, setlocale
import os
import pprint
import sys
import tkinter

background="#99b3ff"
debuguer = None
if "BOUCLE_VERBEUSE" in os.environ :
    debuguer = pprint.PrettyPrinter(indent=4)
dernière_commande = "en attente"
données = {'répertoire' : 'data'}
exit_on_error = True
nb_commande = 0
repertoire = "data"
terminal = 0

parser = argparse.ArgumentParser("Interroge les log ClanLord")
parser.add_argument('--init',action='store',dest='initrc',default=None)
args = parser.parse_args()

top = tkinter.Tk()
top.title("On la boucle ?")
top.geometry('880x550-0+0')
top.config(bg=background)


def unecommande(event=None):
    """lit une commande"""

    dernière_commande = my_cmd.get()
    my_cmd.set("")
    print(f"{nb_commande} > {dernière_commande}")
    if dernière_commande == "FIN." :
        top.quit()
    traiter_commande(dernière_commande)


def afficher_status(données) :
    """! affiche le status, les variables, etc ..."""
    quoi = ""

    quoi = quoi + f" - le répertoire (du dessus) {repertoire}\n"
    if 'personnage' in données :
        quoi = quoi + f" - le personnage {données['personnage']} ({données['nb fichier']}/{données['total']})\n"
    if 'boucle' in données :
        boucle = ",".join(données['boucle'])
        quoi = quoi + f" - on recherche {boucle}\n"

    return quoi,None


setlocale(LC_TIME, 'fr_FR.utf8')

# Ligne 1 : Nom du perso & repertoire
nb_lignes = 1

num_cmd = tkinter.Label(top,
                        text="0",
                        font=("Courier",20),
                        background=background)
num_cmd.grid(row=nb_lignes,column=1)
information_lbl = tkinter.Label(top,
                                text="emplacement à louer",
                                font=('Serif',25),
                                background=background)
information_lbl.grid(row=nb_lignes,column=2,columnspan=6)
repertoire_lbl = tkinter.Label(top,
                               text=repertoire,
                               font=("Courier",10),
                               background=background,
                               anchor="e")
repertoire_lbl.grid(row=nb_lignes,column=7,columnspan=2)


# Ligne 3 : statut dernière commande
nb_lignes = nb_lignes + 1
status_cmd = tkinter.Label(top,
                           text="aucune commande saisie",
                           background="white",
                           font=("Courier",12),
                           anchor="w")
status_cmd.grid(row=nb_lignes,column=2,columnspan=8,
                pady=5,padx=5,sticky="ew")

# Ligne 3 : statut dernière commande
nb_lignes = nb_lignes + 1
aide_lbl = tkinter.Label(top,
                         text="aucune commande saisie",
                         anchor="w")
aide_lbl.grid(row=nb_lignes,column=1,columnspan=10,
              pady=5,padx=10,sticky="ew")


# Ligne de fin : saisie
nb_lignes = nb_lignes + 1

my_cmd = tkinter.StringVar()  # For the messages to be sent.
my_cmd.set("Saisir une commande")
entry_field = tkinter.Entry(top, textvariable=my_cmd, width=100)
entry_field.bind("<Return>", unecommande)
# entry_field.bind("<Ctrl-U>", my_cmd.set(""))
entry_field.grid(row=nb_lignes,column=1,columnspan=10)


def on_closing(event=None):
    global top
    top.destroy()

top.protocol("WM_DELETE_WINDOW", on_closing)

commande = {'répertoire' : {'fonction' : valider.valider_repertoire,
                            'arrité' : 1 ,
                            'afficher' : 10 ,
                            'aide' : "défini le répertoire text logs (au dessus du presonnage)"},
            'personnage' : {'fonction' : valider.valider_personnage ,
                            'arrité' : 1,
                            'afficher' : 10 ,
                            'aide' : "défini le personnage"},
            'analyse' : {'fonction' : valider.valider_analyse ,
                         'arrité' : 1,
                         'afficher' : 20 ,
                         'aide' : "ajoute une analyse (toutes,*,profession,dépeçage,butin)"},
            'profession' : {'fonction' : valider.valider_profession,
                            'arrité' : 0,
                            'afficher' : 0 ,
                            'aide' : """ajout le calcul des professions dans les boucles
 * déprécié, utiliser "analyse profession"
"""},
            'boucle' : {'fonction' : boucle.boucle_lecture,
                        'arrité' : 0,
                        'afficher' : 30 ,
                        'aide' : "lance la boucle principale .. suspense"},

            'afficher' : {'fonction' : boucle.boucle_affichage,
                          'arrité' : 0 ,
                          'afficher' : 40 ,
                          'aide' : "affiche les résultats"},
            'chercher' : {'fonction' : boucle.boucle_chercher,
                          'arrité' : 1 ,
                          'afficher' : 50 ,
                          'aide' : 'cherche un terme,\n * utiliser =terme pour une recherche exacte' },
            'status' : {'fonction' : afficher_status , 'arrité' : 0}
            }

def purge_aide(niveau) :
    """ met à 0 la variable d'affichage si <= niveau """
    for c2 in commande :
        if 'afficher' in commande[c2] and commande[c2]['afficher'] <= niveau :
            commande[c2]['afficher'] = 0

def afficher_aide() :
    """ affiche l'aide dans la boite d'aide"""
    aide_txt = ""
    for c in commande :
        if 'afficher' in commande[c] and commande[c]['afficher'] > 0 :
            if 'aide' in commande[c] :
                aide_txt = aide_txt + c + ">" + commande[c]['aide'] + "\r\r"
    aide_lbl.configure(text=aide_txt)
    
def afficher_status_tk(status,code=1) :
    """affiche le status dans TK
    * code = -1,0,1 : échec,OK, en cours
    """
    status_cmd.configure(text=status,foreground="black")
    if code == -1 :
        status_cmd.configure(foreground="red")
        return
    if code == 0 :
        status_cmd.configure(foreground="green")
        return
 
def afficher_global() :
    """affiche tous les paramètres"""

    global debuguer,nb_commande
    if debuguer is not None :
        debuguer.pprint(données)
    num_cmd.configure(text=f"{nb_commande}")
    if 'personnage' in données :
        information_lbl.configure(text=données['personnage'],foreground="red")
    if 'nb fichier' in données :
        repertoire_lbl.configure(text=f"{données['répertoire']} ({données['nb fichier']}/{données['total']})")
    else :
        repertoire_lbl.configure(text=f"{données['répertoire']} (??)")

def traiter_commande(ligne):
    """traite la commande"""

    global commande,nb_commande
    
    if len(ligne) < 2 or ligne[0] == "#" or ligne[0] == ";" :
        return
    cmd_absente = True
    for c in commande :
        if ligne.lstrip().find(c) == 0 : ## doit débuter par c
            status = f"trouvé {c}"
            cmd_absente = False
            afficher_status_tk(status,1)
            if 'aide' in commande[c] :
                status = f"trouvé {c}/{commande[c]['arrité']}, {commande[c]['aide']}"
                afficher_status_tk(status,0)                
            if commande[c]['arrité'] == 0 :
                cmd_c,données_tmp = commande[c]['fonction'](données)
                if cmd_c is not None :
                    status = status + "\n\n" + cmd_c
                    afficher_status_tk(c+":\n"+cmd_c,0)
                    if 'afficher' in commande[c] : purge_aide(commande[c]['afficher'])
                else:
                    status = status + f"échec de {c} ({ligne}) !!"
                    afficher_status_tk(c+"/"+données_tmp,-1)
            if commande[c]['arrité'] == 1 :
                cmd_t = ligne.strip().split()
                if ligne.find(":") > 0 :
                    cmd_t = list(map(lambda x:x.strip(" \n\t\r"),ligne.split(":")))
                status = status + f"\n\t {cmd_t[1]=}\n\n "
                cmd_c,données_tmp = commande[c]['fonction'](données,cmd_t[1])
                if cmd_c is not None :
                    status = status + cmd_c
                    afficher_status_tk(c+":\n"+cmd_c,0)
                    if 'afficher' in commande[c] : purge_aide(commande[c]['afficher'])
                else :
                    status = status + f"\t[41méchec de {c} ({ligne}) !![0m"
                    afficher_status_tk(c+"/"+données_tmp,-1)
                    print(données_tmp)
            nb_commande = nb_commande + 1
            print(f" cmd[{nb_commande}] : {ligne}\n\t - {status}")
            break
    if cmd_absente :
        afficher_status_tk(f"commande inconnue {ligne}",-1)
        
    afficher_aide()
    afficher_global()

if args.initrc is not None :
    with open(args.initrc,"r") as init_fp :
        for ligne in init_fp :
            traiter_commande(ligne)
            
afficher_aide()
tkinter.mainloop()  # Starts GUI execution.
print("on sort de la boucle")
