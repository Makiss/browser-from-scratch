from src.browser.nodes import Text, Element

SELF_CLOSING_TAGS = [
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr",
]
HEAD_TAGS = ["base", "basefont", "bgsound", "noscript",
        "link", "meta", "title", "style", "script"]

class HTMLParser:
    def __init__(self, body):
        self._body = body
        self._unfinished = []

    def parse(self):
        buffer = ""
        in_tag = False
        i = 0
        body = self._body
        
        while i < len(body):
            if body[i:i+4] == "&lt;":
                buffer += "<"
                i += 4
            elif body[i:i+4] == "&gt;":
                buffer += ">"
                i += 4
            elif body[i] == "<":
                in_tag = True
                if buffer: self._add_text(buffer)
                buffer = ""
                i += 1
            elif body[i] == ">":
                in_tag = False
                self._add_tag(buffer)
                buffer = ""
                i += 1
            else:
                buffer += body[i]
                i += 1
        if not in_tag and buffer:
            self._add_text(buffer)

        return self._finish()
    
    def _add_text(self, text):
        if text.isspace(): return
        self._implicit_tags(None)
        parent = self._unfinished[-1]
        node = Text(text, parent)
        parent.children.append(node)
    
    def _add_tag(self, tag):
        tag, attributes = self._get_attributes(tag)
        if tag.startswith("!"): return
        self._implicit_tags(tag)
        if tag.startswith("/"):
            if len(self._unfinished) == 1: return
            node = self._unfinished.pop()
            parent = self._unfinished[-1]
            parent.children.append(node)
        elif tag in SELF_CLOSING_TAGS:
            parent = self._unfinished[-1]
            node = Element(tag, attributes, parent)
            parent.children.append(node)
        else:
            parent = self._unfinished[-1] if self._unfinished else None
            node = Element(tag, attributes, parent)
            self._unfinished.append(node)
    
    def _get_attributes(self, text):
        parts = text.split()
        tag = parts[0].casefold()
        attributes = {}
        for attrpair in parts[1:]:
            if "=" in attrpair:
                key, value = attrpair.split("=", 1)
                if len(value) > 2 and value[0] in ["", "\""]:
                    value = value[1:-1]
                attributes[key.casefold()] = value
            else:
                attributes[attrpair.casefold()] = ""

        return tag, attributes

    def _finish(self):
        if not self._unfinished:
            self._implicit_tags(None)
        while len(self._unfinished) > 1:
            node = self._unfinished.pop()
            parent = self._unfinished[-1]
            parent.children.append(node)

        return self._unfinished.pop()
    
    def _implicit_tags(self, tag):
        while True:
            open_tags = [node.tag for node in self._unfinished]
            if open_tags == [] and tag != "html":
                self._add_tag("html")
            elif open_tags == ["html"] \
                  and tag not in ["head", "body", "/html"]:
                if tag in HEAD_TAGS:
                    self._add_tag("head")
                else:
                    self._add_tag("body")
            elif open_tags == ["html", "head"] and \
                tag not in ["/head"] + HEAD_TAGS:
                self._add_tag("/head")
            else:
                break
    
def print_tree(node, indent=0):
    print(" " * indent, node)
    for child in node.children:
        print_tree(child, indent + 2)
