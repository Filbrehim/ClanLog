#!/bin/bash

base=$HOME/Sources/ClanLord
depuis="${base}/results"
destination="/home_secure/www/html/Puddleby"

### CSV
rm -f "${destination}/*.csv"
find ${base} -type f -name \*.csv            -mtime -7 -exec cp -p {} "${destination}" \;

make all

# ls ${destination}/{all,professions,ω}-*.html |
#     awk -F/ 'BEGIN { printf "<ol>\n" ; }
#   { printf "<li><a href=%s>%s</a></li>\n",$NF,$NF  ;}
#   END {printf "</ol>\n" ; }' > ${destination}/README.html

printf '<p align="center">' > ${destination}/README.html

for personnage in Balangar Forkalir Ilonos
do
    cat <<EOF >> ${destination}/README.html
<a href="all-${personnage}.html">${personnage}<a> <a href="professions-${personnage}.html">⚒<a> <a href="ω-${personnage}.html">ω<a> --
EOF
done

cat <<EOF >> ${destination}/README.html
 mise à jour $(LANG=fr_FR.utf-8 date "+%A %e %B %Y") </p>
EOF
