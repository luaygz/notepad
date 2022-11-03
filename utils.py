import tkinter as tk
from Phyme import Phyme
from Phyme.rhymeUtils import count_syllables, get_phones, extract_syllables

phyme = Phyme()

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

def control_backspace(text_area):
    cursor_index = text_area.index(tk.INSERT)
    row, column = cursor_index.split(".")
    column = int(column)
    current_line = text_area.get("insert linestart", "insert lineend")
    nearest_space = current_line.rfind(" ", 0, column)
    if nearest_space == -1:
        nearest_space = 0
    start_index = row + "." + str(nearest_space)
    text_area.tag_add(tk.SEL, start_index, cursor_index)

def is_word_char(char):
    return char.lower() in "abcdefghijklmnopqrstuvwxyz'"

def get_current_word(text, index):
    # If char is a nonword (like a space), but is at the boundary of a word on its right,
    # move index to the right
    # e.g.
    # abc |def geh
    #     ^ if the cursor is here, it gives the index of the space before it, but we want
    #       to still assume we are referencing the next word
    should_check_right = index < 0 or not is_word_char(text[index])
    char_to_right_is_word = index < len(text) - 1 and is_word_char(text[index+1])
    if should_check_right and char_to_right_is_word:
        index += 1
    if index < 0:
        return ""
    # Get left boundary
    left_index = index
    while left_index >= 0 and is_word_char(text[left_index]):
        left_index -= 1
    left_index += 1
    # Get right boundary
    right_index = index
    while right_index < len(text) and is_word_char(text[right_index]):
        right_index += 1
    right_index -= 1
    return text[left_index:right_index+1]

def flatten_rhymes_dict(d, num_syllables):
    rhymes = []
    if num_syllables in d:
        rhymes.extend(d[num_syllables])
    for key, value in sorted(d.items(), reverse=True):
        if key == num_syllables:
            continue
        rhymes.extend(value)
    return rhymes

def get_rhymes(word):
    rhymes = []
    try:
        num_syllables = count_syllables(word)
        # for i in range(num_syllables, 0, -1):
        #     perfect_rhymes = phyme.get_perfect_rhymes(word, num_syllables=i)
        #     rhymes.extend(flatten_rhymes_dict(perfect_rhymes, num_syllables))
        for i in range(num_syllables, 0, -1):
            assonance_rhymes = phyme.get_assonance_rhymes(word, num_syllables=i)
            rhymes.extend(flatten_rhymes_dict(assonance_rhymes, num_syllables))
    except:
        pass
    rhymes = list(dict.fromkeys(rhymes)) # Get unique
    rhymes = rhymes[:1000]
    rhymes = [w for w in rhymes if w != word]
    return rhymes