#!/usr/bin/python3
# -*- coding: utf-8 -*-

from re import compile
import xml.etree.cElementTree as ET


class familier:
    """! analyse de la progression des familiers"""

    def __init__(self,qui,victoires,/,debug=0) :
        """! initialisation des tableaux
        @param qui nom du familier
        @param victoires classe des victoires pour déclencher les actions de changement de niveau.
        """
        self.debug     = debug
        self.moi       = qui
        self.fortus    = f"{qui} grows stronger."
        self.fortus_n  = f"{qui} grows much stronger! (But you must go to the stable to train more.)"
        self.bell_message = f"The bell rings soundlessly into the void, summoning {qui} through the shadows."
        self.appel     = { 'appel' : 0 ,
                           'crumble' : 0 ,
                           'dernier_appel' : False ,
                           'suite' : "" }
        self.étape     = []
        self.étape_idx = 0
        self.étape_continue = 0
        self.lasty     = [ { 'message' : f"{qui} vanquished" , 'score' : 4 },
                           { 'message' : f"{qui} killed" , 'score' : 2 },
                           { 'message' : f"{qui} dispatched" , 'score' : 1 } ]
        self.fortus_l  = {}
        self.étape.append(self.étape_idx)
        self.étape[self.étape_idx] = 1
        self.victoire  = victoires

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
        * progression plus fort
        """

        for l1 in self.lasty :
            if ligne.find(l1['message']) != -1 :
                tmp_idx = self.étape[self.étape_idx] + 100 * self.étape_idx
                if tmp_idx in self.fortus_l :
                    self.fortus_l[tmp_idx] = self.fortus_l[tmp_idx] + l1['score']
                else :
                    self.fortus_l[tmp_idx] = l1['score']
                return 1
        if ligne.find(self.fortus) != -1 :
            self.étape[self.étape_idx] = self.étape[self.étape_idx] + 1
            self.étape_continue = self.étape_continue + 1
            self.victoire.palier_familier(self.étape_continue)
            return 1
        if ligne.find(self.fortus_n) != -1 :
            self.étape_idx = self.étape_idx + 1
            self.étape.append(self.étape_idx)
            self.étape[self.étape_idx] = 1
            self.étape_continue = self.étape_continue + 1
            self.victoire.palier_familier(self.étape_continue)
            return 1
        if ligne.find("Your bell crumbles to dust.") != -1 \
           and self.appel['dernier_appel'] :
            self.appel['crumble'] = self.appel['crumble'] + 1
            self.appel['suite'] = self.appel['suite'][:-1] + chr(128277)  # cloche brisée
            return 1
        self.appel['dernier_appel'] = False
        if ligne.find(self.bell_message) != -1 :
            self.appel['appel'] = self.appel['appel'] + 1
            self.appel['suite'] = self.appel['suite'] + chr(128276)
            self.appel['dernier_appel'] = True
            return 1
        return 0

    def afficher(self) :
        """affiche le resultat"""

        # status_txt = "A" * self.appel['appel'] + "/" + self.appel['crumble'] * "C"
        if self.appel['appel'] > 0  :
            print(f"\n\t\t \x1b[31mévolution pour {self.moi}\x1b[0m\n\t{self.appel['suite']}\n")
        else :
            print(f"\n\t\t \x1b[31mévolution pour {self.moi}\x1b[0m\n")

        tmp_idx = 0
        while tmp_idx <= self.étape_idx :
            print(" * étape {e} : ({c}) {s}".format(e=tmp_idx,s="*" * self.étape[tmp_idx],c=self.étape[tmp_idx]))
            tmp_idx_sub = 1
            tmp_idx_étape = 100 * tmp_idx + 1
            tmp_avant = 0
            while tmp_idx_étape in self.fortus_l :
                tmp_a1 = self.fortus_l[tmp_idx_étape]
                ligne = f"\t{tmp_idx_sub:2d} => {tmp_a1:4d}"
                if tmp_avant > 0 :
                    tmp_pc = 100 * (tmp_a1 - tmp_avant) / tmp_avant
                    ligne = ligne + f" {tmp_pc:6.1f}%"
                print(ligne)
                tmp_idx_étape = tmp_idx_étape + 1
                tmp_idx_sub = tmp_idx_sub + 1
                tmp_avant = tmp_a1
            tmp_idx = tmp_idx + 1

    def generer_fichier(self) :
        """!génere les fichers annexes ci besoin
        * aucun fichier annexes pour les familiers
        """
        return None


class grinoter:
    """! grinoter
    @section finances
    liste les familier qui ont grinoter des douces baies 
    """
    
    liste = dict()
    ## @param liste
    # la liste des familiers
    
    def __init__(self,qui,/,arguments=None) :
        """! initialisation des messages de progression
        @param qui le personnage dont on analyse les logs

        """

        self.moi             = qui
        self.dernier_fichier = "?"
        self.nibbles_re      = compile("^(?P<qui>[A-Za-z ]+) nibbles at the sweet berries.")

    def analyser_ligne(self,ligne) :
        """! analyse une ligne pour
        @param ligne la ligne à analyser

        * des sousous (aquis ou dépensés)
        """

        compagnon = self.nibbles_re.match(ligne)
        if compagnon is not None :
            qui = compagnon.group('qui')
            if qui not in self.liste :
                self.liste[qui] = self.dernier_fichier
                return 1
        return 0

    def début_session(self,quand_unix,fichier) :
        """! début de session
        @param quand_unix timestamp unix
        @param fichier nom du fichier

        * rend la valeur (en timestamp) au delà de laquelle on peut faire l'analyse de ligne.
        * retient le nom du fichier
        -1 par défaut
        """
        self.dernier_fichier = fichier
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

        if len(self.liste) > 0 :            
            print("\n\t\t \x1b[31mMes compagnons !\x1b[0m\n")
            idx = 1
            for c in sorted(self.liste) :
                print(f" {idx:2} {c:15} {self.liste[c][7:-7]}")
                idx = idx + 1

    def generer_fichier(self) :
        """!génere les fichers annexes ci besoin
        * la liste des compagnons
        """

        self.print_xml()

    def print_xml(self) :
        """! génère le fichier XML
        root / document / compagnons / familier / nom + quand(texte) *
        pas d'attribut, juste la phrase tel quelle
        """

        if len(self.liste) == 0 : return
        root = ET.Element("root")
        doc = ET.SubElement(root,"document")
        liste = ET.SubElement(doc,"compagnons")
        ET.SubElement(liste,"moi").text = self.moi
        for c in self.liste :
            tmp_c = ET.SubElement(liste,"familier")
            ET.SubElement(tmp_c,"nom").text = c
            ET.SubElement(tmp_c,"quand").text = self.liste[c][7:-7]
        tree = ET.ElementTree(root)
        tree.write(f"results/compagnons-{self.moi}.xml",encoding='utf-8')
