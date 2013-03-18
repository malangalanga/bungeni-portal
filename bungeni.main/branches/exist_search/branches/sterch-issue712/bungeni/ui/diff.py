import difflib
import string

def isTag(x): return x[0] == "<" and x[-1] == ">"

def textDiff(a, b):
    """Takes in strings a and b and returns a human-readable HTML diff.

    HTML Diff: http://www.aaronsw.com/2002/diff Rough code, badly
    documented. Send me comments and patches.

    Aaron Swartz (me@aaronsw.com).
    __author__ = 'Aaron Swartz <me@aaronsw.com>'
    __copyright__ = '(C) 2003 Aaron Swartz. GNU GPL 2.'
    __version__ = '0.21'
    """

    out = []
    a, b = html2list(a), html2list(b)
    s = difflib.SequenceMatcher(isTag, a, b)
    for e in s.get_opcodes():
        if e[0] == "replace":
            # @@ need to do something more complicated here
            # call textDiff but not for html, but for some html... ugh
            # gonna cop-out for now
            out.append('<del class="diff modified">'+''.join(a[e[1]:e[2]]) + '</del><ins class="diff modified">'+''.join(b[e[3]:e[4]])+"</ins>")
        elif e[0] == "delete":
            out.append('<del class="diff">'+ ''.join(a[e[1]:e[2]]) + "</del>")
        elif e[0] == "insert":
            out.append('<ins class="diff">'+''.join(b[e[3]:e[4]]) + "</ins>")
        elif e[0] == "equal":
            out.append(''.join(b[e[3]:e[4]]))
        else: 
            raise "Um, something's broken. I didn't expect a '" + `e[0]` + "'."
    return ''.join(out)

def html2list(x, b=0):
    mode = 'char'
    cur = ''
    out = []
    for c in x:
        if mode == 'tag':
            if c == '>': 
                if b: cur += ']'
                else: cur += c
                out.append(cur); cur = ''; mode = 'char'
            else: cur += c
        elif mode == 'char':
            if c == '<': 
                out.append(cur)
                if b: cur = '['
                else: cur = c
                mode = 'tag'
            elif c in string.whitespace: out.append(cur+c); cur = ''
            else: cur += c
    out.append(cur)
    return filter(lambda x: x is not '', out)

