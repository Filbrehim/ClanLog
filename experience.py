#!/usr/bin/python3
# -*- coding: utf-8 -*-

import argparse
from lib import profession
from locale import LC_TIME,setlocale
import os
from time import mktime,strftime,strptime,time

setlocale(LC_TIME, 'fr_FR.utf8')

parser = argparse.ArgumentParser(description="calcul les plus grandes montées de niveaux (les conditions sont relieés par un 'ou')")
parser.add_argument('--directory','--repertoire',
                    action='store',dest='repertoire',default='data',
                    help='le répertoire avec les CL*')
parser.add_argument('-l','--lignes',action='store',dest='lignes',default=500,type=int,
                    help="résumé que pour les sessions de plus de LIGNES lignes (500)")
parser.add_argument('-n','--niveaux',action='store',dest='niveaux',default=5,type=int,
                    help="résumé que pour les sessions de plus de NIVEAUX niveaux (5)")
parser.add_argument('-a',action='store_true',dest='tous',default=False,
                    help="affiche toutes les dates (60 jours sinon)")

args,reste = parser.parse_known_args()
if len(reste) == 0 :
    print("il manque le destinataire")
    exit(1)

p1 = profession.professions(reste[0])
début = time()

experience = 0
base_data = f"{args.repertoire}/{reste[0]}"

for fichier in sorted(os.listdir(base_data)):
    if fichier.startswith('CL') :
        lignec = 0
        with open(f"{base_data}/{fichier}","r") as fp :
            for ligne in fp :
                lignec = lignec + 1
                p1.analyser_ligne(ligne)
        quand = strptime(fichier[7:26],"%Y-%m-%d %H.%M.%S")
        if (lignec > args.lignes or p1.total - experience >= args.niveaux) \
          and (args.tous or (début - mktime(quand)) < 60 * 86400) :
            if p1.total - experience == 0 :
                ratio = ""
            elif experience > 999 :
                ratio = "{r:6.2f} ‰".format(r=1000 * (p1.total - experience) / experience)
            elif experience > 99 :
                ratio = "{r:6.2f} %".format(r=100 * (p1.total - experience) / experience)
            elif experience > 0 :
                ratio = "{r:3d}    %".format(r=int(100 * (p1.total - experience) / experience))
            else:
                ratio = " " * 8
                ## garder un pour mille ‰ # noqa: E266
            if (args.tous) :
                j2 = fichier[7:23]
            else :
                j2 = strftime("%a %e %b %H:%M",quand)

            print("{j:19}, montée de {n:3d} niveaux ({av:4d} -{total:4d}) {r}".
                  format(j=j2,av=experience,n=p1.total - experience,
                         total=p1.total,r=ratio))
        experience = p1.total

p1.afficher()
