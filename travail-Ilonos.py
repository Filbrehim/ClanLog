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
#parser.add_argument('-r','--ratio',action='store_false',
#                    help="ne calcul pas le ratio Eva/Sprite")
parser.add_argument('-o','--objectif',action='store_false',
                    help="ne calcul pas les objectifs")

qui = "Ilonos"
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

if args.objectif :
    print("\n - Objectifs")
    p1.pousser_objectif('Master Mentus',20,"franchir le portail sans encombre")
    evus = p1.résumé_métier('Evus')
    obj = evus // 5
    raison = f"< {obj} (Eva={evus}) divisé par 5"
    p1.pousser_objectif('Dentir Longtooth',obj,raison)
    p1.pousser_objectif('Skea Brightfur',obj,raison)
    obj = evus // 10
    raison = f"< {obj} un dixième de (Eva={evus})"
    p1.pousser_objectif('Loovma Geer',obj,raison)
    p1.lister_objectif()
