import tkinter
from src.url.url import URL
from src.url.view_source import ViewSourceURL

WIDTH, HEIGHT = 800, 600
HSTEP, VSTEP = 13, 18
SCROLL_STEP = 100

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
        text = lex(body, isinstance(url, ViewSourceURL))
        self._display_list = layout(text)
        self._draw()
    
    def _scroll_down(self, _):
        self._scroll += SCROLL_STEP
        self._draw()
    
    def _scroll_up(self, _):
        self._scroll -= SCROLL_STEP
        self._draw()

    def _draw(self):
        self._canvas.delete("all")
        for x, y, c in self._display_list:
            if y > self._scroll + HEIGHT: continue
            if y + VSTEP < self._scroll: continue
            self._canvas.create_text(x, y - self._scroll, text=c)

def layout(text):
    display_list = []
    cursor_x, cursor_y = HSTEP, VSTEP
    for c in text:
        display_list.append((cursor_x, cursor_y, c))
        cursor_x += HSTEP
        if cursor_x >= WIDTH - HSTEP:
            cursor_x = HSTEP
            cursor_y += VSTEP

    return display_list

def lex(body: str, is_view_source: bool = False):
        text = ""
        if is_view_source:
            text += body
        else:
            in_tag = False
            i = 0
            while i < len(body):
                if body[i:i+4] == "&lt;":
                    text += "<"
                    i += 4
                elif body[i:i+4] == "&gt;":
                    text += ">"
                    i += 4
                elif body[i] == "<":
                    in_tag = True
                    i += 1
                elif body[i] == ">":
                    in_tag = False
                    i += 1
                elif not in_tag:
                    text += body[i]
                    i += 1
                else:
                    i += 1
        return text