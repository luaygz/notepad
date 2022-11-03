import tkinter as tk
import tkinter.ttk as ttk
from tkinter import Text, Menu
from tkinter.ttk import Label
from tkinter import Tk
from ttkthemes import ThemedTk
from tkinter.font import Font

from utils import do_popup, close_popup, select_all, delete_selection, paste, get_current_word, get_rhymes, control_backspace

class ScrollableText(Text):
    def __init__(self, master=None, x_scroll=True, y_scroll=True, wrap=tk.NONE, **kwargs):
        self.frame = ttk.Frame(master)
        if x_scroll:
            self.x_scroll_bar = ttk.Scrollbar(self.frame, orient=tk.HORIZONTAL)
            self.x_scroll_bar.pack(side=tk.BOTTOM, fill=tk.X)
            self.xscrollcommand = self.x_scroll_bar.set
            self.x_scroll_bar.config(command=self.xview)
        else:
            self.xscrollcommand = None
        if y_scroll:
            self.y_scroll_bar = ttk.Scrollbar(self.frame)
            self.y_scroll_bar.pack(side=tk.RIGHT, fill=tk.Y)
            self.yscrollcommand = self.y_scroll_bar.set
            self.y_scroll_bar.config(command=self.yview)
        else:
            self.yscrollcommand = None
        Text.__init__(self, self.frame, wrap=wrap,
                      xscrollcommand=self.xscrollcommand,
                      yscrollcommand=self.yscrollcommand,
                      undo=True,
                      autoseparators=True,
                      maxundo=-1,
                      **kwargs)

        self.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Select all
        self.bind("<Control-Key-a>", lambda event: select_all(self))
        self.bind("<Control-Key-A>", lambda event: select_all(self)) # In case caps lock

        # Custom undo/redo behavior, undo deletes until previous word
        self.bind("<space>", lambda event: self.edit_separator())
        self.bind("<Return>", lambda event: self.edit_separator())

        # By default ctrl+v doesn't overwrite selected text
        self.bind("<<Paste>>", lambda event: delete_selection(self))

        # Control+backspace deletes entire word
        self.bind("<Control-BackSpace>", lambda event: control_backspace(self))

        # Right click popup menu
        self.popup_menu = PopupMenu(self)
        self.bind("<Button-3>", lambda event: do_popup(event.x_root, event.y_root, self.popup_menu)) # Right click
        self.popup_menu.bind("<FocusOut>", lambda event: close_popup(self.popup_menu))

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
        self.add_command(label="Explore Word")

class Notepad(Tk):
    def __init__(self, **kwargs):
        Tk.__init__(self, **kwargs)
        
        self.title("Notepad")
        
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        self.geometry(f"{screen_width}x{screen_height}")
        
        self.menuBar = tk.Menu(self)
        self.fileMenu = tk.Menu(self.menuBar, tearoff=0)
        self.editMenu = tk.Menu(self.menuBar, tearoff=0)
        self.viewMenu = tk.Menu(self.menuBar, tearoff=0)
        self.helpMenu = tk.Menu(self.menuBar, tearoff=0)
        self.config(menu=self.menuBar)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Status bar on the bottom
        self.status_bar = StatusBar(self)
        self.status_bar.grid(row=2, column=1, columnspan=2, sticky="EW")

        # Line numbers on the left
        self.line_numbers = tk.Canvas(self, width="30")
        self.line_numbers.grid(row=0, column=0, sticky='NS', pady=1, rowspan=3)

        # Main text area
        self.editor = ScrollableText(self)
        self.editor.frame.grid(row=0, column=1, sticky="NSEW", rowspan=2)

        # Info frame
        self.info_frame = ttk.Frame(self, width="400")
        self.info_frame.grid(row=0, column=2, sticky="NSEW")

        # Suggested rhymes text area
        self.suggested_rhymes = ScrollableText(self.info_frame, x_scroll=False, wrap=tk.WORD, state="disabled")
        self.suggested_rhymes.frame.pack(side=tk.LEFT, anchor="n")
        self.current_word = ""


        self.editor.bind("<KeyRelease>", self.update_rhymes)
        self.editor.bind("<ButtonRelease>", self.update_rhymes) # Mouse

        # Redraw status bar and line numbers
        self.bind("<KeyRelease>", self.redraw)
        self.bind("<Configure>", self.redraw) # Resizing window
        self.bind('<Button-4>', self.redraw) # Scroll up
        self.bind('<Button-5>', self.redraw) # Scroll down
        self.bind('<Motion>', self.redraw) # Mouse move

        self.editor.focus()
        self.redraw()

    def redraw(self, event=None):
        # Update status bar
        words = self.editor.get('1.0', tk.END).split()
        word_count = len(words)
        self.status_bar.update(word_count)

        # Draw line numbers
        self.line_numbers.delete("all")
        index = self.editor.index("@0,0") # First visible row
        while True:
            line_info = self.editor.dlineinfo(index)
            if line_info is None:
                break
            x_coord = 2
            y_coord = line_info[1]
            line_num = str(index).split(".")[0]
            self.line_numbers.create_text(x_coord, y_coord, anchor="nw", text=line_num, fill="black")
            index = self.editor.index(f"{index}+1line")

    def set_suggested_rhymes_text(self, text):
        self.suggested_rhymes.configure(state="normal")
        self.suggested_rhymes.delete("1.0", tk.END)
        self.suggested_rhymes.insert("1.0", text)
        self.suggested_rhymes.configure(state="disabled")

    def update_rhymes(self, event=None):
        lines = self.editor.get("1.0", tk.END).split("\n")
        index = self.editor.index(tk.INSERT)
        row = int(index.split(".")[0])
        col = int(index.split(".")[1]) - 1 # Cursor points to char before it
        line = lines[row-1]
        current_word = get_current_word(line, col)
        # print(self.current_word, current_word)
        if self.current_word != current_word:
            self.current_word = current_word
            self.set_suggested_rhymes_text(get_rhymes(current_word))

notepad = Notepad()
notepad.mainloop()