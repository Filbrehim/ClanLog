#!/bin/bash

cd /home_secure/zartog/Sources/ClanLord

LOGFILE=$(mktemp --tmpdir=tmp --suffix=.log compile-CL-XXXXXXXXX)

./all-log-no-tty.py Balangar Korancha Goupil GrisePlume &
./all-log-no-tty.py Forkalir &
./all-log-no-tty.py Ilonos &

wait
echo "compilation Balangar, Forkalir et Ilonos OK en ${SECONDS} seconds" > ${LOGFILE}
bin/web-it.sh >> ${LOGFILE}

cp ${LOGFILE} tmp/dernière-compilation.log
