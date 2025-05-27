import tkinter
import tkinter.font
from src.url.url import URL
from src.url.view_source import ViewSourceURL
from dataclasses import dataclass

WIDTH, HEIGHT = 800, 600
HSTEP, VSTEP = 13, 18
SCROLL_STEP = 100
FONTS = {}

class Browser:
    def __init__(self):
        self._window = tkinter.Tk()
        self._canvas = tkinter.Canvas(self._window, width=WIDTH, height=HEIGHT)
        self._canvas.pack()
        self._scroll = 0
        self._canvas.bind("<Down>", self._scroll_down)
        self._canvas.bind("<Up>", self._scroll_up)
        self._canvas.focus_set()

    def load(self, url: URL):
        body = url.request()
        tokens = lex(body)
        self._display_list = Layout(tokens).display_list
        self._draw()

    def loadSource(self, url: URL):
        body = url.request()
        print(body)
    
    def _scroll_down(self, _):
        self._scroll += SCROLL_STEP
        self._draw()
    
    def _scroll_up(self, _):
        self._scroll -= SCROLL_STEP
        self._draw()

    def _draw(self):
        self._canvas.delete("all")
        for x, y, word, font in self._display_list:
            if y > self._scroll + HEIGHT: continue
            if y + VSTEP < self._scroll: continue
            self._canvas.create_text(x, y - self._scroll, text=word, anchor="nw", font=font)
class Layout:
    def __init__(self, tokens):
        self.display_list = []
        self._cursor_x = HSTEP
        self._cursor_y = VSTEP
        self._weight = "normal"
        self._style = "roman"
        self._size = 12
        self._line = []
        for token in tokens:
            self._token(token)
        self._flush()
    
    def _token(self, tokenItem):
        if isinstance(tokenItem, Text):
            for word in tokenItem.text.split():
                self._word(word)
        else:
            self._tag(tokenItem.tag)

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
    
    def _tag(self, tag):
        if tag == "i" or tag == "em":
            self._style = "italic"
        elif tag == "/i" or tag == "/em":
            self._style = "roman"
        elif tag == "b" or tag == "strong":
            self._weight = "bold"
        elif tag == "/b" or tag == "/strong":
            self._weight = "normal"
        elif tag == "small":
            self._size -= 2
        elif tag == "/small":
            self._size += 2
        elif tag == "big":
            self._size += 4
        elif tag == "/big":
            self._size -= 4
        elif tag == "br":
            self._flush()
        elif tag == "/p":
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

def lex(body: str):
    output = []
    buffer = ""
    in_tag = False
    i = 0
    
    while i < len(body):
        if body[i:i+4] == "&lt;":
            buffer += "<"
            i += 4
        elif body[i:i+4] == "&gt;":
            buffer += ">"
            i += 4
        elif body[i] == "<":
            in_tag = True
            if buffer: output.append(Text(buffer))
            buffer = ""
            i += 1
        elif body[i] == ">":
            in_tag = False
            output.append(Tag(buffer))
            buffer = ""
            i += 1
        else:
            buffer += body[i]
            i += 1
    if not in_tag and buffer:
        output.append(Text(buffer))

    return output

@dataclass
class Tag:
    tag: str

@dataclass
class Text:
    text: str