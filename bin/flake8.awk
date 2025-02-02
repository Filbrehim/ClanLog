BEGIN { FS = ":" ;
    avant = "" ;
    printf "<table align=center border=1>\n" ; }

{ if ( $1 != avant ) printf "<tr><th colspan=2>%s</th></tr>\n",$1 ;
    printf "<tr><th>%d</th><td>%s - %s</td></tr>\n",$2,$3,$4 ;
    avant = $1 ;
}

END { print "</table>" ; }
