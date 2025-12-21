#!/usr/bin/python3
# -*- coding: utf-8 -*-

from functools import cmp_to_key
from json import dump,load
from os import path
import re
import xml.etree.cElementTree as ET


class professions:
    """! analyse de la progession des professions
    @section professions Cartographie des professeurs

    * mesure des niveaux à partir de l'expérience
    * correction pour les professeurs combinants
    * affichage par catégorie
    * génération d'un CSV,XML 
    * retenir les fichiers déja visités

    """

    appréciations = dict()
    ## @var appréciations
    # * les appréciations reçues,
    # * le niveau
    # * le domain (cf professeurs)

    cache = False
    ## @var cache
    # utilisation d'un cache
    # * False => ne pas utiliser de cache
    # * True => utiliser (voir paramètres dans cache_param)
    
    compliments = dict()
    ## @var compliments
    # la liste des compliments possible (avec leurs bornes), chargé depuis un csv

    dernier_prof = None
    ## @var dernier_prof
    # le dernier professeur étudié
    
    professeurs = dict()
    ## @var professeurs
    # pour chaque professeur :
    # * le domaine (soin/général/langue/PF/corps)
    # * le message de progrés
    # (jonction difficile pour les professeurs similaires (Sprtus/spirit, Bodrus/Hardia)

    session_ts_apres = -1
    ## @var session_ts_apres
    # ne lit que les fichiers après le ts
    
    totaux = dict()
    ## @var totaux
    # le total explicite pour chaque profession

    incohérences = None
    ## @var incohérences
    # les incohérence niveau/appréciations

    dernier_fichier = None
    
    def __init__(self,qui,/,arguments = None) :
        """! initialisation des messages de progression
        @param qui le personnage dont on analyse les logs
        @param arguement = None (l'analyse de la ligne de commande)

        * doit être instancié pour qui (Hail, qui. You ...)
        * utilise les fichiers `messages.csv` et `compliments.csv` pour construire l'analyse.
        """
        
        self.moi           = qui
        self.bow           = False
        self.incliner      = ""
        self.appréciation_re = re.compile('^(?P<qui>[A-Za-z ]+) says, "Hail, ' + qui + r'.\s+(?P<comment>[A-Za-z ]+)."')
        "l'expression régulière qui capture les compliments du professeur"
        self.dernier_pm    = 'says, "Welcome aboard.'
#        self.chemin_csv    = f"results/félicitations-{qui}.csv"
# en attente génération csv digne de ce nom
        self.nolonger_re   = re.compile("no longer train with (?P<qui>[^.]+).")
        self.total         = 0
        self.incohérences  = open(f"results/incohérences-{qui}.txt","w")
        
        if arguments is not None and arguments.cache :
            self.cache = True
            self.cache_param = dict()
            self.cache_param["fichier"] = f"results/cache-profession-{qui}.json"
            if arguments.repertoire != "data" :
                self.cache_param["fichier"] = "tmp/cache-{chemin}-profession-{qui}.json"\
                    .format(chemin=arguments.repertoire.replace("/","!"),qui=qui)
            self.dernier_ts_unix = 0
            self.lire_cache()
            self.session_ts_apres = self.dernier_ts_unix
            
        with open("lib/messages.csv","r") as message_f :
            for ligne in message_f :
                tmp_l = ligne.split(';')
                self.professeurs[tmp_l[0]] = {'progrés' : tmp_l[1] ,
                                              'domaine' : tmp_l[2]}
                if len(tmp_l) > 3 and len(tmp_l[3]) > 5 :
                    self.professeurs[tmp_l[0]]['redirection'] = tmp_l[3]
                if len(tmp_l) > 4 and len(tmp_l[4]) > 5 :
                    self.professeurs[tmp_l[0]]['professeur'] = tmp_l[4]

        with open("lib/compliments.csv","r") as compliments_f :
            for ligne in compliments_f :
                tmp_l = ligne.split(';')
                if len(tmp_l) < 2 : continue
                self.compliments[tmp_l[2]] = {'min': int(tmp_l[0]) , 'max': int(tmp_l[1])}

    def début_session(self,quand_unix,fichier) :
        """! début de session
        @param quand_unix timestamp unix
        @param fichier nom du fichier

        rend la valeur (en timestamp) au delà de laquelle on peut faire l'analyse de ligne.
        -1 par défaut
        """
        self.dernier_ts_unix = quand_unix
        self.dernier_fichier = fichier
        return self.session_ts_apres

    def fin_session(self) :
        """! fin de la session (le fichier)
        déclenche des actions de maj de fichier
        """
        return None

    def fin_analyse(self) :
        """! plus de fichier à analyser
        déclenche des actions de maj de fichier
        """
        self.incohérences.close()
        return None

    def analyser_ligne(self,ligne) :
        """! analyse une ligne pour
        @param ligne la ligne à analyser

        * une progression d'un métier
        * une appréciation d'un professeur
        * plus possible de progresser
        * le dernier professeur (sauf pour les chemins)

        """
        tmp_app = self.appréciation_re.match(ligne)
        if tmp_app is not None :
            p = tmp_app.group('qui')
            comment = tmp_app.group('comment')
            if p in self.appréciations :
                self.appréciations[p]['comment'] = comment
            else :
                self.appréciations[p] = {'niveau' : 0 , 'comment' : comment}
            return 1

        for p1 in self.professeurs :
            if self.bow :
                for tmp_c in self.compliments :
                    if ligne.find(tmp_c) != -1 :
                        if self.incliner in self.appréciations :
                            self.appréciations[self.incliner]['comment'] = tmp_c
                        else :
                            self.appréciations[self.incliner] = { 'comment' : tmp_c , 'niveau' : 550  }
                        return 1
            self.bow = False
            if (ligne.find(p1+" bows") != -1 ) or (ligne.find(p1+" bows deeply") != -1)  :
                self.bow = True
                self.incliner = p1
                return 1
            if self.professeurs[p1]['progrés'] == "*commun*" :
                if 'professeur' in self.professeurs[p1] :
                    if self.professeurs[p1]['professeur'] in ligne :
                        self.dernier_prof = p1
                continue
            if self.professeurs[p1]['progrés'] in ligne :
                p = p1
                if p1.find("*last*") != -1 and self.dernier_prof is not None :
                    p = self.dernier_prof
                self.total = self.total + 1

                if self.professeurs[p1]['domaine'] in self.totaux :
                    self.totaux[self.professeurs[p1]['domaine']] = self.totaux[self.professeurs[p1]['domaine']] + 1
                else :
                    self.totaux[self.professeurs[p1]['domaine']] = 1
                if p in self.appréciations :
                    self.appréciations[p]['niveau'] = self.appréciations[p]['niveau'] + 1
                else :
                    self.appréciations[p] = {'niveau' : 1 ,
                                             'comment' : '** sans commentaire ** (Jules César)'}
                ## vérifier Evus/Eva
                if p1[0:2] == "Ev" and self.appréciations[p]['comment'] != '** sans commentaire ** (Jules César)' :
                    a = p1
                    if (self.appréciations[a]['niveau'] + 1 < self.compliments[self.appréciations[a]['comment']]['min']) :
                        print(f"{a:17} sous estimé, calculé:{self.appréciations[a]['niveau']:3d}, compliment {self.appréciations[a]['comment']}, min={self.compliments[self.appréciations[a]['comment']]['min']}",file=self.incohérences)
                    if (self.appréciations[a]['niveau'] - 1 > self.compliments[self.appréciations[a]['comment']]['max']) :
                        print(f"{a:17} sur estimé, calculé:{self.appréciations[a]['niveau']:3d}, compliment {self.appréciations[a]['comment']}, max={self.compliments[self.appréciations[a]['comment']]['max']}",file=self.incohérences)
##                       or (self.appréciations[a]['niveau'] > self.compliments[self.appréciations[a]['comment']]['max']) :
                return 1
        nolonger = ligne.find("ou can no longer train with ")
        if nolonger != - 1 :
            tmp_comment = ligne[nolonger - 1:ligne.find('.')]
            tmp_m = ligne[nolonger + 28:]
            qui = tmp_m[0:tmp_m.find('.')]
            if qui in self.appréciations :
                self.appréciations[qui]['comment'] = tmp_comment
                return 1

        if ligne.find(self.dernier_pm) != -1 :
            self.dernier_prof = ligne[:ligne.find(self.dernier_pm) - 1]
            return 1
        return 0

    def afficher_métier(self,a,/,tout=1) :
        """! afficher un métier:
        @param a le nom du professeur
        @param tout (facultatif) si 1, affiche des informations triviales.

        on affiche
        * professeur
        * niveau connu (nom de progression recencées)
        * compliment
        * niveau estimé (si calculabe)
        * plage (à partir du compliment, si pas compatible avec le niveau connu)
        """
        if tout == 1 :
            if (self.appréciations[a]['niveau'] > 0) or (self.appréciations[a]['comment'] != "You have much to learn") :
                print(f"{a:17} : {self.appréciations[a]}")
        else :
            ligne = f"{a:17} "
            ligne_i = 0
            niveau_caché = False
            if self.appréciations[a]['niveau'] > 0 :
                ligne = ligne + f" {self.appréciations[a]['niveau']:3d}, "
                ligne_i = ligne_i + 1
            else :
                ligne = ligne + " " * 6
            if (self.appréciations[a]['comment'] != "You have much to learn") \
               or (self.appréciations[a]['niveau'] > 0) :
                if 'sans commentaire' not in self.appréciations[a]['comment'] :
                    ligne = ligne + f"{self.appréciations[a]['comment']:35}"
                    ligne_i = ligne_i + 1
            if 'corrigé' in self.appréciations[a] :
                niveau_caché = True
                ligne = ligne + f" ( {self.appréciations[a]['corrigé']:d}? )"
                ligne_i = ligne_i + 1
            if self.appréciations[a]['comment'] in self.compliments :
                if niveau_caché \
                   or (self.appréciations[a]['niveau'] < self.compliments[self.appréciations[a]['comment']]['min']) \
                   or (self.appréciations[a]['niveau'] > self.compliments[self.appréciations[a]['comment']]['max']) :
                    ligne = ligne + f" ({self.compliments[self.appréciations[a]['comment']]['min']} - {self.compliments[self.appréciations[a]['comment']]['max']})"
                    ligne_i = ligne_i + 1
            if ligne_i > 0 : print(ligne)

    def trier_métier(self,m1,m2):
        """! trie deux métiers
        * par ordre de profession décroissante
        @param m1,m2 les deux professeurs à comparer
        """

        s_m1 = self.résumé_métier(m1)
        s_m2 = self.résumé_métier(m2)

        if s_m1 != s_m2 : return s_m2 - s_m1
        if m1 < m2 : return -1
        else : return 1

    def trier_totaux(self,c1,c2):
        """! trie les totaux
        * par importance, puis alphabétique
        @param c1,c2 les catégories
        """
        if self.totaux[c1] != self.totaux[c2] :
            return self.totaux[c1] - self.totaux[c2]

    def résumé_métier(self,m):
        """!
        @param m le métier (professeur)

        donne le résumé (niveau)

        * le niveau minimal (si > mesuré) __ou__
        * le niveau corrigé (si ≠ mesuré) __ou__
        * le niveau mesuré
        """

        s_m1 = self.appréciations[m]['niveau']
        if self.appréciations[m]['comment'] in self.compliments :
            if s_m1 < self.compliments[self.appréciations[m]['comment']]['min'] :
                s_m1 = self.compliments[self.appréciations[m]['comment']]['min']
        if 'corrigé' in self.appréciations[m] : s_m1 = self.appréciations[m]['corrigé']
        return s_m1

    def pousser_objectif(self,qui,combien,pourquoi=" "):
        """!
        @param qui le professeur
        @param combien le niveau minimal
        @param pourquoi l'éventuelle raison

        empile un objectif (et son résultat)
        l'objectif de combien pour qui est atteint ?
        """

        if qui not in self.appréciations :
            return
        tmp_obj = self.résumé_métier(qui)
        préfixe = ""
        manque = combien - tmp_obj
        if manque > 0  :
            if pourquoi[0] == "<" :
                préfixe = f"[31m{tmp_obj:3d}[0m"
            cible_ko = chr(9678)
            atteint = f"\t{cible_ko}  il manque {manque:3} pour {qui:20} {préfixe} {pourquoi}"
        else:
            cible_ok = chr(127919)
            préfixe = f"[32m{tmp_obj:3d}[0m"
            atteint = f"\t\t{cible_ok}       pour {qui:20} {préfixe} \u2265 {combien}, {pourquoi}"
            if pourquoi[0] == "<" :
                pourquoi = pourquoi[2:]
                atteint = f"\t\t{cible_ok}       pour {qui:20} {préfixe} \u2265 {pourquoi}"

        if not hasattr(self,'liste_objectifs') :
            self.liste_objectifs = dict()
        self.liste_objectifs[qui + pourquoi] = {'score' : manque, 'quoi':atteint}

    def lister_objectif(self) :
        """! affiche les objectifs par ordre de réalisation """
        if hasattr(self,'liste_objectifs') :
            tmp_o = sorted(self.liste_objectifs,
                           key=cmp_to_key(lambda a,b:self.liste_objectifs[b]['score'] - self.liste_objectifs[a]['score']))
            for o in tmp_o :
                print(self.liste_objectifs[o]['quoi'])

    def afficher(self) :
        """! afficher les professions par catégorie"""

        self.correction_globale()

        tmp_as = sorted(self.appréciations,
                        key=cmp_to_key(lambda a,b :self.trier_métier(a,b)))
        tmp_tt = sorted(self.totaux,
                        key=cmp_to_key(lambda a,b:self.totaux[b] - self.totaux[a]))

        tmp_a  = self.appréciations
        tmp_i  = 0
        print(f"\n\t\t \x1b[31mProfession : {self.total:3d}\x1b[0m")
        for a in tmp_as :
            if a in self.professeurs :
                tmp_a[a]['domaine'] = self.professeurs[a]['domaine']

        for t in tmp_tt :
            pct = self.totaux[t] / self.total
            print(f"\n\t\t \x1b[40m{t:10} : {self.totaux[t]:3d}, ({pct:2.0%})\x1b[0m")
            for a in tmp_as :
                if 'domaine' in tmp_a[a] :
                    if tmp_a[a]['domaine'] == t :
                        self.afficher_métier(a,tout=0)
                else :
                    tmp_a[a]['domaine'] = 'inconnu'
                    if (self.appréciations[a]['niveau'] > 0) or (self.appréciations[a]['comment'] != "You have much to learn") :
                        tmp_i = tmp_i + 1

        if tmp_i == 0 :
            print("")
            return
        print("\n\t\t Y'en reste ?")
        for a in tmp_a :
            if tmp_a[a]['domaine'] == 'inconnu' :
                del tmp_a[a]['domaine']
                self.afficher_métier(a)

    def correction_multiple(self,qui,liste) :
        """! calcul les corrections des profs multiples """
        if qui in self.appréciations :
            correction = 0
            for li in liste :
                if li[0] in self.appréciations :
                    correction = correction + self.appréciations[li[0]]['niveau'] * li[1]
            self.appréciations[qui]['corrigé'] = int(self.appréciations[qui]['niveau'] + correction)

    def correction_indiv(self,qui,coef,ref) :
        """! calcule les corrections d'un seul prof """
        if qui in self.appréciations and ref in self.appréciations :
            self.appréciations[qui]['corrigé'] = int(self.appréciations[qui]['niveau'] + coef * self.appréciations[ref]['niveau'])

    def correction_globale(self) :
        """ apporte les corrections avant d'imprimer .txt et .csv
        * cf http://gorvin.50webs.com/CLRev/healer.html
        """
        self.correction_multiple('Faustus',[('Eva',0.333),('Sprite',0.303)])
        self.correction_multiple('Higgrus',[('Eva',0.25) ,('Sprite',0.10),('Master Bodrus',0.2),('Hardia',0.175)])
        self.correction_multiple('Sespus',[('Eva',0.275),('Sprite',0.24)])
        self.correction_multiple('Respia',[('Eva',0.375),('Sprite',0.208)])
        self.correction_indiv('Horus',0.060,'Eva')
        self.correction_indiv('Awaria',0.060,'Eva')
        self.correction_indiv('Hardia',1,'Master Bodrus')
        self.correction_indiv('Master Bodrus',1,'Hardia')

        self.correction_indiv('Atkus',0.25,'Evus')
        self.correction_indiv('Histia',0.216,'Evus')
        self.correction_indiv('Swengus',0.571,'Evus')
                              

    def print_csv(self) :
        return None

    def print_xml(self) :
        """! génère un fichier XML
        * n'affiche que les catégories, avec en attribut
         + le nom
         + le total
         + le pourcentage
        (en construction)
        """
        self.correction_globale()

        tmp_a  = self.appréciations
        for a in tmp_a :
            if a in self.professeurs :
                tmp_a[a]['domaine'] = self.professeurs[a]['domaine']

        root = ET.Element("root")
        doc = ET.SubElement(root,"document")
        prof = ET.SubElement(doc,"profession")
        ET.SubElement(prof,"qui").text = self.moi
        for t in self.totaux :
            pct = self.totaux[t] / self.total
            tmp_c = ET.SubElement(prof,"Catégorie")
            tmp_c.set("nom",t)
            tmp_c.set("total",f"{self.totaux[t]}")
            tmp_c.set("pourcentage",f"{pct:2.0%}")
            for a in tmp_a :
                if 'domaine' in tmp_a[a] and tmp_a[a]['domaine'] == t :
                    if self.résumé_métier(a) == 0 : continue
                    tmp_p = ET.SubElement(tmp_c,"métier")
                    ET.SubElement(tmp_p,"Professeur").text = a
                    ET.SubElement(tmp_p,"Combien").text = str(self.résumé_métier(a))
                    ET.SubElement(tmp_p,"Mesuré").text = str(tmp_a[a]['niveau'])
                    ET.SubElement(tmp_p,"Commentaire").text = tmp_a[a]['comment']

        tree = ET.ElementTree(root)
        tree.write(f"results/professions-{self.moi}.xml",encoding='utf-8')

    def écrire_cache(self) :
        """!génère le fichier cache avec
        * dernier_unix
        * les appréciations
        * le total et les totaux
        * le dernier professeur
        """

        tmp_cache = {
            'dernier_ts_unix' : self.dernier_ts_unix ,
            'appréciations' : self.appréciations,
            'total' : self.total,
            'totaux' :  self.totaux,
            'dernier_prof' : self.dernier_prof }
        with open(self.cache_param["fichier"],"w") as cache_fp :
            dump(tmp_cache,cache_fp)

    def lire_cache(self) :
        """!lecture fichier cache (si il existe)
        * dernier_unix
        * les appréciations
        * le total et les totaux
        * le dernier professeur
        sinon : rien
        """

        if path.isfile(self.cache_param["fichier"]) :
            with open(self.cache_param["fichier"],"r") as cache_fp :
                résumé = load(cache_fp)
                self.dernier_ts_unix = résumé["dernier_ts_unix"]
                self.appréciations = résumé['appréciations']
                self.dernier_prof = résumé['dernier_prof']
                self.totaux = résumé['totaux']
                self.total = résumé['total']

            
    def generer_fichier(self) :
        """!génere les fichers annexes ci besoin
        * CSV et XML
        * le fichier cache, le cas échéant
        """

        if self.cache : self.écrire_cache()
        self.print_xml()
