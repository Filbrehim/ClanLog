#!/bin/bash

case $(hostname) in

    dathomir )
	
	DESTINATION=~/tmp365/data-clanlord
	mkdir -p ${DESTINATION}

	for destination in ${DESTINATION}
	do
	    
	    rsync --archive \
		  ~/ClanLord/Text\ Logs/* ~cl.balangar/Copie/Text\ Logs/ \
		  ${destination}

	    systemctl --user start compile-clanlord.service &

	    journalctl  --user --follow 

	done
	;;

    falfaren )
	
	DESTINATION=data
	for destination in ${DESTINATION}
	do
    
	    rsync --archive --verbose \
		  ~/ClanLord.Shatrah.ro/ClanLord.win32/data/Text\ Logs/* ~/ClanLord/Text\ Logs/* \
		  ${destination}

	done
	;;
esac

cat <<EOF|tee {data,results,tmp}/CACHEDIR.TAG 
Signature: 8a477f597d28d172789f06886806bc55
dernières mise à jour $(LC_TIME=fr_FR.utf-8 date "+%A %1d %B %T")
EOF
