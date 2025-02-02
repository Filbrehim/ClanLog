#!/bin/bash

destination="/home_secure/www/html/Puddleby/log"
mkdir -p "${destination}"

doxygen | tee ${destination}/doxygen-log.txt
echo; echo; echo
flake8  | tee ${destination}/flake8-log.txt
awk -f bin/flake8.awk ${destination}/flake8-log.txt > ${destination}/flake8-log.html
