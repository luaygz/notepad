import tkinter as tk
import tkinter.ttk as ttk
from tkinter import Text

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
# text_area.insert(tk.END, ('a'*999 + '\n')*999)
text_area.focus()

text_area.bind("<space>", lambda event: text_area.edit_separator())
text_area.bind("<Return>", lambda event: text_area.edit_separator())
line_numbers = tk.Canvas(window, width="30", height="500")
line_numbers.grid(row=0, column=0, sticky='NS', pady=1, rowspan=3)

window.mainloop()