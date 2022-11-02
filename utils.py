import tkinter as tk
import pyperclip

def do_popup(x, y, popup_menu):
    popup_menu.post(x, y)
    popup_menu.focus_set()

def close_popup(popup_menu):
    popup_menu.unpost()

def select_all(text_area):
    text_area.tag_add(tk.SEL, "1.0", tk.END)
    text_area.mark_set(tk.INSERT, "1.0")
    text_area.see(tk.INSERT)
    return "break"

def delete_selection(text_area):
    try:
        text_area.delete("sel.first", "sel.last")
    except:
        pass

def paste(text_area):
    delete_selection(text_area)
    text_area.insert("insert", text_area.clipboard_get())