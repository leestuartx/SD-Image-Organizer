import tkinter as tk

def apply_dark_mode(widget):
    widget.tk_setPalette(background='#2b2b2b', foreground='#d3d3d3',
                         activeBackground='#3a3a3a', activeForeground='#d3d3d3')

    style = {
        'background': '#3a3a3a',
        'foreground': '#d3d3d3',
        'selectBackground': '#4a4a4a',
        'selectForeground': '#d3d3d3'
    }

    text_style = {
        'background': '#3a3a3a',
        'foreground': '#d3d3d3',
        'insertbackground': '#d3d3d3',
        'selectbackground': '#4a4a4a',
        'selectforeground': '#d3d3d3'
    }

    label_style = {
        'foreground': '#d3d3d3'
    }

    button_style = {
        'background': '#4a4a4a',
        'foreground': '#d3d3d3',
        'activebackground': '#3a3a3a',
        'activeforeground': '#d3d3d3'
    }

    if isinstance(widget, (tk.Text, tk.Entry, tk.Listbox)):
        widget.configure(**text_style)
    elif isinstance(widget, tk.Label):
        widget.configure(**label_style)
    elif isinstance(widget, tk.Button):
        widget.configure(**button_style)
    else:
        widget.configure(**style)

    for child in widget.winfo_children():
        apply_dark_mode(child)
