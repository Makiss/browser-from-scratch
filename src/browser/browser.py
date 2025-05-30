import tkinter
import tkinter.font
from src.url.url import URL
from src.browser.htmlParser import HTMLParser
from src.browser.layout import DocumentLayout
from src.browser.layout import paint_tree

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
        self._document = DocumentLayout(self._nodes)
        self._document.layout()
        self._display_list = []
        paint_tree(self._document, self._display_list)
        self._draw()

    def loadSource(self, url: URL):
        body = url.request()
        print(body)
    
    def _scroll_down(self, _):
        max_y = max(self._document.height + 2 * VSTEP - HEIGHT, 0)
        self._scroll = min(self._scroll + SCROLL_STEP, max_y)
        self._draw()
    
    def _scroll_up(self, _):
        min_y = 0
        self._scroll = max(self._scroll - SCROLL_STEP, min_y)
        self._draw()

    def _draw(self):
        self._canvas.delete("all")
        for cmd in self._display_list:
            if cmd.top > self._scroll + HEIGHT: continue
            if cmd.bottom < self._scroll: continue
            cmd.execute(self._scroll, self._canvas)
       