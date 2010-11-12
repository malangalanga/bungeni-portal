def setupVarious(context):
    if context.readDataFile(products.groupworkspaces.txt) is None:
        return
