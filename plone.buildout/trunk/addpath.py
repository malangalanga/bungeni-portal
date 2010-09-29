import os

FILES = ('bin/paster',)
ZOPE_PATH = os.path.abspath('parts/zope2/lib/python')

def main(options, buildout):
    for filename in FILES:
        lines = open(filename, 'r').readlines()
        file = open(filename, 'w')
        for line in lines:
            file.write(line)
            if line.startswith('sys.path'):
                file.write("  '%s',\n" % ZOPE_PATH)
        file.close()

    print "zope path added to %s" % ', '.join(FILES)
