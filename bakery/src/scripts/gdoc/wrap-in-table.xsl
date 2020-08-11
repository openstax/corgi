<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<xsl:template match="@*|node()">
  <xsl:copy>
    <xsl:apply-templates select="@*|node()"/>
  </xsl:copy>
</xsl:template>

<xsl:template match="*[@data-type='note']">
  <xsl:call-template name="wrapper">
    <xsl:with-param name="label">NOTE</xsl:with-param>
  </xsl:call-template>
</xsl:template>

<xsl:template match="*[@data-type='example']">
  <xsl:call-template name="wrapper">
    <xsl:with-param name="label">EXAMPLE</xsl:with-param>
  </xsl:call-template>
</xsl:template>

<xsl:template match="*[@data-type='exercise']">
  <xsl:call-template name="wrapper">
    <xsl:with-param name="label">EXERCISE</xsl:with-param>
  </xsl:call-template>
</xsl:template>

<xsl:template name="wrapper">
  <xsl:param name="label"/>

  <table class="not-used-but-wraps-a-feature">
    <tr><th><xsl:value-of select="$label"/></th></tr>
    <tr>
      <td>
        <xsl:copy>
          <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
      </td>
    </tr>
  </table>
</xsl:template>

</xsl:stylesheet>