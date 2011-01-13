def setupVarious(context):
    if context.readDataFile("products.workspaces.txt") is None:
        return

