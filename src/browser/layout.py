import tkinter
import tkinter.font
from typing import Union
from src.browser.nodes import Text, Element
from src.browser.constants import HSTEP, VSTEP, WIDTH

FONTS = {}

BLOCK_ELEMENTS = [
    "html", "body", "article", "section", "nav", "aside",
    "h1", "h2", "h3", "h4", "h5", "h6", "hgroup", "header",
    "footer", "address", "p", "hr", "pre", "blockquote",
    "ol", "ul", "menu", "li", "dl", "dt", "dd", "figure",
    "figcaption", "main", "div", "table", "form", "fieldset",
    "legend", "details", "summary"
]
class BlockLayout:
    def __init__(self, node, parent, previous):
        self.node = node
        self.parent = parent
        self.previous = previous
        self.children = []
        self.x = None
        self.y = None
        self.width = None
        self.height = None
        self.display_list = []
    
    def _recurse(self, tree: Union[Text, Element]):
        if isinstance(tree, Text):
            for word in tree.text.split():
                self._word(word)
        else:
            self._open_tag(tree.tag)
            for child in tree.children:
                self._recurse(child)
            self._close_tag(tree.tag)

    def _word(self, word):
        font = get_font(
            self._size,
            self._weight,
            self._style
        )
        width = font.measure(word)
        if self._cursor_x + width > self.width:
            self._flush()
        self._line.append((self._cursor_x, word, font))
        self._cursor_x += width + font.measure(" ")

    def _open_tag(self, tag):
        if tag == "i" or tag == "em":
            self._style = "italic"
        elif tag == "b" or tag == "strong":
            self._weight = "bold"
        elif tag == "small":
            self._size -= 2
        elif tag == "big":
            self._size += 4
        elif tag == "br":
            self._flush()
            
    def _close_tag(self, tag):
        if tag == "i" or tag == "em":
            self._style = "roman"
        elif tag == "b" or tag == "strong":
            self._weight = "normal"
        elif tag == "small":
            self._size += 2
        elif tag == "big":
            self._size -= 4
        elif tag == "p":
            self._flush()
            self._cursor_y += VSTEP
    
    def _flush(self):
        if not self._line: return
        metrics = [font.metrics() for _, __, font in self._line]
        max_ascent =  max([metric["ascent"] for metric in metrics])
        baseline = self._cursor_y + 1.25 * max_ascent
        for rel_x, word, font in self._line:
            x = self.x + rel_x
            y = self.y + baseline - font.metrics("ascent")
            self.display_list.append((x, y, word, font))
        max_descent = max([metric["descent"] for metric in metrics])
        self._cursor_y = baseline + 1.25 * max_descent
        self._cursor_x = 0
        self._line = []

    def _layout_intermediate(self):
        previous = None
        for child in self.node.children:
            next = BlockLayout(child, self, previous)
            self.children.append(next)
            previous = next

    def _layout_mode(self):
        if isinstance(self.node, Text):
            return "inline"
        elif any([isinstance(child, Element) and \
                  child.tag in BLOCK_ELEMENTS
                  for child in self.node.children]):
            return "block"
        elif self.node.children:
            return "inline"
        else:
            return "block"

    def layout(self):
        self.x = self.parent.x
        self.width = self.parent.width

        if self.previous:
            self.y = self.previous.y + self.previous.height
        else:
            self.y = self.parent.y

        mode = self._layout_mode()
        if mode == "block":
            previous = None
            for child in self.node.children:
                next = BlockLayout(child, self, previous)
                self.children.append(next)
                previous = next
        else:
            self._cursor_x = 0
            self._cursor_y = 0
            self._weight = "normal"
            self._style = "roman"
            self._size = 12

            self._line = []
            self._recurse(self.node)
            self._flush()

        for child in self.children:
            child.layout()

        if mode == "block":
            self.height = sum([child.height for child in self.children])
        else:
            self.height = self._cursor_y
    
    def paint(self):
        cmds = []

        if isinstance(self.node, Element) and self.node.tag == "pre":
            x2, y2 = self.x + self.width, self.y + self.height
            rect = DrawRect(self.x, self.y, x2, y2, "gray")
            cmds.append(rect)
        if self._layout_mode() == "inline":
            for x, y, word, font in self.display_list:
                cmds.append(DrawText(x, y, word, font))

        return cmds

def paint_tree(layout_object, display_list):
    display_list.extend(layout_object.paint())

    for child in layout_object.children:
        paint_tree(child, display_list)


def get_font(size, weight, style):
    key = (size, weight, style)
    if key not in FONTS:
        font = tkinter.font.Font(
            size=size,
            weight=weight,
            slant=style
        )
        label = tkinter.Label(font=font)
        FONTS[key] = (font, label)
    
    return FONTS[key][0]

class DocumentLayout:
    def __init__(self, node):
        self.node = node
        self.parent = None
        self.children = []
        self.x = None
        self.y = None
        self.width = None
        self.height = None

    def layout(self):
        child = BlockLayout(self.node, self, None)
        self.children.append(child)
        self.width = WIDTH - 2 * HSTEP
        self.x = HSTEP
        self.y = VSTEP
        child.layout()
        self.height = child.height
    
    def paint(self):
        return []
    
class DrawText:
    def __init__(self, x1, y1, text, font):
        self.top = y1
        self.left = x1
        self.text = text
        self.font = font
        self.bottom = y1 + font.metrics("linespace")
    
    def execute(self, scroll, canvas):
        canvas.create_text(
            self.left, self.top - scroll,
            text=self.text,
            font=self.font,
            anchor="nw"
        )

class DrawRect:
    def __init__(self, x1, y1, x2, y2, color):
        self.top = y1
        self.left = x1
        self.bottom = y2
        self.right = x2
        self.color = color
    
    def execute(self, scroll, canvas):
        canvas.create_rectangle(
            self.left, self.top - scroll,
            self.right, self.bottom - scroll,
            width=0,
            fill=self.color
        )
        