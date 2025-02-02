#!/bin/bash

DESTINATION=~/tmp365/data-clanlord
## echo ${DESTINATION}
mkdir -p ${DESTINATION}

for destination in ${DESTINATION}
do
    
rsync --archive \
      ~/ClanLord/Text\ Logs/* ~cl.balangar/Copie/Text\ Logs/ \
      ${destination}

done

cat <<EOF|tee {data,results,tmp}/CACHEDIR.TAG 
Signature: 8a477f597d28d172789f06886806bc55
dernières mise à jour $(date "+%A %e %B %T")
EOF

systemctl --user start compile-clanlord.service &

journalctl  --user --follow 

