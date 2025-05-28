#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# vim:ts=4:sw=4:softtabstop=4:smarttab:expandtab

# Copyright 2017 Kevin B. Hendricks, Stratford Ontario

# This plugin's source code is available under the GNU LGPL Version 2.1 or GNU LGPL Version 3 License.
# See https://www.gnu.org/licenses/old-licenses/lgpl-2.1.en.html or
# https://www.gnu.org/licenses/lgpl.html for the complete text of the license.
# If a different license is required, please contact the author directly for written permission

from __future__ import unicode_literals, division, absolute_import, print_function

import sys
import os
import re

try:
    from urllib.parse import unquote
except ImportError:
    from urllib import unquote

from plugin_utils_light import QtWidgets

# convert string to utf-8
def utf8_str(p, enc='utf-8'):
    if p is None:
        return None
    if isinstance(p, str):
        return p.encode('utf-8')
    if enc != 'utf-8':
        return p.decode(enc, errors='replace').encode('utf-8')
    return p

# convert string to be unicode encoded
def unicode_str(p, enc='utf-8'):
    if p is None:
        return None
    if isinstance(p, str):
        return p
    return p.decode(enc, errors='replace')

fsencoding = sys.getfilesystemencoding()

# handle paths that might be filesystem encoded
def pathof(s, enc=fsencoding):
    if s is None:
        return None
    if isinstance(s, str):
        return s
    if isinstance(s, bytes):
        try:
            return s.decode(enc)
        except:
            pass
    return s

# properly handle relative paths
def relpath(path, start=None):
    return os.path.relpath(pathof(path) , pathof(start))

# generate a list of files in a folder
def walk_folder(top):
    top = pathof(top)
    rv = []
    for base, dnames, names  in os.walk(top):
        base = pathof(base)
        for name in names:
            name = pathof(name)
            rv.append(relpath(os.path.join(base, name), top))
    return rv

# validate destination directory for font use
def valid_destination(destdir):
    files = walk_folder(destdir)
    for file in files:
        segs = file.split(os.sep)
        if "META-INF" in segs or "meta-inf" in segs:
            if "encryption.xml" in segs or "ENCRYPTION.XML" in segs:
                return False
    return True

# borrowed from calibre from calibre/src/calibre/__init__.py
# added in removal of non-printing chars
# and removal of . at start

def cleanup_file_name(name):
    import string
    _filename_sanitize = re.compile(r'[\xae\0\\|\?\*<":>\+/]')
    substitute='_'
    one = ''.join(char for char in name if char in string.printable)
    one = _filename_sanitize.sub(substitute, one)
    one = re.sub(r'\s', '_', one).strip()
    one = re.sub(r'^\.+$', '_', one)
    one = one.replace('..', substitute)
    # Windows doesn't like path components that end with a period
    if one.endswith('.'):
        one = one[:-1]+substitute
    # Mac and Unix don't like file names that begin with a full stop
    if len(one) > 0 and one[0:1] == '.':
        one = substitute+one[1:]
    return one


# routine to copy the files internal to Sigil for the epub being edited
# to a destination folder
def copy_book_contents_to(bk, destdir):
    destdir = unicode_str(destdir)
    # first copy all of the files that are listed in the opf manifest
    for id in bk._w.id_to_filepath:
        rpath = bk._w.id_to_filepath[id]
        data = bk.readfile(id)
        filepath = os.path.join(destdir,rpath)
        base = os.path.dirname(filepath)
        if not os.path.exists(base):
            os.makedirs(base)
        if isinstance(data, str):
            data = utf8_str(data)
        with open(pathof(filepath),'wb') as fp:
            fp.write(data)
        print("  saved:",rpath) 
    # now copy all of the non-manifested files
    for href in bk._w.book_href_to_filepath:
        rpath = bk._w.book_href_to_filepath[href]
        data = bk.readotherfile(href)
        filepath = os.path.join(destdir,rpath)
        base = os.path.dirname(filepath)
        if not os.path.exists(base):
            os.makedirs(base)
        if isinstance(data, str):
            data = utf8_str(data)
        with open(pathof(filepath),'wb') as fp:
            fp.write(data)
        print("  saved:",rpath) 


# the plugin entry point
def run(bk):

    if bk.launcher_version() < 20230315:
        print("This plugin requires Sigil-2.0.0 or later")
        return -1

    # handle preferences
    prefs = bk.getPrefs() # a dictionary
    prefs.defaults['lastDir'] = os.path.expanduser('~')
    basepath = prefs['lastDir']
    if not (os.path.exists(basepath) and os.path.isdir(basepath)):
        basepath = os.path.expanduser('~')
    
    # parse the opf to get first dc:title
    opfbookhref = "OEBPS/content.opf"
    if bk.launcher_version() >= 20190927:
        opfbookhref = bk.get_opfbookpath();
    opfdata = bk.readotherfile(opfbookhref)
    qp = bk.qp
    bk.qp.setContent(opfdata)
    dctitle = "foldername"
    # look for contents of first dc:title tag in the opf
    for txt, tp, tname, ttype, tattr in bk.qp.parse_iter():   
        if txt is not None:
            if tp.endswith(".dc:title"):
                dctitle = txt
                break

    if dctitle is None or dctitle == "":
        dctitle = "foldername"
    foldname = cleanup_file_name(dctitle)
    print("Book title: ", dctitle)
    print("Folder name: ", foldname)

    destpath = os.path.join(basepath, foldname)

    if os.path.exists(destpath) and os.path.isdir(destpath):
        basepath = destpath

    # ask the user to select the source folder to load files from
    app = QtWidgets.QApplication(sys.argv)
    foldpath = QtWidgets.QFileDialog.getExistingDirectory(None, 'Select Folder to copy ebook files into', basepath)
    app.quit()

    if not foldpath:
        print("FolderOut plugin cancelled by user")
        return 0

    # now copy files from ebook to this destination directory
    
    # for safety:
    #     existing files with duplicate paths are overwritten
    #     but already existing files with unique names are NOT changed
    
    if not os.path.isdir(foldpath):
        print("Folder selected is not a directory or does not exist")
        return -1

    if not valid_destination(foldpath):
        print("Folder selected is invalid due to existing encryption.xml")
        return -1

    try:
        copy_book_contents_to(bk,foldpath)
        # Add the proper mimetype file
        data = "application/epub+zip"
        with open(os.path.join(foldpath,"mimetype"),'wb') as f:
            f.write(data.encode('utf-8'))
        print("  saved: mimetype") 

    except Exception as e:
        print("Copy to Folder failed")
        print(str(e))
        return -1
        
    # handle preferences
    prefs['lastDir'] = os.path.dirname(foldpath)
    bk.savePrefs(prefs)
     
    # was successful so return with no error
    return 0

def main():
    print("I reached main when I should not have\n")
    return -1
    
if __name__ == "__main__":
    sys.exit(main())
