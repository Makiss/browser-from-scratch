import tkinter
import tkinter.font
from src.url.url import URL
from src.browser.htmlParser import HTMLParser
from src.browser.layout import Layout

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
        self._nodes = HTMLParser(body).parse()
        self._display_list = Layout(self._nodes).display_list
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
       