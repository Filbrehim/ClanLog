#!/usr/bin/python3
# -*- coding: utf-8 -*-

import re
from time import time
import xml.etree.cElementTree as ET


class finances:
    """! divers (finances)
    @section finances

    * cacule les frais de bibliothèque
    * le dernier midnight
    """

    def __init__(self,qui) :
        """! initialisation des messages de progression
        @param qui le personnage dont on analyse les logs

        """

        self.moi       = qui
        self.finance   = dict()
        self.coin_re   = re.compile("^You have (?P<piece>[0-9]+) coins.")
        self.charge_re = re.compile("• You have been charged (?P<piece>[0-9]+) coin(s)? for advanced studies.")

    def analyser_ligne(self,ligne) :
        """! analyse une ligne pour
        @param ligne la ligne à analyser

        * des sousous (aquis ou dépensés)
        """

        piepiece = self.coin_re.match(ligne)
        if piepiece is not None :
            self.finance['pièces'] = int(piepiece.group('piece'))
            return 1
        piepiece = self.charge_re.match(ligne)
        if piepiece is not None :
            intitulé = 'séjours à la biliothèque'
            total    = 'total des frais'
            if intitulé in self.finance :
                self.finance[intitulé] = self.finance[intitulé] + 1
                self.finance[total] = self.finance[total] + int(piepiece.group('piece'))
            else :
                self.finance[intitulé] = 1
                self.finance[total] = int(piepiece.group('piece'))
            return 1
        if ligne.find("You have no coins.") != -1 :
            self.finance['pièces'] = 0
            return 1
        if ligne.find("You have a single coin.") != -1 :
            self.finance['pièces'] = 1
            return 1
        return 0

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

    def afficher(self) :
        """! affiche ma fortune et mes dépenses de libraries"""

        print("\n\t\t \x1b[31mO Fortuna !\x1b[0m\n")
        for f in self.finance :
            if f[0:5] == 'total' :
                print(f" * {f} {self.finance[f]} pièces.")
                continue
            if f == "pièces" :
                if self.finance[f] == 0 :
                    print(" * fauché !")
                    continue
                if self.finance[f] == 1 :
                    print(" * une seule pièce")
                    continue
            print(f" * {self.finance[f]} {f}.")

    def generer_fichier(self) :
        """!génere les fichers annexes ci besoin
        * aucun fichier annexes pour les finances
        """


class minuit:
    """! date : retrouve le dernier minuit
    @section minuit

    * le dernier midnight
    """

    def __init__(self,qui) :
        """! initialisation des messages de progression
        @param qui le personnage dont on analyse les logs

        """

        self.moi       = qui
        self.début     = int(time()) - 8 * 86400
        self.factures  = dict()
        self.dépenses  = {'maison': 'fees for your home',
                          'consigne': f'{qui}, your locker'}
        # @var dépenses
        # les chaines fixes à rechercher

        self.minuit    = "une époque ancienne"
        # @var minuit
        # le dernier minuit

    def analyser_ligne(self,ligne) :
        """! analyse une ligne pour
        @param ligne la ligne à analyser

         * l'heure de connexion
         * le dernier minuit
         * les dépenses
           ** consignes
           ** maison(s)
        """
        self.nb_ligne = self.nb_ligne + 1
        if self.nb_ligne < 20 :
            if ligne.find("It's") > -1 :
                self.factures['heure'] = ligne[:-1]
                return 1
        if ligne.find("Midnight on") > -1 :
            self.minuit = ligne[19:-1]
            return 1
        for d in self.dépenses :
            if ligne.find(self.dépenses[d]) > -1 :
                self.factures[d] = ligne[:-1]
                return 1
        return 0

    def début_session(self,quand_unix,fichier) :
        """! début de session
        @param quand_unix timestamp unix
        @param fichier nom du fichier

        rend la valeur (en timestamp) au delà de laquelle on peut faire l'analyse de ligne.
        -1 par défaut
        """
        self.nb_ligne = 0
        self.factures["dernière session"] = fichier[7:]
        return self.début

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

    def afficher(self) :
        """! affiche ma fortune et mes dépenses de libraries"""

        print(f"\n * {self.minuit}")
        for f in self.factures :
            print(f" * {f:10} : {self.factures[f]}")
        map(lambda f : print(f" * {f:10} : {self.factures[f]}"),self.factures)

    def print_xml(self) :
        """! génère le fichier XML
        root / document / divers / *
        pas d'attribut, juste la phrase tel quelle
        """

        root = ET.Element("root")
        doc = ET.SubElement(root,"document")
        liste = ET.SubElement(doc,"divers")
        ET.SubElement(liste,"moi").text = self.moi
        if "époque" not in self.minuit :
            ET.SubElement(liste,"minuit").text = self.minuit
        for f in self.factures :
            if " " not in f :
                ET.SubElement(liste,f).text = self.factures[f]
        tree = ET.ElementTree(root)
        tree.write(f"results/divers-{self.moi}.xml",encoding='utf-8')

    def generer_fichier(self) :
        """!génere les fichers annexes ci besoin
        * aucun fichier annexes pour les finances
        """
        self.print_xml()


def delta_ts_humain(d) :
    """
    convertir un delta de timestamp en format humain
    si d négatif, on est dans le futur
    """
    tmp_format = "%A %e %B"
    tmp_delta = "il y a {j} jours".format(j=int(d / 86400))
    if d < 7 * 86400 : tmp_format = "%A %e à %k hr."
    if d < 2 * 86400 :
        tmp_format = "%A %e à %k:%M"
        tmp_delta = "il y a {h} heures".format(h=int(d / 3600))
    if d <     86400 : tmp_format = "%A à %k:%M"
    if d < 6 *  3600 : tmp_format = "%T"
    if d < 2 *  3600 : tmp_delta = "il y a {m} minutes".format(m=int(d / 60))
    if d <       120 : tmp_delta = "il y a {s} secondes".format(s=int(d))
    if d == 0 :
        tmp_format = "à l'instant"
        tmp_delta  = ""
    if d <       -120 :
        tmp_delta = "dans {s} secondes".format(s=int(-d))
        tmp_format = "%T"
    if d < -2 *  3600 : tmp_delta = "dans {m} minutes".format(m=int(-d / 60))
    if d < -6 *  3600 :
        tmp_format = "%A à %k:%M"
        tmp_delta = "dans {h} heures".format(h=int(-d / 3600))
    if d <     -86400 : tmp_format = "%A à %k:%M"
    if d < -2 * 86400 :
        tmp_format = "%A %e à %k:%M"
    if d < -7 * 86400 :
        tmp_format = "%A %e à %k hr."
        tmp_delta = "dans {j} jours".format(j=int(-d / 86400))

    return tmp_format,tmp_delta
