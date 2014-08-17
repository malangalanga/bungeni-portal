<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema" exclude-result-prefixes="xs" version="2.0">
    
    <xsl:output media-type="text/html" method="xhtml"/>
    
    <xsl:variable name="type_name" select="tokenize(tokenize(base-uri(),'/')[last()], '\.')[1]" />
    
    <xsl:template name="html_head">
        <head>
            <link rel="stylesheet" type="text/css" href="docs.css" /> 
            <title><xsl:value-of select="$type_name" /></title>
        </head>
    </xsl:template>
    
    <xsl:template match="descriptor">
        <html>
            <xsl:call-template name="html_head" />
            <xsl:call-template name="html_body" />  
        </html>
    </xsl:template>
    
    <xsl:template name="fields_table_header">
        <thead>
            <tr>
                <th>Field Name</th>
                <th>Label</th>
                <th>Description</th>
                <th>Required?</th>
                <th>Field Type</th>
                <th>Rendered as</th>
                <th>Mode Info</th>
            </tr>
        </thead>
    </xsl:template>
    
    <xsl:template name="field_required">
        <xsl:choose>
            <xsl:when test="@required eq 'true'">
                Yes
            </xsl:when>
            <xsl:otherwise>
                No
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>
    
    <xsl:template name="field_modes">
        <!-- render modes -->
        <xsl:variable name="vmodes" as="element()*">
            <mode>add</mode>
            <mode>view</mode>
            <mode>edit</mode>
            <mode>listing</mode>
        </xsl:variable>
        
        <xsl:variable name="vshow" select="./show"/>
        <xsl:variable name="vshow-modes">
            <xsl:value-of select="$vshow/@modes"/>
        </xsl:variable>
        
        <xsl:variable name="vhide" select="./hide"/>
        <xsl:variable name="vhide-modes">
            <xsl:value-of select="$vhide/@modes"/>
        </xsl:variable>
        
        <table border="1">
            <tr class="gray">
                <td>Customizable</td>
                <td>Visibility</td>
            </tr>
            <xsl:for-each select="$vmodes">
                <xsl:variable name="current-mode" select="."/>
                <tr>
                    <!-- localizable -->
                    <td>
                        <xsl:value-of select="$current-mode"/>
                    </td>
                    
                    <!-- show / hide -->
                    <td>
                        <xsl:choose>
                            <xsl:when
                                test="not(empty($vshow)) or not(empty($vhide))">
                                <xsl:choose>
                                    <!-- if it is in the show list it must be shown -->
                                    <xsl:when
                                        test="contains($vshow-modes, $current-mode)"> Show </xsl:when>
                                    <xsl:otherwise>
                                        <!-- if it is not in show, it may be hidden 
                                            so we explicitly check in hidden modes -->
                                        <xsl:choose>
                                            <!-- if it is in the hide modes list , it is hidden -->
                                            <xsl:when
                                                test="contains($vhide-modes, $current-mode)"> Hide </xsl:when>
                                            <!-- otherwise it is shown -->
                                            <xsl:otherwise> Show </xsl:otherwise>
                                        </xsl:choose>
                                    </xsl:otherwise>
                                </xsl:choose>
                            </xsl:when>
                            <xsl:otherwise> Show (dependent upon permissions)
                            </xsl:otherwise>
                        </xsl:choose>
                    </td>
                </tr>
            </xsl:for-each>
        </table>                                
        
    </xsl:template>
    
    <xsl:template name="fields_table_body">
        <tbody>
            <xsl:for-each select="./field">
            <tr class="m{position() mod 2}">
                <td><xsl:value-of select="@name" /></td> 
                <td><xsl:value-of select="@label" /></td> 
                <td><xsl:value-of select="@description" /></td> 
                <td><xsl:call-template name="field_required" /></td> 
                <td><xsl:call-template name="field_value_type" /></td> 
                <td><xsl:value-of select="@render_type" /></td>
                <td><xsl:call-template name="field_modes" /></td>
            </tr>                         
            </xsl:for-each>
        </tbody>
    </xsl:template>
    
    <xsl:template name="fields">
        <table border="1">
            <xsl:call-template name="fields_table_header" />
            <xsl:call-template name="fields_table_body" />
        </table>
    </xsl:template>
    
    <xsl:template name="html_body">
        <body>
            <h1 class="main"><xsl:value-of select="$type_name" /></h1>
            <!--
            <field name="title" label="Title" required="true" value_type="text" render_type="text_box">
                <show modes="add view edit listing" />
            </field>
            -->
            <xsl:call-template name="fields" />
        </body>
    </xsl:template>
    
    
    <xsl:template name="field_value_type">
        <xsl:choose>
            <xsl:when test="@value_type eq 'vocabulary'">
                <xsl:value-of select="@value_type" /><br />
                <em>(<xsl:value-of select="@vocabulary" />)</em>
            </xsl:when>
            <xsl:otherwise>
                <xsl:value-of select="@value_type" />
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>
    
</xsl:stylesheet>