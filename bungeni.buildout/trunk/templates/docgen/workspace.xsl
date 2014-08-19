<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema" exclude-result-prefixes="xs" version="2.0">
    
    <xsl:output media-type="text/html" method="xhtml"/>
    
    <xsl:variable name="path_file" select="tokenize(base-uri(),'/')[last()]" />
    <xsl:variable name="path_file_prefix" select="tokenize($path_file, '\.')[1]" />
    <xsl:variable name="folder_file" select="substring-before(base-uri(), $path_file)" />
        
    <xsl:variable name="tabs" select="document(concat($folder_file, 'tabs.xml'))/tabs" />
    
    <xsl:variable name="root" select="/" />
    
    <xsl:template name="html_head">
        <head>
            <link rel="stylesheet" type="text/css" href="docs.css" /> 
            <title>Workspace Configuration : <xsl:value-of select="$path_file_prefix" /></title>
        </head>
    </xsl:template>
    
    <xsl:template match="workspace">
        <html>
            <xsl:call-template name="html_head" />
            <xsl:call-template name="html_body" />  
        </html>
    </xsl:template>
    
    <xsl:template name="html_body">
        <h1 class="main">Workspace configuration for : <xsl:value-of select="$path_file_prefix" /> </h1>
            <xsl:for-each select="$tabs/tab">
                <xsl:variable name="tab_id" select="@id" />
                <h2>tab : <xsl:value-of select="$tab_id" /></h2>
                <table border="1">
                    <thead>
                       <tr class="gray">
                        <th>State</th>
                        <th>Roles</th>
                       </tr>
                    </thead>
                    <tbody>
                        <xsl:for-each-group 
                            select="$root//state[tab[@id eq $tab_id]]" 
                            group-by="tab" >
                            <xsl:for-each 
                                select="current-group()">
                                <xsl:sort select="@id" />
                                <tr class="m{position() mod 2}">
                                    <!-- state -->
                                    <td>
                                        <a href="{concat('wf_', $path_file_prefix, '.html#', @id)}">
                                        <xsl:value-of select="@id" />
                                        </a>
                                    </td>
                                    <!-- roles -->
                                    <td style="text-align:left"><xsl:variable name="roles" 
                                                 select="tokenize(normalize-space(./tab[@id eq $tab_id]/@roles), '\s+')" />
                                        <xsl:choose>
                                            <xsl:when test="count($roles) &gt; 1">
                                                <ul>
                                                    <xsl:for-each select="$roles">
                                                        <li><xsl:value-of select="normalize-space(.)" /></li>    
                                                    </xsl:for-each>
                                                </ul>
                                            </xsl:when>
                                            <xsl:when test="count($roles) eq 1">
                                                <xsl:value-of select="normalize-space($roles[1])" />
                                            </xsl:when>
                                            <xsl:otherwise>
                                                N/A
                                            </xsl:otherwise>
                                        </xsl:choose>
                                        <!--
                                        <xsl:for-each select="$roles">
                                            <xsl:value-of select="normalize-space(replace(.,'&quot;',''))" />
                                            <xsl:if test="position() != last()">
                                                <br />
                                            </xsl:if>
                                        </xsl:for-each> -->
                                    </td>
                                </tr>
                            </xsl:for-each>
                        </xsl:for-each-group>
                    </tbody>     
                </table>
            </xsl:for-each>
    </xsl:template>

</xsl:stylesheet>