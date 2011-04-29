<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema" 
    exclude-result-prefixes="xs" version="2.0">
    <xd:doc xmlns:xd="http://www.oxygenxml.com/ns/doc/xsl" scope="stylesheet">
        <xd:desc>
            <xd:p><xd:b>Created on:</xd:b> Jun 14, 2010</xd:p>
            <xd:p><xd:b>Author:</xd:b> Ashok</xd:p>
            <xd:p>UI.xml documentation generator </xd:p>
        </xd:desc>
        <xd:param name="tested-version">r8173</xd:param>
    </xd:doc>
    <xsl:output media-type="text/html" method="xhtml"/>
    
    <xsl:variable name="form-map">
        <form name="AgendaItem" wf="agendaitem"/>
        <form name="AttachedFile" wf="attachedfile"/>
        <form name="Bill" wf="bill"/>
        <form name="Committee" wf="committee"/>
        <form name="EventItem" wf="event"/>
        <form name="Group" wf="group"/>
        <form name="Motion" wf="motion"/>
        <form name="Heading" wf="heading"/>
        <form name="Parliament" wf="parliament"/>
        <form name="Question" wf="question"/>
        <form name="Report" wf="report"/>
        <form name="Sitting" wf="sitting"/>
        <form name="TabledDocument" wf="tableddocument"/>
        <form name="User" wf="user"/>
        
        <!--
        <form name="AgendaItemVersion" wf="agendaitemversion"/>
        <form name="AttachedFileVersion" wf="attachedfileversion"/>
        <form name="Attendance" wf="attendance"/>
        <form name="BillVersion" wf="billversion"/>
        <form name="CommitteeMember" wf="committeemember"/>
        <form name="CommitteeStaff" wf="committeestaff"/>
        <form name="Constituency" wf="constituency"/>
        <form name="ConstituencyDetail" wf="constituencydetail"/>
        <form name="Cosignatory" wf="cosignatory"/>
        <form name="Country" wf="country"/>
        <form name="Government" wf="government"/>
        <form name="GroupAddress" wf="groupaddress"/>
        <form name="GroupGroupItemAssignment" wf="groupgroupitemassignment"/>
        <form name="ItemGroupItemAssignment" wf="itemgroupitemassignment"/>
        <form name="ItemSchedule" wf="itemschedule"/>
        <form name="ItemScheduleDiscussion" wf="itemschedulediscussion"/>
        <form name="MemberRoleTitle" wf="memberroletitle"/>
        <form name="Minister" wf="minister"/>
        <form name="Ministry" wf="ministry"/>
        <form name="MotionVersion" wf="motionversion"/>
        <form name="Mp" wf="mp"/>
        <form name="Office" wf="office"/>
        <form name="OfficeMember" wf="officemember"/>
        <form name="PartyMember" wf="partymember"/>
        <form name="PoliticalGroup" wf="politicalgroup"/>
        <form name="Province" wf="province"/>
        <form name="QuestionVersion" wf="questionversion"/>
        <form name="Region" wf="region"/>
        <form name="Report4Sitting" wf="report4sitting"/>
        <form name="Session" wf="session"/>
        <form name="TabledDocumentVersion" wf="tableddocumentversion"/>
        <form name="UserAddress" wf="useraddress"/>
        <form name="UserDelegation" wf="userdelegation"/>
        -->
        
    </xsl:variable>
    
    
    
   
  
    
    <xsl:template match="ui">
        <html>
            <head>
                <title>
                    Forms
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
                    tr.yellow td {
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
                    }
                
                    div.showhide {
                       border-top:1px solid gray;
                    }
                    
                    div.mode-title {
                      background-color:#ddd;
                    }
                    
                    div.modes-div {
                        border-top:1px solid #ddd;
                    }
                    span.mode-sub-title {
                        color:#2F4F4F;
                    }
                </style>
            </head>
            <body>
                <h1 class="main">
                    Forms
                </h1>
                
                <div id="toc">
                    <xsl:for-each select="descriptor">
                        <xsl:call-template name="descriptor-toc" />
                    </xsl:for-each>
                </div>
                
                <div  id="body">
                    <xsl:for-each select="descriptor">
                        <xsl:call-template name="descriptor" />
                    </xsl:for-each>
                </div>
             
                
            </body>
        </html>
    </xsl:template>
    
    <xsl:template name="descriptor-toc">
        <a href="#{@name}"><xsl:value-of select="@name" /></a>
        <xsl:if test="not(position() = last())">
            <xsl:text>,</xsl:text>
        </xsl:if>
    </xsl:template>
    
    <xsl:template name="descriptor">
        <xsl:variable name="form-name"><xsl:value-of select="@name" /></xsl:variable>
        <a name="{$form-name}"></a>
        
        <h2><xsl:value-of select="$form-name" /></h2>
        <xsl:variable name="wf-name">
            <xsl:value-of select="$form-map/form[@name=$form-name]/@wf"></xsl:value-of>
        </xsl:variable>
        <xsl:if test="not(empty($wf-name))">
            <a href="{$wf-name}.html">[Workflow]</a> 
        </xsl:if>
         <table border="1">
            <tr class="yellow">
                <td>Name</td>
                <td>Modes</td>
                <td>Localizable</td>
                <td>Show/Hide</td>
            </tr>
         
            <xsl:for-each select="field">
                <tr class="m{position() mod 2}">
                    <!-- Name -->
                    <td>
                        <xsl:value-of select="@name" />
                    </td>
                    <!-- modes -->
                    <td>
                        <xsl:call-template name="display_vertically">
                            <xsl:with-param name="space_delimited_string">
                                <xsl:value-of select="@modes" />
                            </xsl:with-param>
                        </xsl:call-template>
                    </td>
                    <!-- Localizable -->
                    <td>
                        <xsl:choose>
                            <xsl:when test="@localizable">
                                <xsl:call-template name="display_vertically">
                                <xsl:with-param name="space_delimited_string">
                                    <xsl:value-of select="@localizable" />
                                </xsl:with-param>
                                </xsl:call-template>
                            </xsl:when>
                            <xsl:otherwise>
                                None
                            </xsl:otherwise>
                        </xsl:choose>
              
                    </td>
                    <!-- Show / Hide -->
                    <td>
                        <!--
                        <hide modes="view listing" roles="bungeni.Anonymous" /> 
                        -->
                        <xsl:apply-templates select="show" />
                        <xsl:apply-templates select="hide" />
                        
                    </td>
                </tr>
                
            </xsl:for-each>
        </table>    
    </xsl:template>
    
    <xsl:template match="show | hide">
        <div class="mode-title">
            <xsl:choose>
                <xsl:when test="local-name() = 'show'">
                    <xsl:text>Show</xsl:text>
                </xsl:when>
                <xsl:otherwise>
                    <xsl:text>Hide</xsl:text>
                </xsl:otherwise>
            </xsl:choose>
        </div>
        <div class="showhide">
           <span class="mode-sub-title">Modes</span>
            <div class="modes-div">
            <xsl:call-template name="display_vertically">
                <xsl:with-param name="space_delimited_string">
                    <xsl:value-of select="@modes" />
                </xsl:with-param>
            </xsl:call-template>
            </div>
            <xsl:if test="@roles">
                <span class="mode-sub-title">Roles</span>
                <div class="modes-div">
                <xsl:call-template name="display_vertically">
                    <xsl:with-param name="space_delimited_string">
                        <xsl:value-of select="@roles" />
                    </xsl:with-param>
                </xsl:call-template>
                 </div>
            </xsl:if>
        </div>
    </xsl:template>
    

    
    <xsl:template name="display_vertically">
        <xsl:param name="space_delimited_string" />
        <xsl:variable name="arr" select="tokenize($space_delimited_string,'\s+')" />
        <xsl:for-each select="$arr">
            <div class="vert">
                <xsl:value-of select="." />
            </div>
         </xsl:for-each>
    </xsl:template>
    
</xsl:stylesheet>
