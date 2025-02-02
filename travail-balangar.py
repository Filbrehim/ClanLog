#!/usr/bin/python3
# -*- coding: utf-8 -*-

import argparse
from lib import profession
import os
from time import mktime,strptime

parser = argparse.ArgumentParser(description="analyse les logs de ClanLord")
parser.add_argument('--nocache',action='store_false',dest='cache',
                     help='ne pas générer ou utiliser de cache')
parser.add_argument('--directory','--repertoire',
                    action='store',dest='repertoire',default='data',
                    help="""le répertoire avec les Text Logs/* de CL
                    (celui du dessus, le nom du personnage est ajouté)""")
parser.add_argument('-r','--ratio',action='store_false',
                    help="ne calcul pas le ratio Eva/Sprite")
parser.add_argument('-o','--objectif',action='store_false',
                    help="ne calcul pas les objectifs")

qui = "Balangar"
args = parser.parse_args()
p1 = profession.professions(qui,arguments=args)

base_data = f"{args.repertoire}/{qui}"
for fichier in sorted(os.listdir(base_data)):
    if fichier.startswith('CL'):
        quand = mktime(strptime(fichier[7:26],"%Y-%m-%d %H.%M.%S"))
        if quand <= p1.début_session(quand,fichier) :
            continue
        with open(f"{base_data}/{fichier}","r") as fp :
            for ligne in fp :
                if p1.analyser_ligne(ligne) is not None :
                    continue

p1.afficher()

print(f"\n - {p1.dernier_prof} est le dernier professeur")

if args.ratio :
    print("\n - Ratio Eva:Sprite 5:1")
    eva = p1.résumé_métier('Eva')
    sprite = p1.résumé_métier('Sprite')
    r_sprite = 5 * sprite / eva
    if 5 * sprite > eva :
        delta = 5 * sprite - eva
        print(f"\t • il manque {delta} Eva (5/{r_sprite:.3f})")
    else :
        delta = (eva // 5) - sprite
        if delta > 0 :
            print(f"\t • il manque {delta} Sprite (5/{r_sprite:.3f})")

if args.objectif :
    print("\n - Objectifs")
    p1.pousser_objectif('Master Mentus',20,"franchir le portail sans encombre")
    eva = p1.résumé_métier('Eva')
    obj = eva // 4
    raison = f"< {obj} (Eva={eva}) divisé par 4"
    p1.pousser_objectif('Dentir Longtooth',obj,raison)
    p1.pousser_objectif('Skea Brightfur',obj,raison)
    p1.pousser_objectif('Proximus',obj,raison)
    p1.pousser_objectif('Hardia',obj,raison)

    p1.lister_objectif()
