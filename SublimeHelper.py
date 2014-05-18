# -*- encoding: UTF-8 -*-

"""
SublimeHelper.py - https://github.com/revolunet/sublimetext-google-apps-scripts
copyright: (c) 2013 by Julien Bouquillon - julien@revolunet.com
license: MIT
"""

''' helper class to abstract the ST2/ST3 plugin API changes '''

import sublime
import os
import tempfile

def write(content, path=None, name=None, encoding='utf-8'):
    ''' write a file and generate tempfile if no path defined.
        rename the final file if 'name' defined.
        return the final path.
    '''
    if not path:
        handle, path = tempfile.mkstemp()
        if name:
            path2 = os.path.join(os.path.dirname(path), name)
            os.close(handle)
            os.rename(path, path2)
            path = path2
    with open(path, 'w') as f:
        f.write(content.encode(encoding))
    return path

def show_list_panel(items, callback):
    get_window().show_quick_panel(items, callback)

def get_window():
    return sublime.active_window()

def message(msg):
    sublime.message_dialog(msg)

def show_input(title, message, callback):
    sublime.active_window().show_input_panel(title, message, callback, lambda a:a, lambda a:a)
