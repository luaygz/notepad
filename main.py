import tkinter as tk
import tkinter.ttk as ttk
from tkinter import Text, Menu
from tkinter.ttk import Label

from utils import do_popup, close_popup, select_all, delete_selection, paste

class ScrollableText(Text):
    def __init__(self, master=None, **kwargs):
        self.frame = ttk.Frame(master)
        self.x_scroll_bar = ttk.Scrollbar(self.frame, orient=tk.HORIZONTAL)
        self.x_scroll_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.y_scroll_bar = ttk.Scrollbar(self.frame)
        self.y_scroll_bar.pack(side=tk.RIGHT, fill=tk.Y)

        Text.__init__(self, self.frame, wrap=tk.NONE,
                      xscrollcommand=self.x_scroll_bar.set,
                      yscrollcommand=self.y_scroll_bar.set,
                      **kwargs)
        self.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.x_scroll_bar.config(command=self.xview)
        self.y_scroll_bar.config(command=self.yview)

class StatusBar(Label):
    def __init__(self, master=None, **kwargs):
        self.word_count = tk.StringVar()
        self.word_count.set("")
        Label.__init__(self, master, textvariable=self.word_count, **kwargs)
        self.update("")

    def update(self, text):
        wc = len(text.split())
        self.word_count.set(f"Word Count -> {wc}")

class PopupMenu(Menu):
    def __init__(self, master=None, **kwargs):
        Menu.__init__(self, master, tearoff=0)
        self.add_command(label="Select All", command=lambda: select_all(master))
        self.add_command(label="Cut", command=lambda: master.event_generate("<<Cut>>"))
        self.add_command(label="Copy", command=lambda: master.event_generate("<<Copy>>"))
        self.add_command(label="Paste", command=lambda: paste(master))
        self.add_command(label="Save")


window = tk.Tk()
# style = ttk.Style()
window.title("Notepad")
window.geometry(f"{window.winfo_screenwidth()}x{window.winfo_screenheight()}")
window.grid_columnconfigure(1, weight=1)
window.grid_rowconfigure(0, weight=1)

menuBar = tk.Menu(window)
window.config(menu=menuBar)
fileMenu = tk.Menu(menuBar, tearoff=0)
editMenu = tk.Menu(menuBar, tearoff=0)
viewMenu = tk.Menu(menuBar, tearoff=0)
helpMenu = tk.Menu(menuBar, tearoff=0)

text_area = ScrollableText(window, undo=True, autoseparators=True, maxundo=-1)
text_area.frame.grid(row=0, column=1, sticky="NSEW")
text_area.focus()

line_numbers = tk.Canvas(window, width="30", height="500")
line_numbers.grid(row=0, column=0, sticky='NS', pady=1, rowspan=3)

status_bar = StatusBar(window)
status_bar.grid(row=2, column=1, columnspan=2, sticky="EW")

text_area.bind("<space>", lambda event: text_area.edit_separator())
text_area.bind("<Return>", lambda event: text_area.edit_separator())
text_area.bind("<KeyRelease>", lambda event: status_bar.update(text_area.get('1.0', tk.END)))
text_area.bind("<<Paste>>", lambda event: delete_selection(text_area))
text_area.bind("<Control-Key-a>", lambda event: select_all(text_area))
text_area.bind("<Control-Key-A>", lambda event: select_all(text_area))

popup_menu = PopupMenu(text_area)
text_area.bind("<Button-3>", lambda event: do_popup(event.x_root, event.y_root, popup_menu))
popup_menu.bind("<FocusOut>", lambda event: close_popup(popup_menu))

window.mainloop()