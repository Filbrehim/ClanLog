<?xml version="1.0"?>
<xsl:stylesheet
version="1.0"
xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
>

  <xsl:output method="text" />

<xsl:template match="/datablock">
  il y a <xsl:copy-of select="clanners/population" /> exilés, dont
<xsl:for-each select="clanners/exile"> - <xsl:value-of select="name" />, <xsl:value-of select="race"/>.
</xsl:for-each>
  <xsl:for-each select="./announcements/announcement[type='Congrats']" >
 - félicitation à <xsl:value-of select="awardee"/> <xsl:value-of select="message"/>
  </xsl:for-each>
.
</xsl:template>

</xsl:stylesheet>
