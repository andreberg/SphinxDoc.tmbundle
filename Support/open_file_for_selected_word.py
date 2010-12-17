##!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
#  open_file_for_selected_word.py
#  SphinxDoc.tmbundle
#  
#  Created by André Berg on 2010-12-14.
#  Copyright 2010 Berg Media. All rights reserved.
# 
#  Like the filename implies this bit of Python
#  code is used to open the file counterpart
#  corresponding to the current selection of text
#  or the active word plus the file ext as set in 
#  conf.py (under a setting named "source_suffix")
#

import os
import sys
from subprocess import PIPE, Popen

DEBUG = 0

if DEBUG:
    tmbundlesup = "/Users/andre/Library/Application Support/TextMate/Bundles/Sphinx Doc.tmbundle/Support"
else:
    tmbundlesup = os.environ['TM_BUNDLE_SUPPORT']
    
sys.path.append(tmbundlesup)
from sphinxdoc import SphinxDocUtils as util

if DEBUG:
    tmdir = "/Users/andre/Documents/Aptana Studio 2.0/Workspaces/Python/File Sequence Checker/doc/sphinx"
    tmpython = "/usr/local/bin/python2.7"
    cursor_word = "checkfileseqs"
else:
    tmdir = os.environ.get('TM_PROJECT_DIRECTORY', os.environ.get('TM_DIRECTORY', None))
    tmpython = os.environ.get('TM_PYTHON', 'python')
    cursor_word = util.current_word()
    

if cursor_word is None or tmdir is None:
    print("Can't get current word or nothing selected")
    sys.exit(1)

found_path = None

exclude_files = ['.DS_Store', '.Trash', '.Trashes', '.fseventsd', '.Spotlight-V100', '.hotfiles.btree']

_tmpresult = util.get_conf_value('exclude_patterns', tmdir)
if _tmpresult is not None:
    if isinstance(_tmpresult, list):
        exclude_patterns = _tmpresult
    else:
        exclude_patterns = [str(_tmpresult)]
else:
    exclude_patterns = []

_tmpresult = util.get_conf_value('source_suffix', tmdir)
if _tmpresult is not None:
    if isinstance(_tmpresult, list):
        supported_exts = _tmpresult
    else:
        supported_exts = [str(_tmpresult)]
else:
    supported_exts = ['.rst', '.rest', '.txt']

for root, dirs, files in os.walk(tmdir):
    if DEBUG: print("root = %s, dirs = %s<br>" % (root, dirs))
    for pat in exclude_patterns:
        if DEBUG: print("trying exclude pattern %s<br>" % pat)
        if pat in root:
            if DEBUG: print("excluding...<br>")
            continue
        for f in files:
            (filename, fileext) = os.path.splitext(f)

            #print "f = %s<br>" % f
            #print "filename = %s, fileext = %s<br>" % (filename, fileext)
            #print "root = %s<br>" % root

            if f in exclude_files:
                continue
            for ext in supported_exts:
                if ext[:1] != ".":
                    ext = "." + ext
                try_fname = cursor_word + ext
                try_path = root + os.sep + try_fname

                #print "try_fname = %s<br>" % try_fname
                #print "try_path = %s<br>" % try_path

                if os.path.exists(try_path):
                    found_path = try_path
                    if DEBUG: print("found_path = %s" % found_path + "<br>")
                if found_path:
                    break
            if found_path:
                break
        if found_path:
            break
    if found_path:
        break

if found_path:
    os.system('open -a TextMate "%s"' % found_path)
else:
    if DEBUG:
        print("type exclude_patterns = %s" % type(exclude_patterns))
        print("type supported_exts = %s" % type(supported_exts))
        print("exclude_patterns = %s" %  exclude_patterns)
        print("supported_exts = %s" %  supported_exts)
    if len(supported_exts) == 1:
        supported_exts = supported_exts[0]
    print("nothing found for '%s%s'" % (cursor_word, str(supported_exts)))