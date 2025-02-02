<?xml version="1.0"?>
<xsl:stylesheet
version="1.0"
xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
>

  <xsl:output method="text" />
<xsl:template match="/datablock">
  <xsl:for-each select="./announcements/announcement[type='Congrats']" >
    <xsl:variable name="squote"><xsl:text>'</xsl:text></xsl:variable>
    <xsl:variable name="uuid" select="translate(concat(translate(awardee,$squote,''),'---',message),' ','')" />

<![CDATA[cat <<finfin > ~/.tmp24/new-congrat]]>-<xsl:value-of select="$uuid"/>.json
{
 "titre" : "Congratulation to <xsl:value-of select='awardee'/> who <xsl:value-of select='message'/>",
 "auteur" : "<xsl:value-of select='messenger'/>" ,
 "uuid" : "<xsl:value-of select='$uuid' />" ,
 "_quand_unix" : $(date -d<xsl:value-of select="time" />  +'%s') ,
 "posté" : "$(date -d<xsl:value-of select="time" />  +'%A %e %kh%M')",
 "quoi" : "<xsl:value-of select='message' />" ,
 "forum" : "Puddleby" ,
 "type" : "rumeur"
}

finfin
multicast-annonce.py --clanlord json=~/.tmp24/new-congrat-<xsl:value-of select="$uuid"/>.json
sleep 2

</xsl:for-each>

</xsl:template>
</xsl:stylesheet>
