#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
from time import mktime,strptime,time


def boucle_lecture(données) :
    """!lance la boucle de lecture
    @param données le dictionaire avec les données
    """

    base_data = données['répertoire'] + "/" + données['personnage']
    chercher = données['boucle']
    fichier_courant = 0
    six_pct = données['nb fichier'] // 6
    fichiers_cherchés = 0
    filtre_date = -1
    dés = ""
    if "filtre_date" in données :
        filtre_date = int(time()) - données['filtre_date']
    if données['nb fichier'] < 100 :
        six_pct = 100
    for fichier in sorted(os.listdir(base_data)):
        if fichier.startswith('CL'):
            fichier_courant = fichier_courant + 1
            if fichier_courant % six_pct == 0 :
                dés = chr(9855 + (fichier_courant // six_pct)) + " "
                print(dés,end='',flush=True)
            quand = mktime(strptime(fichier[7:26],"%Y-%m-%d %H.%M.%S"))
            if quand < filtre_date : continue
            c2 = dict()
            fichiers_cherchés = fichiers_cherchés + 1
            for c in chercher :
                if quand > chercher[c].début_session(quand,fichier) :
                    c2[c] = chercher[c]
            with open(f"{base_data}/{fichier}","r") as fp :
                for ligne in fp :
                    for c in c2 :
                        c2[c].analyser_ligne(ligne)
            for c in chercher :
                chercher[c].fin_session()
    if dés != "" : print(" !")
    for c in chercher :
        chercher[c].fin_analyse()

    return f"analysé {fichiers_cherchés}/{fichier_courant} fichiers dans {base_data}",None


def boucle_affichage(données) :
    """!lance la boucle d'affichage
    @param données le dictionaire avec les données
    """

    chercher = données['boucle']
    quoi = ", ".join(chercher)
    for c in chercher :
        chercher[c].afficher()

    return f"affichage de l'analyse pour {quoi}",None


def boucle_chercher(données,quoi) :
    """!recherche la chaine c dans les résultats
    @param c le terme à chercher (avec = pour un recherche exacte)
    """
    
    chercher = données['boucle']
    liste = ', '.join(chercher)
    for c in chercher :
        if hasattr(chercher[c],'chercher_afficher') :
            chercher[c].chercher_afficher(quoi.lower())
    
    return f"recherche de {quoi} dans {liste}",None
