import httplib
import urllib2
from pyquery import PyQuery as pq
from urlparse import urlsplit, urlparse

def get_theme_host(log):
    theme_host = urlsplit(log.theme_url)[1].split("/themes")[0]
    return theme_host
    
def check_url(url):
    """
    Get the header for a given url and check response code.
    """
    parsed_url = urlparse(url)
    http_instance = httplib.HTTP(parsed_url[1])
    http_instance.putrequest('HEAD', parsed_url[2])
    http_instance.endheaders()
    return http_instance.getreply()[0] == httplib.OK

def add_section_links(content, theme, resource_fetcher, log):
    """
    Add top level class links and logos for the different sections
    (workspace and portal).
    """
    host_url = urlsplit(log.theme_url)
    if theme('#portal-personaltools').html() == None:
        theme('body').addClass('template-portal')
    else:
        if "logout" in theme('#portal-personaltools').html():
            theme('body').addClass('template-workspace')
        else:
            theme('body').addClass('template-portal')

def update_links(content, theme, resource_fetcher, log):
    """
    Use absolute links to the members image and political groups logo.
    Change home page tab name if necessary
    """
    
    if content('#region-content').html() != None:
        link_value  = content('#region-content').html()
        to_replace = 'file-image/image'
        to_replace = ['file-image/image', 'file-image/logo_data']
        
        for image in to_replace:
            if image in link_value:
                link_id= content('#portal-breadcrumbs a:last-child')
                link_id = str(link_id).split('href="')
                link_id = str(link_id[1]).split('">')[0]
                link_node = content('#region-content')
                new_value = link_value.replace('./'+image, 
                                               str(link_id)+'/'+image)
                link_node.replaceWith('<div id="region-content" \
                class="documentContent">' + new_value + '</div>')

    if theme('#portal-globalnav').html() != None:
	tab_content = theme('#portal-globalnav').html()
        tab_content = tab_content.replace("home", "National Assembly")
        tab_node = theme('#portal-globalnav')
        tab_node.replaceWith('<div id="portal-globalnav" \
                ">' + tab_content + '</div>')                
       
def add_member_workspace_links(content, theme, resource_fetcher, log):
    """
    Add a member's 'private space' and 'web space' links to the workspace
    second level menu items (if they exist).
    Add link to group digital repositories - all members can view.
    """
    if len(content("#portal-personaltools span")) == 0:
        link_items = theme("#portal-personaltools span")
    else:
        link_items = content("#portal-personaltools span")
    member_id = link_items.pop(0).text
    if len(content("#portal-personaltools span")) == 0:
        theme('ul.level1').append(
            "<li class='navigation' id='private'><a href='/plone/membership/" + member_id +
            "/private_space/folder_contents" + "'>private space</a></li>")
    else:
        content('#portal-personaltools').append(
            "<li class='navigation' id='private'><a href='/plone/membership/" + member_id +
            "/private_space/folder_contents" + "'>private space</a></li>")

    
    host_url = urlsplit(log.theme_url)
    theme_host = get_theme_host(log).split(":")[0]
    test_url = "http://" + theme_host + ":8082" + "/plone/membership/" + \
                member_id + "/web_space"
                
    if check_url(test_url):
        if len(content("#portal-personaltools span")) == 0:
            theme('ul.level1').append("<li class='navigation' id='public'>\
            <a href='/plone/membership/" + member_id + \
            "/web_space/folder_contents" + "'>web space</a></li>")
        else:
            content('#portal-personaltools').append("<li class='navigation' id='public'>\
            <a href='/plone/membership/" + member_id + \
            "/web_space/folder_contents" + "'>web space</a></li>")

    if len(content("#portal-personaltools span")) == 0:
        theme('ul.level1').append("<li class='navigation'>\
        <a href='/plone/groups/library-view'>digital library</a></li>")
    else:
        content('#portal-personaltools').append("<li class='navigation'>\
        <a href='/plone/groups/library-view'>digital library</a></li>")


def redirect_group_workspace_links(request, response, response_headers, log):
    """
    Redirect bungeni group workspace view to corresponding plone workspace view.
    If the plone workspace does not exist, default bungeni view will be used.
    """ 
    link_url = request.url
    # !+CUSTOM(mn, jan-2013) move group variables to bungeni_custom 
    if "pol_group" or "committee" in link_url:
        group_url = link_url.replace("workspace/groups/my-groups","plone/groups") 
        group_url = group_url.replace("-",".") + "web_space"
        if check_url(group_url):
            response._status__set("302 Found") 
            response.location = group_url 
    
def add_member_public_links(content, theme, resource_fetcher, log):
    """
    Add a member's 'web pages' links to the public view.
    """
    member_id = content(".MemberOfParliament .User .content-right-column")\
                .pop(4).text_content()
    link_value = "/plone/membership/" +  member_id.strip() + "/web_space"

def add_exist_content(content, theme, resource_fetcher, log):
    """
    Add content from exist to frontpage placeholders
    """
    theme_host = get_theme_host(log)
    theme_url = "http://" + theme_host
    if len(theme_host.split(":")) > 1:
        theme_port = ":" + theme_host.split(":")[1]

    exist_port = ":8080" 
    plone_port = ":8082" 
    exist_url = theme_url.split(":")[0] + ":" + theme_url.split(":")[1] + \
                exist_port + "/exist/"
    plone_url = theme_url.split(":")[0] + ":" + theme_url.split(":")[1] + \
                plone_port

    link_val = exist_url +"higher_house/whatson?tab=sittings&showing=old"
    if check_url(link_val):
        eurl = pq(link_val)
        econtent = eurl(".whatson-wrapper .left").html()
        theme(".portlet-static-whats-on-senate .portletItem").append(pq(econtent))
        content("#main-wrapper").append(pq(econtent))

    link_val = exist_url +"lower_house/whatson?tab=sittings&showing=old"
    if check_url(link_val):
        eurl = pq(link_val)
        econtent = eurl(".whatson-wrapper .left").html()
        theme(".portlet-static-whats-on-house-of-representatives .portletItem").append(pq(econtent))
        content("#main-wrapper").append(pq(econtent))
  
def add_space_tab(content, theme, resource_fetcher, log, space_type):
    """
    Add the member's or groups web space as a tab
    """
    theme_host = get_theme_host(log)
    theme_url = "http://" + theme_host
    if len(theme_host.split(":")) > 1:
        theme_port = ":" + theme_host.split(":")[1]
        
    # !+HACK(mn, may-2011) - the plone port is hardcoded. 
    plone_port = ":8082"    
    plone_url = theme_url.split(":")[0] + ":" + theme_url.split(":")[1] + \
                plone_port
    if space_type == "member":
        item_id = content('#portal-breadcrumbs a:last-child')
        space_id = item_id.text().split( )
        link_val = plone_url + "/plone/membership/" + space_id[1] + "." + \
                    space_id[2] +"/web_space"        
    else:
        item_id = content('#portal-breadcrumbs a:last-child').attr("href")
        space_id =  item_id.split("-")[-1]
        if space_type == "committee":
            link_val = plone_url + "/plone/groups/group.committee." + \
                        space_id + "web_space"            
        else:
            link_val = plone_url + "/plone/groups/group.political-group." + \
                        space_id + "web_space"  

def replace_login_link(content, theme, resource_fetcher, log):
    """Login and logout will be via plone to facilitate creation of
     member  and group spaces.
    """
    login_link = theme("a[href$='/login']")
    if len(login_link) > 0:
        if login_link.attr("href"):
            login_value = pq(login_link).attr("href").replace(
                            "login", "plone/login")
            pq(login_link).attr("href", login_value)
            pq(login_link).attr("class", "link-overlay")
    
    logout_link = theme("a[href$='/logout']")
    if len(logout_link) > 0:
        if "plone/logout" not in logout_link.attr("href"):
            logout_value = pq(logout_link).attr("href").replace(
                            "logout", "plone/logout")
            pq(logout_link).attr("href", logout_value)


def add_menu_items(content, theme, resource_fetcher, log):
    """
    Add menu items
    """
    newlist = theme("div#portal-globalnav").clone()("li")

    theme(".row_1 .three-columns-equal .block_1").append(
        "<h1 class='documentFirstHeading'>Menu</h1>")    
    theme(".row_1 .three-columns-equal .block_1").append("<ul></ul>")    
    for item in newlist:
        pq(item).removeClass("plain")
        theme(".row_1 .three-columns-equal .block_1 ul").append(item)
        for list_item in theme("div#portal-column-one li"):
            check_val = urlsplit(pq(list_item.getchildren()).attr("href"))[2]
            if "plone" in pq(list_item.getchildren()).attr("href"):
                check_val = check_val.split("/")[2]
            else:
                check_val = check_val.split("/")[1]                
                
            if check_val in pq(item).children().attr("href"):
                pq(list_item).addClass("2ndlevel")
                theme(".row_1 .three-columns-equal .block_1 ul").append(
                    list_item)

def reposition_contentActions(content, theme, resource_fetcher, log):
    """
    Move '.contentActions below '.documentDescription'
    !+ Some pages have 2 document descriptions whilst others have none,
    hence the explicit check. Should be revised immediately each document has 
    one top level description.
    """
    element_length = len(theme(".documentDescription"))
    if "site-plone" not in content("html").html():
        if element_length == 1:
            ca = theme(".contentActions")
            theme.remove(".contentActions")            
            ca.insertAfter(theme(".documentDescription")) 
        elif element_length == 2:
            ca = theme(".contentActions")
            theme.remove(".contentActions")            
            ca.insertAfter(theme(".documentDescription:nth-child(2)"))             
 

def enable_text_editor(content, theme, resource_fetcher, log):
    """
    Disable rich text editor in favor of plain text editor for Selenium.
    """
    scripts = theme('#alchemist-form script')
    for script in scripts:
        if script.text.__contains__('YAHOO.widget.Editor'):
            script.text=""
            script.drop_tag()                    
            
def modify_proxy_response(request, response,
                          orig_base, proxied_base, proxied_url, log):
    """
    Match proxy response content links to request host url.
    """      
    if "HTTP_HOST" in request.environ.keys():
        host = request.environ["HTTP_HOST"]
    else:
        host = request.environ["deliverance.base_url"]
    resp = response.request.environ["HTTP_HOST"]                          
    if host != resp and resp in response.body:
        response.body = response.body.replace(resp, host)              
        return response
