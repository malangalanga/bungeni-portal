<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema" exclude-result-prefixes="xs" version="2.0">

    <xsl:output media-type="text/html" method="xhtml"/>

    <xsl:variable name="path_file" select="tokenize(resolve-uri('types.xsl'),'/')[last()]" />
    <xsl:variable name="path_file_prefix" select="tokenize($path_file, '\.')[1]" />
    <xsl:variable name="folder_file" select="substring-before(resolve-uri('types.xsl'), $path_file)" />
    
    <xsl:variable name="types_with_ws" select="document(concat($folder_file, '.types_ws.xml'))/types" />

    <xsl:template name="html_head">
        <head>
            <link rel="stylesheet" type="text/css" href="docs.css" /> 
            <title>Bungeni Document Types</title>
        </head>
    </xsl:template>
    
    <xsl:template match="types">
        <html>
          <xsl:call-template name="html_head" />
          <xsl:call-template name="html_body" />  
        </html>
    </xsl:template>
    
    <xsl:template name="html_body">
        <body>
            <xsl:call-template name="types_info" />     
            <xsl:call-template name="custom_archetypes" />     
            <xsl:call-template name="all_docs" />     
            <xsl:call-template name="all_events" />
            <xsl:call-template name="all_groups" />
        </body>
    </xsl:template>
    
    <xsl:template name="types_info" >
        <h1 class="main">Parliamentary Type Information </h1>
        <ul style="font-family:arial;">
            <li>Parliament Type : 
                <xsl:choose>
                    <xsl:when test="@bicameral eq 'true'">Bicameral</xsl:when>
                    <xsl:otherwise>Unicameral</xsl:otherwise>
                </xsl:choose></li>
            <li>Country Code : <xsl:value-of select="@country_code" /></li>
        </ul>
    </xsl:template>
    
    
    <xsl:template name="custom_archetypes" >
       <xsl:call-template name="type_generator">
           <xsl:with-param name="heading">
               <xsl:text>Custom Archetypes</xsl:text>
           </xsl:with-param>
           <xsl:with-param name="docs_select" select="doc[@descriptor eq 'doc']" />
       </xsl:call-template>
    </xsl:template>
    
    <xsl:template name="all_docs" >
        <xsl:call-template name="type_generator">
            <xsl:with-param name="heading">
                <xsl:text>All Doc Types</xsl:text>
            </xsl:with-param>
            <xsl:with-param name="docs_select" select="./doc[@descriptor ne 'doc' or not(@descriptor)]" />
        </xsl:call-template>
    </xsl:template>
    
    <xsl:template name="all_events" >
        <xsl:call-template name="type_generator">
            <xsl:with-param name="heading">
                <xsl:text>All Event Types</xsl:text>
            </xsl:with-param>
            <xsl:with-param name="docs_select" select="./event" />
        </xsl:call-template>
    </xsl:template>
    
    <xsl:template name="all_groups" >
        <xsl:call-template name="type_generator">
            <xsl:with-param name="heading">
                <xsl:text>All Groups</xsl:text>
            </xsl:with-param>
            <xsl:with-param name="docs_select" select="./group" />
        </xsl:call-template>
    </xsl:template>
    
    <xsl:template name="members_generator">
        <xsl:param name="docs_select" />
        <xsl:param name="heading" />
        <xsl:for-each select="$docs_select">
            <h3 style="margin-below:1px;">
                <xsl:value-of select="@name" />
                <xsl:choose>
                    <xsl:when test="@enabled">
                        <xsl:choose>
                            <xsl:when test="@enabled eq 'true'">
                                (Enabled)
                            </xsl:when>
                            <xsl:otherwise>
                                (Disabled)
                            </xsl:otherwise>
                        </xsl:choose>
                    </xsl:when>
                    <xsl:otherwise>
                        (Enabled)
                    </xsl:otherwise>
                </xsl:choose>
            </h3>
            <ul>
                <li>Workflow : 
                    <xsl:call-template name="render_wf" />
                </li>
                <li>
                    Listings appears as: <xsl:value-of select="@container_label" />, Item type is shown as:<xsl:value-of select="@label" /> 
                </li>
            </ul>
        </xsl:for-each>
    </xsl:template>
    
    <xsl:template name="render_wf">
        <xsl:choose>
            <xsl:when test="@workflow">
                <xsl:call-template name="render_wf_link">
                    <xsl:with-param name="wf_name">
                        <xsl:value-of select="@workflow" />
                    </xsl:with-param>
                </xsl:call-template>
            </xsl:when>
            <xsl:otherwise>
                <xsl:call-template name="render_wf_link">
                    <xsl:with-param name="wf_name">
                        <xsl:value-of select="@name" />
                    </xsl:with-param>
                </xsl:call-template>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>
    
    <xsl:template name="render_wf_link">
        <xsl:param name="wf_name" />
        <a href="{concat('wf_', $wf_name, '.html')}"><xsl:value-of select="$wf_name" /></a>
    </xsl:template>

    <xsl:template name="render_fm">
        <xsl:choose>
            <xsl:when test="@descriptor">
                <xsl:call-template name="render_fm_link">
                    <xsl:with-param name="fm_name">
                        <xsl:value-of select="@descriptor" />
                    </xsl:with-param>
                </xsl:call-template>
            </xsl:when>
            <xsl:otherwise>
                <xsl:call-template name="render_fm_link">
                    <xsl:with-param name="fm_name">
                        <xsl:value-of select="@name" />
                    </xsl:with-param>
                </xsl:call-template>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>
    
    
    <xsl:template name="render_fm_link">
        <xsl:param name="fm_name" />
        <a href="{concat('fm_', $fm_name, '.html')}"><xsl:value-of select="$fm_name" /></a>
    </xsl:template>
    
    
    
    <xsl:template name="type_generator">
        <xsl:param name="heading" />
        <xsl:param name="docs_select" />
        <h2 class="index"><xsl:value-of select="$heading" /></h2>
        <table border="1">
            <thead>
                <tr class="yellow">
                    <th>Name</th>
                    <th>Form</th>
                    <th>Workflow</th>
                    <th>Workspace</th>
                    <th>Enabled</th>
                    <th>Labels</th>
                </tr>
            </thead>
            <tbody>
                <xsl:for-each select="$docs_select">
                    <xsl:sort select="@name" />
                    <tr class="m{position() mod 2}">
                        <td>
                            <xsl:value-of select="@name" />

                        </td>
                        <td>
                            <xsl:call-template name="render_fm" />
                        </td>
                        
                        <td>
                            <xsl:call-template name="render_wf" />
                        </td>
                        
                        <td>
                            <xsl:variable name="t_name" select="@name" />
                            <xsl:variable name="ws_match" select="count($types_with_ws/type[. eq $t_name])" />
                            <xsl:choose>
                                <xsl:when test="$ws_match &gt; 0">
                                    <a href="{concat('ws_', $t_name, '.html')}"><xsl:value-of select="$t_name" /></a>
                                </xsl:when>
                                <xsl:otherwise>
                                    N/A
                                </xsl:otherwise>
                            </xsl:choose>
                        </td>
                        <td><xsl:choose>
                            <xsl:when test="@enabled">
                                <xsl:choose>
                                    <xsl:when test="@enabled eq 'true'">Yes</xsl:when>
                                    <xsl:otherwise>No</xsl:otherwise>
                                </xsl:choose>     
                            </xsl:when>
                            <xsl:otherwise>
                                Yes
                            </xsl:otherwise>
                        </xsl:choose>
                        </td>
                        <td style="text-align:left;">
                          <ul>
                            <li>Item Type: 
                            <xsl:choose>
                                <xsl:when test="@label">
                                    <xsl:value-of select="@label" />
                                </xsl:when>
                                <xsl:otherwise>
                                    N/A
                                </xsl:otherwise>
                            </xsl:choose>                                     
                            </li>
                            <li>Listing: 
                            <xsl:choose>
                                <xsl:when test="@container_label">
                                    <xsl:value-of select="@container_label" />
                                </xsl:when>
                                <xsl:otherwise>
                                    N/A
                                </xsl:otherwise>
                            </xsl:choose> 
                            </li>
                          </ul>
                        </td>
                    </tr>
                    <xsl:if test="name() eq 'group'">
                        <xsl:if test="child::member">
                            <tr>
                                <td>
                                    Members Info for <xsl:value-of select="@name" />
                                </td>
                                <td colspan="5" style="text-align:left; vertical-align:top">
                                    <xsl:call-template name="members_generator">
                                        <xsl:with-param name="docs_select" select="./member"/>
                                        <xsl:with-param name="heading">Group members</xsl:with-param>
                                    </xsl:call-template>
                                </td>
                            </tr>
                        </xsl:if>    
                    </xsl:if>
                </xsl:for-each>
            </tbody>
        </table>
    </xsl:template>
    
    
</xsl:stylesheet>