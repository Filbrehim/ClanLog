#!/bin/bash

find data/Balangar/ -type f -mtime -7 \
     -exec grep -f lib/casual-grep.txt --no-filename {} + |
    awk '$3 == "Midnight" { printf "\t%c[31m%s%c[0m\n",27,$0,27;next ;}
    	/Midnight/ { next;}
         {print}'
