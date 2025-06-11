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
previous_status = ""

parser = argparse.ArgumentParser("Interroge les log ClanLord")
parser.add_argument('--init',action='store',dest='initrc',default=None)
args = parser.parse_args()

top = tkinter.Tk()
top.title("On la boucle ?")
top.geometry('880x550-0+0')
top.config(bg=background)


def choix_balangar() : traiter_commande("personnage Balangar" )
def choix_ilonos() : traiter_commande("personnage Ilonos" ) 

def choix_analyse() :
    global analyse_choisie,str_analyse

    tmp_liste = {}
    for a in analyse_choisie :
        if a == "toutes" and analyse_choisie[a].get() == 1 :
            str_analyse.set("tout analyser")
            return 
        elif analyse_choisie[a].get() == 1 :
            tmp_liste[a] = 1
    if len(tmp_liste) == 0 :
        str_analyse.set("aucune analyse")
    else :
        str_analyse.set(",".join(tmp_liste))

def boucle_afficher() :
    """
    analyse les menus cochés/décochés
    lance la boucle
    affiche les résultats
    """
    global analyse_choisie,temporel_choisi,str_chercher,previous_status

    combien_analyse = 0
    for a in analyse_choisie :
        if analyse_choisie[a].get() == 1 :
            combien_analyse = combien_analyse + 1
            if a == "toutes" :
                traiter_commande("analyse toutes",True)
                break
            else :
                traiter_commande(f"analyse {a}",True)
        else :
            if 'boucle' in données :
                if a in données['boucle'] :
                    del données['boucle'][a]
                    previous_status = f"{previous_status}\n-> retrait de {a} de l'analyse"
    if combien_analyse == 0 :
        print("aucune analyse choisie")
        return
    if "filtre_date" in données :
        filtre = données["filtre_date"]
        del données["filtre_date"]
    for t in temporel_choisi :
        if temporel_choisi[t].get() == 1 :
            traiter_commande(f"filtre {t}",True)
            break
    traiter_commande("boucle",True)
    if str_chercher.get() != "" :
        traiter_commande("cherche:{}".format(str_chercher.get()),True)
    else :
        traiter_commande("afficher",True)

    afficher_status_tk(previous_status)
    previous_status = ""

def afficher_chercher(event=None):
    "affiche les rasultats, filtré par le champ chercher"

    global previous_status,str_chercher

    if str_chercher.get().strip() == "" :
        afficher_status_tk("aucun champ saisie",-1)
        return
    previous_status = ""
    traiter_commande("cherche:{}".format(str_chercher.get()),True)
    afficher_status_tk(previous_status)
    previous_status = ""
    
def choix_personnage(valeur):
    global debuguer,perso_menu

    if debuguer is not None :
        print(f" - personnage choisi {valeur}")
    traiter_commande(f"personnage {valeur}")
    perso_menu.configure(text=valeur)

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

str_personnage = tkinter.StringVar()
str_personnage.set("Choisir le personnage")
str_analyse = tkinter.StringVar()
str_analyse.set("aucune analyse choisie")
str_chercher = tkinter.StringVar()
str_chercher.set("")
num_cmd = tkinter.Label(top,
                        text="0",
                        font=("Courier",20),
                        background=background)
num_cmd.grid(row=nb_lignes,column=1)
information_lbl = tkinter.Label(top,
                                textvariable=str_personnage,
                                font=('Serif',25),
                                background=background)
information_lbl.grid(row=nb_lignes,column=2,columnspan=6)
repertoire_lbl = tkinter.Label(top,
                               text=repertoire,
                               font=("Courier",10),
                               background=background,
                               anchor="e")
repertoire_lbl.grid(row=nb_lignes,column=7,columnspan=2)



# ligne  : choix du personnage
nb_lignes = nb_lignes + 1
liste_perso = [ "Balangar" , "Forkalir" , "Ilonos" ]

nb_colone = 1
perso_menu = tkinter.Menubutton(top,
                                textvariable = str_personnage,
                                width='20',
                                borderwidth=2,
                                bg=background,
                                activebackground='darkorange' )
perso_menu.grid(row=nb_lignes,column=nb_colone,columnspan=2)
nb_colone = nb_colone + 2
perso_déroulant= tkinter.Menu(perso_menu)
#for perso in liste_perso :
#    tmpf = lambda : choix_personnage(perso)
#    perso_déroulant.add_command(label=f" - {perso} - ",command = tmpf )
perso_déroulant.add_command(label=" * Balangar * ",command=choix_balangar)
perso_déroulant.add_command(label=" * Ilonos * ",command=choix_ilonos)
perso_menu.configure(menu=perso_déroulant)


analyse_choisie={}
temporel_choisi = {}
analyse_menu = tkinter.Menubutton(top,
                                  textvariable = str_analyse,
                                  borderwidth=2,
                                  bg=background,
                                  activebackground='darkorange' )
analyse_menu.grid(row=nb_lignes,column=nb_colone,columnspan=3)
analyse_déroulant = tkinter.Menu(analyse_menu)
for analyse in [ "toutes", "butin", "dépeçage", "profession", "victoire" ] :
    analyse_choisie[analyse]=tkinter.IntVar()
    analyse_déroulant.add_checkbutton(label=analyse,
                                      variable=analyse_choisie[analyse],
                                      onvalue=1,
                                      offvalue=0,
                                      command=choix_analyse)
analyse_déroulant.add_separator()
for filtre_temporel in [ "jour", "semaine" ,"mois" ] :
    temporel_choisi[filtre_temporel] = tkinter.IntVar()
    analyse_déroulant.add_checkbutton(label=filtre_temporel,
                                      variable=temporel_choisi[filtre_temporel],
                                      onvalue=1,
                                      offvalue=0)
analyse_déroulant.add_separator()
analyse_déroulant.add_command(label="boucle et afficher",command=boucle_afficher)
analyse_menu.configure(menu=analyse_déroulant)
nb_colone = nb_colone + 3

chercher_lbl = tkinter.Label(top,text="chercher:",background=background,anchor="e")
chercher_lbl.grid(row=nb_lignes,column=nb_colone,columnspan=1)

chercher_input = tkinter.Entry(top,textvariable=str_chercher,width=30)
chercher_input.grid(row=nb_lignes,column=nb_colone+1,columnspan=2)
chercher_input.bind("<Return>",afficher_chercher)

# Ligne : statut dernière commande
nb_lignes = nb_lignes + 1
status_cmd = tkinter.Label(top,
                           text="aucune commande saisie",
                           background="white",
                           font=("Courier",12),
                           justify="left",
                           anchor="w")
status_cmd.grid(row=nb_lignes,column=2,columnspan=8,
                pady=5,padx=5,sticky="ew")

# Ligne  : aide dernière commande
nb_lignes = nb_lignes + 1
aide_lbl = tkinter.Label(top,
                         text="aucune commande saisie",
                         justify="left",
                         anchor="w")
aide_lbl.grid(row=nb_lignes,column=1,columnspan=10,
              pady=5,padx=10,sticky="ew")

# Ligne de fin : saisie
nb_lignes = nb_lignes + 1

my_cmd = tkinter.StringVar()  
my_cmd.set("")
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
            'filtre' : {'fonction' : valider.filtrer_date,
                         'arrité' : 1 ,
                         'afficher' : 25 ,
                         'aide' : "filtre les fichiers sur les dates : jour,semaine,mois"},

            'personnage' : {'fonction' : valider.valider_personnage ,
                            'arrité' : 1,
                            'afficher' : 10 ,
                            'aide' : "défini le personnage"},
            'analyse' : {'fonction' : valider.valider_analyse ,
                         'arrité' : 1,
                         'afficher' : 20 ,
                         'aide' : "ajoute une analyse (toutes,*,profession,dépeçage,butin,victoire)"},
            'boucle' : {'fonction' : boucle.boucle_lecture,
                        'arrité' : 0,
                        'afficher' : 30 ,
                        'aide' : "lance la boucle principale."},

            'affiche' : {'fonction' : boucle.boucle_affichage,
                          'arrité' : 0 ,
                          'afficher' : 40 ,
                          'aide' : "affiche les résultats"},
            'cherche' : {'fonction' : boucle.boucle_chercher,
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

    global debuguer,nb_commande,str_personnage
    if debuguer is not None :
        debuguer.pprint(données)
    num_cmd.configure(text=f"{nb_commande}")
    if 'personnage' in données :
        str_personnage.set(données['personnage'])
        information_lbl.configure(foreground="red")
    if 'nb fichier' in données :
        repertoire_lbl.configure(text=f"{données['répertoire']} ({données['nb fichier']}/{données['total']})")
    else :
        repertoire_lbl.configure(text=f"{données['répertoire']} (??)")


def traiter_commande(ligne,keep_status = False):
    """traite la commande"""

    global commande,nb_commande,previous_status

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
                    status = status + "\n" + cmd_c
                    if keep_status :
                        previous_status = f"{previous_status}\n{status}"
                    afficher_status_tk(c+":\n"+cmd_c,0)
                    if 'afficher' in commande[c] : purge_aide(commande[c]['afficher'])
                else:
                    status = status + f"échec de {c} ({ligne}) !!"
                    afficher_status_tk(c+"/"+données_tmp,-1)
            if commande[c]['arrité'] == 1 :
                cmd_t = ligne.strip().split()
                if ligne.find(":") > 0 :
                    cmd_t = list(map(lambda x:x.strip(" \n\t\r"),ligne.split(":")))
                status = status + f"\n\t {cmd_t[1]=}\n"
                if keep_status :
                    previous_status = f"{previous_status}\n{status}"
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
            # print(f" cmd[{nb_commande}] : {ligne}\n\t - {status}")
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
