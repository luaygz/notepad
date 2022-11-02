import tkinter as tk
import tkinter.ttk as ttk
from tkinter import Text, Menu
from tkinter.ttk import Label
from tkinter import Tk
from ttkthemes import ThemedTk
from tkinter.font import Font

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

        self.tag_configure("BOLD", font=Font(family="Helvetica", size=14, weight="bold"))

    def highlight_pattern(self, pattern, tag, start="1.0", end="end",
                          regexp=False):
        '''Apply the given tag to all text that matches the given pattern

        If 'regexp' is set to True, pattern will be treated as a regular
        expression according to Tcl's regular expression syntax.
        '''

        start = self.index(start)
        end = self.index(end)
        self.mark_set("matchStart", start)
        self.mark_set("matchEnd", start)
        self.mark_set("searchLimit", end)

        count = tk.IntVar()
        while True:
            index = self.search(pattern, "matchEnd", "searchLimit",
                                count=count, regexp=regexp)
            if index == "": break
            if count.get() == 0: break # degenerate pattern which matches zero-length strings
            self.mark_set("matchStart", index)
            self.mark_set("matchEnd", "%s+%sc" % (index, count.get()))
            self.tag_add(tag, "matchStart", "matchEnd")

class StatusBar(Label):
    def __init__(self, master=None, **kwargs):
        self.word_count = tk.StringVar()
        self.word_count.set("")
        Label.__init__(self, master, textvariable=self.word_count, **kwargs)

    def update(self, wc):
        self.word_count.set(f"Word Count -> {wc}")

class PopupMenu(Menu):
    def __init__(self, master=None, **kwargs):
        Menu.__init__(self, master, tearoff=0)
        self.add_command(label="Select All", command=lambda: select_all(master))
        self.add_command(label="Cut", command=lambda: master.event_generate("<<Cut>>"))
        self.add_command(label="Copy", command=lambda: master.event_generate("<<Copy>>"))
        self.add_command(label="Paste", command=lambda: paste(master))
        self.add_command(label="Save")

class Notepad(Tk):
    def __init__(self, **kwargs):
        Tk.__init__(self, **kwargs)
        
        self.title("Notepad")
        
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.geometry(f"{screen_width}x{screen_height}")
        
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.menuBar = tk.Menu(self)
        self.fileMenu = tk.Menu(self.menuBar, tearoff=0)
        self.editMenu = tk.Menu(self.menuBar, tearoff=0)
        self.viewMenu = tk.Menu(self.menuBar, tearoff=0)
        self.helpMenu = tk.Menu(self.menuBar, tearoff=0)
        self.config(menu=self.menuBar)

        # Main text area
        self.text = ScrollableText(self, undo=True, autoseparators=True, maxundo=-1)
        self.text.frame.grid(row=0, column=1, sticky="NSEW")

        # Line numbers
        self.line_numbers = tk.Canvas(self, width="30", height="500")
        self.line_numbers.grid(row=0, column=0, sticky='NS', pady=1, rowspan=3)

        # Status bar on the bottom
        self.status_bar = StatusBar(self)
        self.status_bar.grid(row=2, column=1, columnspan=2, sticky="EW")

        # Right-click popup menu
        self.popup_menu = PopupMenu(self.text)

        # Custom undo/redo behavior, undo deletes until previous word
        self.text.bind("<space>", lambda event: self.text.edit_separator())
        self.text.bind("<Return>", lambda event: self.text.edit_separator())

        # Update word count
        self.text.bind("<KeyRelease>", self.redraw)

        # By default ctrl+v doesn't overwrite selected text
        self.text.bind("<<Paste>>", lambda event: delete_selection(self.text))

        # Select all
        self.text.bind("<Control-Key-a>", lambda event: select_all(self.text))
        self.text.bind("<Control-Key-A>", lambda event: select_all(self.text)) # In case caps lock

        # Create and close right click popup
        self.text.bind("<Button-3>", lambda event: do_popup(event.x_root, event.y_root, popup_menu)) # Right click
        self.popup_menu.bind("<FocusOut>", lambda event: close_popup(popup_menu))

        self.text.focus()
        self.redraw()

    def redraw(self, event=None):
        # Update status bar
        words = self.text.get('1.0', tk.END).split()
        word_count = len(words)
        self.status_bar.update(word_count)

        # Draw line numbers
        self.line_numbers.delete("all")
        index = "1.0"
        while True:
            line_info = self.text.dlineinfo(index)
            if line_info is None:
                break
            x_coord = 2
            y_coord = line_info[1]
            line_num = str(index).split(".")[0]
            self.line_numbers.create_text(x_coord, y_coord, anchor="nw", text=line_num, fill="black")
            index = self.text.index(f"{index}+1line")

        # Highlight
        # self.text.highlight_pattern("a", "BOLD")

notepad = Notepad()
notepad.mainloop()