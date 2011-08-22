def setup_theme(context):
    """Set up theme.

    We copy the current skin to a new one with the name of 'Bungeni',
    then disable public-facing stylesheets from the CSS registry.
    """
    
    if context.readDataFile('marker.txt') is None:
        return

    portal = context.getSite()

    # disable public stylesheets
    css = portal['portal_css']
    for resource in css.getResources():
        if not resource.getCookedExpression().text.strip():
            resource.setEnabled(False)
    css.cookResources()
    
    # clone skin
    skins = portal['portal_skins']
    skinpath = skins.getSkinPath('Plone Default').split(',')
    skins.manage_skinLayers(add_skin=1, skinname='Bungeni', skinpath=skinpath)
    skins.default_skin = 'Bungeni'
