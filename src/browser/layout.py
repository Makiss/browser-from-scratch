import tkinter
import tkinter.font
from typing import Union
from src.browser.nodes import Text, Element
from src.browser.constants import HSTEP, VSTEP, WIDTH

FONTS = {}

class Layout:
    def __init__(self, tree):
        self.display_list = []
        self._cursor_x = HSTEP
        self._cursor_y = VSTEP
        self._weight = "normal"
        self._style = "roman"
        self._size = 12
        self._line = []
        self._recurse(tree)
        self._flush()
    
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
        if self._cursor_x + width > WIDTH - HSTEP:
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
        for x, word, font in self._line:
            y = baseline - font.metrics("ascent")
            self.display_list.append((x, y, word, font))
        max_descent = max([metric["descent"] for metric in metrics])
        self._cursor_y = baseline + 1.25 * max_descent
        self._cursor_x = HSTEP
        self._line = []

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