#!/usr/bin/python3
# -*- coding: utf-8 -*-


class métrique:
    """calcul la volumétrie des lignes analysées"""

    def __init__(self) :
        """initialisation des métriques"""
        self.lignes  = 0
        self.total   = 0
        self.bruit   = 0
        self.derniereligne = 0

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
        """mesurer la longueur"""
        self.derniereligne = len(ligne)
        self.lignes = self.lignes + 1
        self.total = self.total + self.derniereligne

    def dubruit(self) :
        """la dernière ligne est du bruit"""
        self.bruit = self.bruit + self.derniereligne
        self.derniereligne = 0

    def afficher(self) :
        """afficher les statistiques"""
        print(f"\nil a {self.lignes:,} lignes pour un total de {self.total:,} charactères".replace(","," "))
        signal = self.total - self.bruit

        message = "\tdont {signal:,} de signal ({sig_pm:.1f} %)".format(signal=signal,sig_pm=100 * signal / self.total)
        message = message + f"\n\tet {self.bruit:,} de bruit"
        print(message.replace(","," "))

    def generer_fichier(self) :
        """!génere les fichers annexes ci besoin
        * aucun fichier annexes pour les métriques
        """
        return None
