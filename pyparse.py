import cgi
from pyparsing import makeHTMLTags, SkipTo

raw = """<body><div class="shoveler" id="purchaseShvl">
<p>Customers who bought this item also bought</p>
<div class="foo">
    <span class="bar">Shovel cozy</span>
    <span class="bar">Shovel rack</span>
</div>
</div></body>"""

def foo(parseResult):
    parts = []
    for token in parseResult:
        st = '<div id="%s" class="%s">' % \
             (cgi.escape(getattr(token, 'id')),
             cgi.escape(getattr(token, 'class')))
        parts.append(st + token.body + token.endDiv)
    return '\n'.join(parts)

start, end = makeHTMLTags('div')
anchor = start + SkipTo(end).setResultsName('body') + end
res = anchor.searchString(raw)
print foo(res)
