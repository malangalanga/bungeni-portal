PROJECTNAME = "bungenicms.workspaces"
PUBLIC_FOLDER_ENTRY_NAME = "PublicFolder"
PRIVATE_FOLDER_ENTRY_NAME = "PrivateFolder"

ADD_PERMISSIONS = {
    "PrivateFolder"    : "bungenicms.workspaces: Add PrivateFolder",
    "PublicFolder"  : "bungenicms.workspaces: Add PublicFolder",
}

GLOBALS = globals()

MEMBER_SPACE_CONTENT = [{"id": "my_blog", "title": "Blog", 
                        "type":"Folder", "addable_types":["Blog Entry"]},
                        {"id": "my_political_interests", 
                        "type":"Folder", "title":"My Political Interests",
                        "addable_types":["Document","File", "Collection"]},
                        {"id": "my_speeches", "title": "My Speeches",
                        "type":"Folder", "addable_types":["Document","File", "Link"]}
                      ]
GROUP_SPACE_CONTENT = [{"id": "members_blog", "title": "Members Blog", 
                        "type":"Folder", "addable_types":["Blog Entry"]},
                        {"id": "thematic_folders", "title": "Thematic Folders", 
                        "type":"Folder", 
                        "addable_types":["Document","File", "Collection"]},
                        {"id": "events", "title": "Events", 
                        "type":"Folder", "addable_types":["Event"]},
                        {"id": "repository", "title": "Virtual Library", 
                        "type":"RepositoryCollection", 
                        "addable_types":["RepositoryCollection", "RepositoryItem"]},
                        {"id": "forums", "title": "Forums", 
                        "type":"Folder", 
                        "addable_types":["Ploneboard","PlonePopoll"]},                           
                        ]
                        
ROLES_FOR_WEB_SPACE = ["bungeni.MemberAssembly","bungeni.MemberSenate"]                                                

