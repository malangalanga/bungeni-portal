<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema" exclude-result-prefixes="xs" version="2.0">
    <xd:doc xmlns:xd="http://www.oxygenxml.com/ns/doc/xsl" scope="stylesheet">
        <xd:desc>
            <xd:p><xd:b>Created on:</xd:b> Jun 14, 2010</xd:p>
            <xd:p><xd:b>Author:</xd:b> Ashok</xd:p>
            <xd:p/>
        </xd:desc>
        <xd:param name="tested-version">r8173</xd:param>
    </xd:doc>
    <xsl:output media-type="text/html" method="xhtml"/>
    
    <!-- Global variable containing content type extracted from Workflow title -->
    <xsl:variable name="wf-content-type">
        <xsl:variable name="tmp">
            <xsl:value-of select="//workflow/@title" />
        </xsl:variable>
        <xsl:value-of select="tokenize($tmp, '\s+')[1]" />
    </xsl:variable>
    
    <!-- Queryable key for state elements on state id -->
    <xsl:key name="query_state" match="//state" use="@id"/>
    
    <xsl:template match="workflow">
        <html>
            <head>
                <title>
                    <xsl:value-of select="@title"/>
                </title>
                <style type="text/css">
                    table {
                        font: 11px/24px Verdana, Arial, Helvetica, sans-serif;
                        border-collapse: collapse;
                        width: 94%;
                    }
                    th {
                        padding: 0 0.5em;
                        text-align: left;
                    }
                    tr.yellow td th {
                        border-top: 1px solid #FB7A31;
                        border-bottom: 1px solid #FB7A31;
                        background: #FFC;
                    }
                    td {
                        border-bottom: 1px solid #CCC;
                        padding: 0 0.5em;
                        vertical-align:top;
                    }
                    td:first-child {
                        width: 190px;
                    }
                    td+td {
                        border-left: 1px solid #CCC;
                        text-align: center;
                    }
                    tr.m0 {
                        background-color: #ffffcc;
                    }
                    tr.m1 {
                        background-color: #ffffff;
                    }
                    tr.s0 {
                        background-color: #eee;
                         
                    }
                    tr.s1 {
                        background-color: #fff;
                         
                    }
                    div.ident {
                        font-style:normal;
                        color:gray;
                         
                    }
                    div.trig {
                        color:dark-gray;
                    }
                    /* * for table of content * */
                    #menu li {
                        display: inline;
                        list-style-type: none;
                        padding-right: 20px;
                    }
                    #menu li a {
                        font-size:0.9em;
                    }
                    .linkbar a {
                        font-size: 0.7em;
                    }
                    .toc-links a {
                        font-size:0.7em;
                    }
                    .note {
                        font-size:0.9em;
                        font-style:italics;
                        font-family:helvetica;
                        color:gray;
                    }
                    h1 {
                        font-family:Helvetica;
                        font-style:bold;
                        font-size:1.3em;
                    }
                    h2 {
                        font-family:Helvetica;
                        font-style:bold;
                        font-size:1.1em;
                    }
                    h3 {
                        font-family:Helvetica;
                        font-style:bold;
                        font-size:0.9em;
                    }
                    h1.main {
                        color:orange;
                    }
                    h1.index {
                        color:gray;
                    }
                    h2.index {
                        color:gray;
                    }</style>
            </head>
            <body>
                <h1 class="main">
                    <xsl:value-of select="@title"/>
                </h1>

                <div id="toc">
                    <a name="table-of-contents"/>
                    <h1 class="index">Document Index</h1> TABLE_OF_CONTENT <!-- The above string is place holder for embedding the global table of documents -->
                    <h2 class="index">Index of <a href="#states">States</a></h2>
                    <div class="toc-links">
                        <xsl:for-each select="//state">
                            <a href="#{@id}"><xsl:value-of select="@title"/></a>
                            <xsl:if test="not(position() = last())">
                                <!-- ADD A COMMA ONLY IF IT IS NOT THE LAST ELEMENT -->
                                <xsl:text>,</xsl:text>
                            </xsl:if> </xsl:for-each>
                    </div>
                    <h2 class="index">Index of <a href="#transitions">Transitions</a></h2>
                    <div class="toc-links">
                        <xsl:for-each select="//transition">
                            <a href="#{generate-id(.)}"><xsl:value-of select="@title"/></a>
                            <xsl:if test="not(position() = last())">
                                <!-- ADD A COMMA ONLY IF IT IS NOT THE LAST ELEMENT -->
                                <xsl:text>,</xsl:text>
                            </xsl:if>
                        </xsl:for-each>
                    </div>
                </div>
                
                <!-- TRANSITIONS -->
                <a name="transitions"/>
                <h3><xsl:value-of select="$wf-content-type"/>:Transitions</h3>
                <div class="linkbar">
                    <a href="#table-of-contents">[Document Index]</a>
                    <xsl:text>,</xsl:text>
                    <a href="#states">[States]</a>
                    <xsl:text>,</xsl:text>
                    <xsl:call-template name="diagram"/>
                </div>
                <table border="1">
                    <thead>                    
                    <tr class="yellow">
                        <th>Transition Name</th>
                        <th>Source</th>
                        <th>Destination</th>
                        <th>Roles</th>
                        <th>Action/Condition</th>                        
                        <th>Confirm?</th>
                    </tr>
                    </thead>
                    <tbody>
                    <xsl:for-each select="./transition">
                        <xsl:call-template name="match-transition"/>
                    </xsl:for-each>
                    </tbody>
                </table>
                <a href="#table-of-contents">[Document Index]</a>
                

                <!-- STATES -->

                <a name="states"/>
                <h3><xsl:value-of select="$wf-content-type"/>:States</h3>
                <div class="linkbar">
                    <a href="#table-of-contents">[Document Index]</a>
                    <xsl:text>,</xsl:text>
                    <a href="#transitions">[Transitions]</a>
                    <xsl:text>,</xsl:text>
                    <xsl:call-template name="diagram"/>
                </div>
                
                <h4>Global Grants</h4>
                <table border="1">
                    <xsl:call-template name="grant-denies">
                       <xsl:with-param name="grant-or-denies" select="./grant" />
                    </xsl:call-template>
                </table>
                
                <h4>State Grants</h4>
                
                <table border="1">
                    <thead>
                    <tr class="yellow">
                        <th>State Name</th>
                        <th>Allow</th>
                        <th>Deny</th>
                    </tr>
                    </thead>
                    <tbody>
                    <xsl:for-each select="./state">
                        <xsl:call-template name="match-state"/>
                    </xsl:for-each>
                    </tbody>
                </table>
                <a href="#table-of-contents">[Document Index]</a>
                
              
            </body>
        </html>
    </xsl:template>

    <!-- This template is called for each <state> -->
    <xsl:template name="match-state">
        <xsl:variable name="counter">
            <xsl:number/>
        </xsl:variable>
        <tr class="m{$counter mod 2}">
            <td>
                <a name="{@id}"/>
                <span class="state-title"><xsl:value-of select="@title"/></span>
                <!-- uncomment the below to show the id on the page -->
                <!--
                <div class="ident">
                    <xsl:value-of select="@id"/>
                </div>
                -->
                <xsl:if test="@like_state">
                    <div> Like:
                        <a href="#{@like_state}">
                            <!-- Query the state key using the id value in like_state and return the title -->
                            <xsl:value-of select="key('query_state',@like_state)/@title" />
                        </a>
                    </div>
                </xsl:if>
                <xsl:if test="@version">
                    <div> Version: <span class="ident"><xsl:value-of select="@version"/></span> </div>
                </xsl:if>
                <xsl:if test="child::notification">
                    <div> Notify: <span class="ident">true</span> </div>
                </xsl:if>
                <xsl:if test="@note">
                    <div class="note">
                        <xsl:value-of select="@note"/>
                    </div>
                </xsl:if>

            </td>
            <td>&#160; <table border="0">
                    <xsl:call-template name="grant-denies">
                        <xsl:with-param name="grant-or-denies" select="./grant">
                        </xsl:with-param>
                    </xsl:call-template>
                </table>`
            </td>
            <td>&#160; <table border="0">
                    <xsl:call-template name="grant-denies">
                        <xsl:with-param name="grant-or-denies" select="./deny">
                        </xsl:with-param>
                    </xsl:call-template>
                </table>
            </td>
        </tr>
    </xsl:template>

    <!-- this template is called for each transition -->
    <xsl:template name="match-transition">
        <xsl:variable name="counter">
            <xsl:number/>
        </xsl:variable>
        <tr class="m{$counter mod 2}">
            <!-- Transition Name -->
            <td>
                <a name="{generate-id(.)}"/>
                <span class="transition-title"><xsl:value-of select="@title"/></span>
                <xsl:choose>
                    <xsl:when test="@trigger='manual'">
                        <div class="trig">(Manual)</div>
                    </xsl:when>
                    <xsl:otherwise>
                        <div class="trig">(Auto)</div>
                    </xsl:otherwise>
                </xsl:choose>
                <!-- Generate the note only if it exists -->
                <xsl:if test="@note">
                    <div class="note">
                        <xsl:value-of select="@note"/>
                    </div>
                </xsl:if>
            </td>
            <!-- Source -->
            <td>
                <xsl:variable name="tokSource" select="tokenize(@source, '\s+')"> </xsl:variable>
                <xsl:for-each select="$tokSource">
                    <a>
                        <xsl:attribute name="href">
                            <xsl:text>#</xsl:text>
                            <xsl:value-of select="."/>
                        </xsl:attribute>
                        <xsl:value-of select="."/>
                    </a>
                    <br/>
                </xsl:for-each>
            </td>
            <!-- Destination -->
            <td>
                <xsl:variable name="tokDest" select="tokenize(@destination, '\s+')"> </xsl:variable>
                <xsl:for-each select="$tokDest">
                    <a>
                        <xsl:attribute name="href">
                            <xsl:text>#</xsl:text>
                            <xsl:value-of select="."/>
                        </xsl:attribute>
                        <xsl:value-of select="."/>
                    </a>
                    <br/>
                </xsl:for-each>
            </td>
            <!-- Roles -->
            <td>
                <xsl:variable name="tokRoles" select="tokenize(@roles, '\s+')"/>
                <xsl:for-each select="$tokRoles">
                    <xsl:call-template name="display-role">
                        <xsl:with-param name="role">
                            <xsl:value-of select="."/>
                        </xsl:with-param>
                    </xsl:call-template>
                    <br/>
                </xsl:for-each>
            </td>

            <!-- Action and Condition -->
            <td>
                <!-- action -->
                <p style="text-align:left"> A: <span class="ident"><xsl:value-of select="@action"
                /></span>
                </p>
                <!-- condition -->
                <p style="text-align:left"> C: <span class="ident"><xsl:value-of select="@condition"
                /></span>
                </p>
            </td>
            
            <!-- Confirmation yes/no -->
            <td>
                <xsl:choose>
                    <xsl:when test="@require_confirmation">
                        <xsl:value-of select="@require_confirmation"/>
                    </xsl:when>
                    <xsl:otherwise>
                        <xsl:text>false</xsl:text>
                        <br/>
                        <xsl:text>[not declared]</xsl:text>
                    </xsl:otherwise>
                </xsl:choose>
            </td>

        </tr>
    </xsl:template>

    <!-- This template matches grant or deny elements -->
    <xsl:template name="grant-denies">
        <xsl:param name="grant-or-denies" >
            <!-- A grant or deny context element is required -->
        </xsl:param>
        <tr>
            <td><em>Permission</em></td>
            <td><em>Role</em></td>
        </tr>
        <xsl:for-each-group select="$grant-or-denies" group-by="@permission" >
            <xsl:variable name="counter">
                <xsl:value-of select="position()"/>
            </xsl:variable>
            <tr class="s{$counter mod 2}">
                <td>
                    <xsl:call-template name="display-permission">
                        <xsl:with-param name="perm">
                            <xsl:value-of select="current-grouping-key()"/>
                        </xsl:with-param>
                    </xsl:call-template>
                </td>
                <td>
                    <xsl:for-each select="current-group()">
                        <xsl:call-template name="display-role">
                            <xsl:with-param name="role">
                                <xsl:value-of select="@role"/>
                            </xsl:with-param>
                        </xsl:call-template>
                        <xsl:if test="not(position() = last())">
                            <xsl:text> - </xsl:text>
                        </xsl:if>
                    </xsl:for-each>
                </td>
            </tr>    
        </xsl:for-each-group>
        
    </xsl:template>
    <!-- 
        The diagram is generated from a file called e.g. question.dot.png if the xml file is called question.xml 
        so we get the current xml file name, get the part before the .xml and append .dot.png at the end
    -->
    <xsl:template name="diagram">
        <xsl:variable name="diagImage">
            <xsl:value-of select="tokenize(base-uri(),'/')[last()]"/>
        </xsl:variable>
        <a href="./{substring-before($diagImage,'.xml')}.dot.png" target="_blank">[Workflow Diagram]</a>
    </xsl:template>

    <!-- 
        Templates to display permissions and roles 
     -->
    <xsl:template name="display-permission">
       <xsl:param name="perm" />
        <!-- remove the zope. prefix -->
       <xsl:variable name="remove-zope" select="replace($perm,'zope.','')" />
        <!-- remove the bungeni. prefix -->
       <xsl:variable name="remove-bungeni" select="replace($remove-zope,'bungeni.','')" />
       <xsl:value-of select="$remove-bungeni" /> 
    </xsl:template>
    
    <xsl:template name="display-role">
        <xsl:param name="role" />
        <xsl:variable name="remove-bungeni" select="replace($role,'bungeni.','')" />
        <xsl:value-of select="$remove-bungeni" /> 
    </xsl:template>
    

</xsl:stylesheet>
