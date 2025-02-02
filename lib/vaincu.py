#!/usr/bin/python3
# -*- coding: utf-8 -*-

import csv
from functools import cmp_to_key
import re


class chasse:
    """! analyse des victoires"""

    def __init__(self,qui,/,debug=0, fam=False) :
        """!initialisation des tableaux
        @param fam False un familier ?
        construction chaine regexp pour les vanq/kill/...
        avec soit
         * **you**
         * le familier
        """
        self.vaincu  = dict()
        self.debug   = debug
        self.moi     = qui
        qui_chercher = "You"
        self.fam_lvl = -1
        self.ordre   = ["vanquished",
                        "helped vanquish",
                        "killed",
                        "helped kill",
                        "dispatched",
                        "helped dispatch",
                        "slaughtered",
                        "fallen to"
                        ]
        tmp_all         = "|".join(self.ordre[0:7])
        if fam :
            qui_chercher = qui
            self.fam_lvl = 0
            self.ventilation = dict()
            self.ordre   = ["vanquished",
                            "killed",
                            "dispatched",
                            "slaughtered"
                            ]

        self.kill_re    = re.compile(f"{qui_chercher} (?P<comment>{tmp_all}) a[n]* (?P<quoi>[^.]+)(.|!)")
        self.fallen_re  = re.compile(qui + " has fallen to a[n]* (?P<quoi>[^.]+).")
        self.chemin_csv = f"results/victoires-{qui}.csv"

    def empiler_vaincu(self,quoi,comment) :
        """! test et empile les caractéristiques des victoires"""
        if quoi not in self.vaincu :
            self.vaincu[quoi] = dict()
        if comment in self.vaincu[quoi] :
            self.vaincu[quoi][comment] = self.vaincu[quoi][comment] + 1
        else:
            self.vaincu[quoi][comment] = 1

    def empiler_niveau_fam(self,quoi,comment) :
        """! test et empile les niveaux lors des victoires
        @param quoi la victime
        @param comment vanq/kill/disp/slaugther
        (la classe connait le niveau)

        réutilise self.vaincu[quoi]
         * seld.empilaer_vaincu() appelé avant
         * self.vaincu[quoi][comment + "_max"] (toujours)
         * self.vaincu[quoi][comment + "_min"] (une fois)
        """
        tmp_max = comment + "_max"
        self.vaincu[quoi][tmp_max] = self.fam_lvl
        tmp_min = comment + "_min"
        if tmp_min not in self.vaincu[quoi] :
            self.vaincu[quoi][tmp_min] = self.fam_lvl

    def palier_familier(self,palier) :
        """! nouveau palier pour le familier
        (improprement appelé niveau)
        """
        self.fam_lvl = palier

    def début_session(self,quand_unix,fichier) :
        """! début de session
        @param quand_unix timestamp unix
        @param fichier nom du fichier

        rend la valeur (en timestamp) au delà de laquelle on peut faire l'analyse de ligne.
        -1 par défaut
        """
        return -1

    def fin_session(self) :
        """! fin de la session (le fichier)
        déclenche des actions de maj de fichier
        """
        return None

    def fin_analyse(self) :
        """! plus de fichier à analyser
        déclenche des actions de maj de fichier
        """
        return None

    def analyser_ligne(self,ligne) :
        """analyse une ligne pour
        * voir ce que j'ai tué
        * comment (je l'ai tué)
        """
        victime = self.kill_re.match(ligne)
        if victime is not None :
            self.empiler_vaincu(victime.group('quoi'),victime.group('comment'))
            if self.fam_lvl > -1 :
                self.empiler_niveau_fam(victime.group('quoi'),victime.group('comment'))
            return 1
        tombe = self.fallen_re.match(ligne)
        if tombe is not None :
            self.empiler_vaincu(tombe.group('quoi'),'fallen to')
            return 1
        return 0

    def trier_victoire(self,a,b) :
        """ trie les victoires par ordre d'importance"""

        for o in self.ordre :
            tmp_a = tmp_b = 0
            if o in self.vaincu[a] : tmp_a = self.vaincu[a][o]
            if o in self.vaincu[b] : tmp_b = self.vaincu[b][o]
            if tmp_a == tmp_b : continue
            return tmp_b - tmp_a
        if a < b : return -1
        else : return 1

    def afficher(self) :
        """! affiche le resultat
        fonction chapeau pour appeler
        * afficher_perso()
        * afficher_pet()
        """
        if self.fam_lvl == -1 :
            self.afficher_perso()
        else :
            self.afficher_familier()

    def afficher_perso(self) :
        """! affiche les victoires (parfois les défaites) du personnage """
        largeur = 30
        idx_ligne = 1
        print(f"\n\t\t \x1b[31mVictoires pour {self.moi}\x1b[0m\n")
        print(" " * largeur + "  " + "_" * 39)
        print(" " * largeur + " :  v , hv |  k , hk |  d , hd |  s , ft .")

        for v in sorted(self.vaincu, key=cmp_to_key(lambda a, b: self.trier_victoire(a,b))) :
            ligne = f"{v:<{largeur}} :"  # pour les chaines, la précision troncate.
            for o in self.ordre :
                k = " "
                sep = ","
                if o.find("help") == 0 : sep = "|"
                if o in self.vaincu[v] :
                    k = self.vaincu[v][o]
                    if k > 1000 : k = "∞"
                ligne = ligne + f" {k:3}{sep}"
            idx_ligne = idx_ligne + 1
            format_ligne = "{}"
            if idx_ligne % 5 == 0 :
                format_ligne = "\x1b[4m{}\x1b[0m"
            print(format_ligne.format(ligne[:-1] + "."))
        if idx_ligne % 5 != 0 :
            print(" " * largeur + "  " + "_" * 39)

    def chercher_afficher(self,quoi) :
        """! affiche les victoires (parfois les défaites) du personnage 
        @param quoi filtre sur quoi
        """
        largeur = 30
        idx_ligne = 1
        entete_tty = f"\n\t \x1b[31mVictoires pour {self.moi}\x1b[0m ({quoi})\n" +\
                 " " * largeur + "  " + "_" * 39 + "\n" +\
                 " " * largeur + " :  v , hv |  k , hk |  d , hd |  s , ft ."
        exacte = False
        if quoi[0] == "=" :
            exacte = True
            quoi = quoi[1:]
        for v in sorted(self.vaincu, key=cmp_to_key(lambda a, b: self.trier_victoire(a,b))) :
            if exacte and v.lower() != quoi :
                continue
            if v.lower().find(quoi) == - 1 :
                continue
            if entete_tty is not None :
                print(entete_tty)
                entete_tty = None
            ligne = f"{v:<{largeur}} :"  # pour les chaines, la précision troncate.
            for o in self.ordre :
                k = " "
                sep = ","
                if o.find("help") == 0 : sep = "|"
                if o in self.vaincu[v] :
                    k = self.vaincu[v][o]
                    if k > 1000 : k = "∞"
                ligne = ligne + f" {k:3}{sep}"
            idx_ligne = idx_ligne + 1
            format_ligne = "{}"
            if idx_ligne % 5 == 0 :
                format_ligne = "\x1b[4m{}\x1b[0m"
            print(format_ligne.format(ligne[:-1] + "."))
        if idx_ligne % 5 != 0 :
            print(" " * largeur + "  " + "_" * 39)
        if entete_tty is None : print("\n")        

    def afficher_familier(self) :
        """! affiche les victoires (à quel prix) du familier"""
        largeur = 20
        lg_col = 12
        idx_ligne = 1
        print(f"\n\t\t \x1b[31mVictoires pour {self.moi}\x1b[0m\n")
        entete = ""
        for o in self.ordre :
            entete = entete + f"{o:^{lg_col}}|"
        print(" " * largeur + " " + (1 + len(entete)) * "-")
        print(" " * largeur + " :" + entete[:-1] + ".")
        for v in sorted(self.vaincu, key=cmp_to_key(lambda a, b: self.trier_victoire(a,b))) :
            ligne = f"{v:<{largeur}} :"
            for o in self.ordre :
                k = " "
                minmax = "     "
                if o in self.vaincu[v] :
                    k = self.vaincu[v][o]
                    if k > 1000 : k = "∞"
                    if o + "_max" in self.vaincu[v] :
                        i = self.vaincu[v][o + "_min"]
                        a = self.vaincu[v][o + "_max"]
                        if i < a : minmax = f"{i:2}-{a:<2}"
                        else: minmax = f"{i:^5}"
                    ligne = ligne + f" {k:3}, {minmax} |"
                else :
                    ligne = ligne + lg_col * " " + "|"
            idx_ligne = idx_ligne + 1
            format_ligne = "{}"
            if idx_ligne % 5 == 0 :
                format_ligne = "\x1b[4m{}\x1b[0m"
            print(format_ligne.format(ligne[:-1] + "."))

    def print_csv(self) :
        with open(self.chemin_csv,'w',newline='') as csv_file :
            tmp_ordre = tmp_entete = dict()
            tmp_entete['nom'] = 'nom'
            for o in self.ordre :
                tmp_entete[o] = o
            ecrire = csv.DictWriter(csv_file,fieldnames=tmp_entete)
            ecrire.writeheader()
            for a in self.vaincu :
                tmp_ordre['nom'] = a
                for o in self.ordre :
                    if o in self.vaincu[a] :
                        tmp_ordre[o] = self.vaincu[a][o]
                    else:
                        tmp_ordre[o] = 0
                ecrire.writerow(tmp_ordre)
        return None

    def generer_fichier(self) :
        """!génere les fichers annexes ci besoin
        * csv
        """

        self.print_csv()
        return None
