#!/usr/bin/python2

import markdown
import codecs

with codecs.open("template.html", encoding="utf8") as f:
    template = f.read()
    
with codecs.open("llvm-cheatsheet.md", encoding="utf8") as f:
    source = f.read()

target = markdown.markdown(source,
        output_format="html5",
        )

target_full = template.replace(u"INSERT_CONTENT_HERE", target)

with codecs.open("llvm-cheatsheet.html", "w", encoding="utf8") as f:
    f.write(target_full)
    