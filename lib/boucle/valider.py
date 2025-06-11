#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
from lib import profession,skinndent,vaincu


def valider_repertoire(données,r) :
    """!change le répertoire (des text logs)  par défaut
    @param r le nouveau répertoire
    """
    if os.path.exists(r) :
        données['répertoire'] = r
        return f" on change les text logs pour {r}",None
    return None,f" - {r} n'est pas accessible"


def valider_personnage(données,p) :
    """! valide si il existe repertoire/p
    @param p le nom du personnage
    """

    repertoire = données['répertoire']
    data = f"{repertoire}/{p}"
    compte = 0
    total = 0
    if os.path.exists(data) :
        for fichier in os.listdir(data) :
            if fichier.startswith("CL") :
                compte = compte + 1
                total = total + os.stat(f"{data}/{fichier}").st_size
        données['personnage'] = p
        données['nb fichier'] = compte
        données['total'] = total
        return f"le chemin {repertoire}/{p} existe (avec {compte} fichiers d'un total de {total:,} octets)",None
    return None,f"le chemin {data} n'est pas un répertoire (s'il existe)"


def valider_profession(données) :
    """! ajoute le test de la profession dans les boucles
    """

    if "boucle" not in données :
        données["boucle"] = dict()
    données["boucle"]["profession"] = profession.professions(données['personnage'])
    return "calcul des professions ajoutées à la boucle",données


def valider_analyse(données,a) :
    """! valide une des analyses passée en argument
    @param données dictionnaires des données
    @param a une analyse
    * buttin
    * dépeçage
    * profession
    * victoire
    """

    if "boucle" not in données :
        données["boucle"] = dict()

    if a == "toutes" or a == "*"  :
        données["boucle"]["butin"] = skinndent.butin()
        données["boucle"]["dépeçage"] = skinndent.peauetdent(données['personnage'])
        données["boucle"]["profession"] = profession.professions(données['personnage'])
        données["boucle"]["victoire"] = vaincu.chasse(données['personnage'])
        quoi = ", ".join(données["boucle"])
        return f"calcul des {quoi} ajoutées à la boucle",données

    if a == "butin" :
        données["boucle"][a] = skinndent.butin()
        return "calcul des butins ajoutées à la boucle",données

    if a == "dépeçage" :
        données["boucle"][a] = skinndent.peauetdent(données['personnage'])
        return "calcul des dépeçages ajoutées à la boucle",données

    if a == "profession" :
        données["boucle"][a] = profession.professions(données['personnage'])
        return "calcul des professions ajoutées à la boucle",données

    if a == "victoire" :
        données["boucle"][a] = vaincu.chasse(données['personnage'])
        return "calcul des victoires ajoutées à la boucle",données

    return None,f"l'analyse {a} n'est pas disponible"

def filtrer_date(données,date) :
    """ filtrer sur les dates (relatives) des fichiers
    * j(our)
    * s(emaine)
    * m(mois)
    """
    
    t = -1
    if date[0] == "j" :
        données["filtre_date"] = 86400
        return "ne conserve que les fichiers de 24h",données
    
    if date[0] == "s" :
        données["filtre_date"] = 86400 * 7
        return "ne conserve que les fichiers d'une semaine",données

    if date[0] == "m" :
        données["filtre_date"] = 86400 * 30
        return "ne conserve que les fichiers du mois",données

    return None,f"la critère de date ({date}) est inconue (j(our),s(emaine),m(ois))"
