#!/usr/bin/python3
# -*- coding: utf-8 -*-

import csv
from functools import cmp_to_key
from os import unlink
from time import time
import re


class peauetdent:
    """analyse de nombre et des bénéfices de l'extraction des peaux et mandibules"""

    def __init__(self,qui,/,debug=0,arguments=None) :
        """initialisation des tableaux
        construction chaine regexp
        niveaux Skea et Dentir
        """
        self.animaux = dict()
        self.debug   = debug
        self.moi     = qui
        self.skea    = 0
        self.dentir  = 0
        self.récent = -1
        if arguments is not None and hasattr(arguments,'dépeçage') :
            if arguments.dépeçage > 0 :
                self.récent = int(time()) - 86400 * arguments.dépeçage
        self.i_skinned = False
        self.chemin_csv = f"results/dépeçage-{qui}.csv"
        self.ordre   = ['combien', 'total', 'mes parts', 'Don entrant', 'Don sortant']
        self.ordra   = ['Don entrant', 'combien', 'total', 'mes parts', 'Don sortant']
        self.skin_re = re.compile(r"^\* ((?P<qui>.*) recovers the|You recover the)"
                                  " (?P<quoi>[^,]+)"
                                  " (?P<type>fur|mandibles),"
                                  " worth (?P<vaut>[0-9]+)c."
                                  "( Your share is (?P<part>[0-9]+)c.)?")
        self.dépecer_f = open(f"results/tous-les-dépeçages-de-{qui}.csv","w")
        self.dépecer_f.write("qui,quoi,vaut\n")

    def empiler_animaux(self,animal,letype,quoi,valeur) :
        """test et empile les caractéristiques des extractions"""
        if animal not in self.animaux :
            self.animaux[animal] = {'letype' : letype}
        if quoi in self.animaux[animal] :
            self.animaux[animal][quoi] = self.animaux[animal][quoi] + valeur
        else:
            self.animaux[animal][quoi] = valeur

    def début_session(self,quand_unix,fichier) :
        """! début de session
        @param quand_unix timestamp unix
        @param fichier nom du fichier

        rend la valeur (en timestamp) au delà de laquelle on peut faire l'analyse de ligne.
        -1 par défaut
        """
        return self.récent

    def fin_session(self) :
        """! fin de la session (le fichier)
        déclenche des actions de maj de fichier
        """
        return None

    def fin_analyse(self) :
        """! plus de fichier à analyser
        déclenche des actions de maj de fichier
        """

        self.dépecer_f.close()
        if not self.i_skinned :
            unlink(self.dépecer_f.name)

        return None

    def analyser_ligne(self,ligne) :
        """analyse une ligne pour
        * voir qui a trouvé
        * combien j'ai donné (don sortant si j'ai tout donné)
        """
        tmp_rec = self.skin_re.match(ligne)
        if tmp_rec is None : return 0
        qui = qui_stat = 'moi'
        if tmp_rec.group('qui') is not None :
            qui = qui_stat = tmp_rec.group('qui')
        quoi   = tmp_rec.group('quoi')
        letype = tmp_rec.group('type')
        vaut   = int(tmp_rec.group('vaut'))
        part   = tmp_rec.group('part')
        self.empiler_animaux(quoi,letype,'combien',1)
        if qui == 'moi' :
            if self.skea > 0 and letype == 'fur' :
                qui_stat = f"moi s{self.skea}"
            if self.dentir > 0 and letype == 'mandibles' :
                qui_stat = f"moi d{self.dentir}"

            self.empiler_animaux(quoi,letype,'total',vaut)
            if part is None :
                self.empiler_animaux(quoi,letype,'Don sortant',vaut)
            else :
                ipart = int(part)
                self.empiler_animaux(quoi,letype,'mes parts',ipart)
                if vaut > ipart :
                    self.empiler_animaux(quoi,letype,'Don sortant',vaut - ipart)
        else :
            if part is not None :
                self.empiler_animaux(quoi,letype,'Don entrant',int(part))
            else :
                return 0

        self.i_skinned = True
        self.dépecer_f.write(f"{qui_stat},{quoi},{vaut}\n")
        return 1

    def trier_resultats(self,a,b) :
        """trier selon un certain ordre"""

        for o in self.ordra :
            tmp_a = tmp_b = 0
            if o in self.animaux[a] : tmp_a = self.animaux[a][o]
            if o in self.animaux[b] : tmp_b = self.animaux[b][o]
            if tmp_a == tmp_b : continue
            return tmp_b - tmp_a
        if a < b : return -1
        else : return 1

    def afficher(self) :
        """affiche le resultat"""

        print(f"\n\t\t \x1b[31mDépeçage pour {self.moi}\x1b[0m\n")
        idx_ligne = 0
        ligne = " " * 30 + " :  # ,  Σ  , moi ,  ->m,  m->,  profit."
        print(f"\x1b[1m{ligne}\x1b[0m")
        for a in sorted(self.animaux,key=cmp_to_key(lambda a,b : self.trier_resultats(a,b))) :
            ligne = f"{a:30.30} "
            c = s = 0
            idx_ligne = idx_ligne + 1
            for o in self.ordre :
                val = " "
                v0 = 0
                if o in self.animaux[a] : v0 = val = self.animaux[a][o]
                if o == 'combien'   :
                    c = v0
                    ligne = ligne + f", {val:3}"
                    continue
                if o == 'total'     :
                    if v0 > 10000 :
                        v0 = int(v0) / 10000
                        ligne = ligne + f",{v0:4d}K"
                        continue
                if o == 'mes parts' : s = v0
                ligne = ligne + f", {val:4}"
            ratio = s / c
            if ratio > 0.1 :
                ligne = ligne + f", {ratio:5.2f} c/tête"
            if idx_ligne % 5 == 0 :
                print(f"\x1b[4m{ligne}.\x1b[0m")
            else :
                print(ligne + ".")

    def chercher_afficher(self,quoi) :
        """affiche le resultat"""

        ligne = " " * 30 + " :  # ,  Σ  , moi ,  ->m,  m->,  profit."
        entete_tty = f"\n\t \x1b[31mDépeçage pour {self.moi}\x1b[0m ({quoi})\n" + ligne
        entete_dict = f"Dépeçage pour {self.moi}"
        idx_ligne = 0
        exacte = False
#        quoi = quoi.lower()
        if quoi[0] == "=" :
            exacte = True
            quoi = quoi[1:]
        for a in sorted(self.animaux,key=cmp_to_key(lambda a,b : self.trier_resultats(a,b))) :
            if exacte and a.lower() != quoi :
                continue
            if a.lower().find(quoi) == - 1 :
                continue
            if entete_tty is not None :
                print(entete_tty)
                entete_tty = None
            ligne = f"{a:30.30} "
            c = s = 0
            idx_ligne = idx_ligne + 1
            for o in self.ordre :
                val = " "
                v0 = 0
                if o in self.animaux[a] : v0 = val = self.animaux[a][o]
                if o == 'combien'   :
                    c = v0
                    ligne = ligne + f", {val:3}"
                    continue
                if o == 'total'     :
                    if v0 > 10000 :
                        v0 = int(v0) / 10000
                        ligne = ligne + f",{v0:4d}K"
                        continue
                if o == 'mes parts' : s = v0
                ligne = ligne + f", {val:4}"
            ratio = s / c
            if ratio > 0.1 :
                ligne = ligne + f", {ratio:5.2f} c/tête"
            if idx_ligne % 5 == 0 :
                print(f"\x1b[4m{ligne}.\x1b[0m")
            else :
                print(ligne + ".")
        if entete_tty is None : print("\n")
                
    def print_csv(self) :
        """! calcul le csv si il y a lieu"""
        if len(self.animaux) == 0 :
            return None
        with open(self.chemin_csv,'w',newline='') as csv_file :
            tmp_ordre = tmp_entete = dict()
            tmp_entete['nom'] = 'nom'
            for o in self.ordre :
                tmp_entete[o] = o
            ecrire = csv.DictWriter(csv_file,fieldnames=tmp_entete)
            ecrire.writeheader()
            for a in self.animaux :
                tmp_ordre['nom'] = a
                for o in self.ordre :
                    if o in self.animaux[a] :
                        tmp_ordre[o] = self.animaux[a][o]
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


class butin:
    """Compile les butins"""

    def __init__(self) :
        """! initialise la regex et les tableaux"""

        self.butin    = dict()
        self.butin_re = re.compile(r"Your share in the (?P<total>[0-9]+)c (?P<quoi>[\w ]+) bounty is (?P<part>[0-9]+)c.")

    def empiler(self,quoi,total,part) :

        if quoi in self.butin :
            self.butin[quoi]['total'] = self.butin[quoi]['total'] + int(total)
            self.butin[quoi]['part'] = self.butin[quoi]['part'] + int(part)
            self.butin[quoi]['combien'] = self.butin[quoi]['combien'] + 1
        else :
            self.butin[quoi] = {'total' : int(total) , 'part' : int(part) , 'combien' : 1}

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

        tmp_butin = self.butin_re.search(ligne)
        if tmp_butin is None : return 0
        self.empiler(tmp_butin.group('quoi'),tmp_butin.group('total'),tmp_butin.group('part'))
        return 1

    def afficher(self) :

        print("\n\t\t \x1b[31mButin\x1b[0m\n")
        print(" " * 31 + " # ,  Σ  , ->m")
        for b in sorted(self.butin) :
            ligne = f"{b:30.30} "
            ligne = ligne + f"{self.butin[b]['combien']:3d}, {self.butin[b]['total']:4d}, {self.butin[b]['part']:3d}"
            print(ligne)

    def generer_fichier(self) :
        """!génere les fichers annexes ci besoin
        * aucun fichier généré
        """

        return None
