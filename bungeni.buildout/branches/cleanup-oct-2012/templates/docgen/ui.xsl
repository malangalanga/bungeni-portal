<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema" exclude-result-prefixes="xs" version="2.0">
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
                <title> Forms </title>
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
                        background: #ECE5B6;
                    }
                    
                    tr.gray td {
                       border-top: 1px dotted #FB7A31;
                        border-bottom: 1px dotted #FB7A31;
                        background: #FDEEF4;
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
                    }</style>
            </head>
            <body>
                <h1 class="main"> Forms </h1>

                <div id="toc">
                    <xsl:for-each select="descriptor">
                        <xsl:variable name="form-name"><xsl:value-of select="@name" /></xsl:variable>
                        <xsl:if test="$form-map/form[@name=$form-name]">                             
                            <xsl:call-template name="descriptor-toc"/>
                        </xsl:if>
                    </xsl:for-each>
                </div>

                <div id="body">
                    <xsl:for-each select="descriptor">
                        <xsl:variable name="form-name"><xsl:value-of select="@name" /></xsl:variable>
                        <xsl:if test="$form-map/form[@name=$form-name]">                             
                            <xsl:call-template name="descriptor"/>
                        </xsl:if>
                    </xsl:for-each>
                </div>


            </body>
        </html>
    </xsl:template>

    <xsl:template name="descriptor-toc">
        <a href="#{@name}">
            <xsl:value-of select="@name"/>
        </a>
        <xsl:if test="not(position() = last())">
            <xsl:text>,</xsl:text>
        </xsl:if>
    </xsl:template>

    <xsl:template name="descriptor">
        <xsl:variable name="form-name">
            <xsl:value-of select="@name"/>
        </xsl:variable>
        <a name="{$form-name}"/>

        <h2>
            <xsl:value-of select="$form-name"/>
        </h2>
        <xsl:variable name="wf-name">
            <xsl:value-of select="$form-map/form[@name=$form-name]/@wf"/>
        </xsl:variable>
        <xsl:if test="not(empty($wf-name)) and (string-length($wf-name) gt 0)">
            <a href="{$wf-name}.html" >[Workflow]</a>
        </xsl:if>
        <table border="1">
            <tr class="yellow">
                <td>Name</td>
                <td>Field Info</td>
            </tr>

            <xsl:for-each select="field">
                <tr class="m{position() mod 2}">
                    <!-- Name -->
                    <td>
                        <xsl:value-of select="@name"/>
                    </td>

                    <xsl:variable name="vmodes" select="tokenize(@localizable,'\s+')"/>
                    <xsl:variable name="vshow" select="./show"/>
                    <xsl:variable name="vshow-modes">
                        <xsl:value-of select="$vshow/@modes"/>
                    </xsl:variable>
                    <xsl:variable name="vhide" select="./hide"/>
                    <xsl:variable name="vhide-modes">
                        <xsl:value-of select="$vhide/@modes"/>
                    </xsl:variable>
                    
                    <!-- modes -->
                    <td>
                        <xsl:choose>
                            <xsl:when test="not(empty($vmodes))">
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
                            </xsl:when>
                            <xsl:otherwise>
                                Not Customizable
                            </xsl:otherwise>
                        </xsl:choose>
                    </td>
                </tr>

            </xsl:for-each>
        </table>
    </xsl:template>

   
</xsl:stylesheet>
