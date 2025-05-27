from src.url.url import URL
from src.url.view_source import ViewSourceURL
from src.browser.browser import Browser
import tkinter

if __name__ == "__main__":
    import sys
    url = sys.argv[1]
    if url.startswith("view-source:"):
        Browser().loadSource(ViewSourceURL(url))
    else:
        Browser().load(URL(sys.argv[1]))
        tkinter.mainloop()