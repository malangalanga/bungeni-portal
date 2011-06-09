def setup_theme(context):
    """Set up theme.

    We copy the current skin to a new one with the name of 'Bungeni CMS theme'.
    """
    
    if context.readDataFile('marker.txt') is None:
        return

    portal = context.getSite()
    
    # clone skin
    skins = portal['portal_skins']
    skinpath = skins.getSkinPath('Plone Classic Theme').split(',')
    skins.manage_skinLayers(add_skin=1, 
        skinname='Bungeni CMS theme', skinpath=skinpath)
    skins.default_skin = 'Bungeni CMS theme'
