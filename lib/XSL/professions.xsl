<?xml version="1.0"?>
<xsl:stylesheet
version="1.0"
xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
>

  <xsl:output method="html" />

  <xsl:template match="//profession">
    <xsl:element name="script">
      document.title =  "<![CDATA[⚒]]> <xsl:value-of select="qui" />"
    </xsl:element>
    <xsl:element name="H3">
      <xsl:value-of select="qui" />
    </xsl:element>
    <p align="center">Ses métiers</p>
    <table align="center" border="1">
      <xsl:for-each select="Catégorie">
	<xsl:sort select="@total" data-type="number" order="descending" />
	<tr>
	  <th colspan="2"><xsl:value-of select="@nom"/></th>
	  <td align="center"><xsl:value-of select="@total"/> (<xsl:value-of select="@pourcentage"/>)</td>
	</tr>
	<xsl:for-each select="métier">
	  <xsl:sort select="Combien" data-type="number" order="descending" />
	  <tr>
	    <td>               <xsl:value-of select="Professeur"/> </td>
	    <td align="right">
	      <xsl:if test="Combien = Mesuré"> <xsl:value-of select="Combien"/></xsl:if>
	      <xsl:if test="Combien != Mesuré">
		<div class="commentaire">
		  ~<xsl:value-of select="Combien"/>
		  <xsl:if test="Mesuré != 0">/<xsl:value-of select="Mesuré"/></xsl:if>
		</div>
	      </xsl:if>
	    </td>
	    <td align="center">
	      <div class="commentaire"><xsl:value-of select="Commentaire"/></div>
	    </td>
	  </tr>
	</xsl:for-each>
    </xsl:for-each>
    </table>
  </xsl:template>
  
</xsl:stylesheet>
