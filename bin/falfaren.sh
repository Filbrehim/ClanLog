#!/bin/bash

mkdir -p ~/tmp365/data-clanlord

rsync --archive \
      ~/ClanLord/Text\ Logs/* ~cl.balangar/Copie/Text\ Logs/ \
      ~/tmp365/data-clanlord

cat <<EOF|tee {data,results,tmp}/CACHEDIR.TAG 
Signature: 8a477f597d28d172789f06886806bc55
dernières mise à jour $(date "+%A %e %B %T")
EOF
if ping -c 3 falfaren
then
    rsync --archive *                      falfaren:Sources/ClanLord
    rsync --archive ~/tmp365/data-clanlord falfaren:tmp365
fi
