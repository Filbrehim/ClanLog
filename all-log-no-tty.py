#!/usr/bin/python3
# -*- coding: utf-8 -*-

import argparse
import os
import sys
from time import mktime,strptime

from lib import divers,familier,métrique,profession,skinndent,vaincu

parser = argparse.ArgumentParser(description="analyse les logs de ClanLord")
parser.add_argument('--bounty','--butin',action='store_true',dest='bounty',
                    help='calcul le butin')
parser.add_argument('-3','--core3',action='store_true',dest='core3',
                    help='ne prend que Skinn, kill et profession')
parser.add_argument('--directory','--repertoire',
                    action='store',dest='repertoire',default='data',
                    help="""le répertoire avec les Text Logs/* de CL
                    (celui du dessus, le nom du personnage est ajouté)""")
parser.add_argument('-ç','--dépeçage-récent',action='store',
                    dest='dépeçage',default=0,type=int,
                    help="limite la durée de l'analyse des dépeçage")
parser.add_argument('--nocache',action='store_false',dest='cache',
                     help='ne pas générer ou utiliser de cache')
parser.add_argument('--nocsv','--noresults',action='store_true',help="ne génère pas les fichiers de résultat")
parser.add_argument('-k','--nokills',action='store_true',dest='nokills',
                    help="ne caclul pas l'art et la manière de tuer")
parser.add_argument('-s','--noskins',action='store_true',dest='noskins',
                    help='ne caclul pas les skins')
parser.add_argument('-p','--noprofs',action='store_true',dest='noprofs',
                    help='ne compile pas les professions')

args,reste = parser.parse_known_args()

if len(reste) == 0 :
    print("il manque le destinataire et ses éventuels familiers")
    exit(1)

chercher = {'vaincu': vaincu.chasse(reste[0]),
            'peaux' : skinndent.peauetdent(reste[0],arguments=args),
            'prof'  : profession.professions(reste[0],arguments=args),
            # à retirer dynamiquement si l'option core3 est appelée
            'divers': divers.finances(reste[0]),
            'minuit': divers.minuit(reste[0])
            }

métrique = métrique.métrique()

dentir_skin = True

if args.bounty and not args.core3 :
    chercher['butin'] = skinndent.butin()
if args.core3 :
    del chercher['divers']
    del chercher['minuit']
if args.noskins :
    del chercher['peaux']
    dentir_skin = False
if args.noprofs :
    del chercher['prof']
    dentir_skin = False
if args.nokills :
    del chercher['vaincu']
else:
    c = 0 
    for r in reste[1:] :
        chercher['V-' + r] = vaincu.chasse(r,fam=True)
        chercher['S-' + r] = familier.familier(r,chercher['V-' + r])
        c = c + 1
    if c > 0 :
        chercher['compagnons'] = familier.grinoter(reste[0],arguments=args)

base_data = f"{args.repertoire}/{reste[0]}"
for fichier in sorted(os.listdir(base_data)):
    if fichier.startswith('CL'):
        quand = mktime(strptime(fichier[7:26],"%Y-%m-%d %H.%M.%S"))
        c2 = dict()
        for c in chercher :
            if quand > chercher[c].début_session(quand,fichier) :
                c2[c] = chercher[c]
        with open(f"{base_data}/{fichier}","r") as fp :
            if dentir_skin :
                qui = "Dentir Longtooth"
                if qui in chercher['prof'].appréciations :
                    chercher['peaux'].dentir = \
                        int(chercher['prof'].appréciations[qui]['niveau'])
                qui = "Skea Brightfur"
                if qui in chercher['prof'].appréciations :
                    chercher['peaux'].skea = \
                        int(chercher['prof'].appréciations[qui]['niveau'])

            for ligne in fp :
                métrique.analyser_ligne(ligne)
                s1 = 0
                for c in c2 :
                    s1 = s1 + c2[c].analyser_ligne(ligne)
                if s1 == 0 :
                    métrique.dubruit()
        for c in chercher :
            chercher[c].fin_session()

for c in chercher :
    chercher[c].fin_analyse()

if sys.stdout.isatty() :
    for c in chercher :
        chercher[c].afficher()
    métrique.afficher()

for c in chercher :
    if not args.nocsv :
        chercher[c].generer_fichier()
