#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
#  open_counterpart.py
#  SphinxDoc.tmbundle
#  
#  Created by André Berg on 2010-12-16.
#  Copyright 2010 Berg Media. All rights reserved.
# 
#  This script can be used to open the counterpart
#  of source and target files. When launched from
#  a source file, open the target file in build dir
#  that has the same name as source file but with 
#  the file extension typical for the target file.
#  That is to say, when used on a file "file.rst"
#  open "file.html" in "_build" folder, and vice
#  versa. 
#  The correct file extension for a source file is
#  inferred from a setting named "source_suffix"
#  from the config file (conf.py).
#

import os
import sys

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
    filename = "checkfileseq.rst"
    buildirname = "_build"
else:
    tmdir = os.environ.get('TM_PROJECT_DIRECTORY', os.environ.get('TM_DIRECTORY', None))
    tmpython = os.environ.get('TM_PYTHON', 'python')
    buildirname = os.environ.get('TM_SPHINX_BUILD_DIR_NAME', '_build')
    if len(sys.argv) > 1:
        currentfile = sys.argv[1]
    else:
        sys.exit(1)

filename, fileext = os.path.splitext(currentfile)
srcsuffix = util.get_conf_value("source_suffix", tmdir)

if fileext == srcsuffix:
    targetext = ".html"
    filedir = tmdir + os.path.sep + buildirname
else:
    targetext = srcsuffix
    filedir = tmdir

targetfilename = "%s%s" % (os.path.basename(filename), targetext)

if DEBUG:
    print "filename = %s, fileext = %s" % (filename, fileext)
    print "filedir = %s" % (filedir)
    print "targetfilename = %s" % targetfilename

found_path = None
exclude_files = ['.DS_Store', '.Trash', '.Trashes', '.fseventsd', '.Spotlight-V100', '.hotfiles.btree']

for root, dirs, files in os.walk(filedir):
    if DEBUG: print("root = %s, dirs = %s" % (root, dirs))
    for f in files:
        if f in exclude_files:
            if DEBUG: print("excluding '%s'..." % f)
            continue
        (filename, fileext) = os.path.splitext(f)
        if DEBUG: print "f == %s" % f
        if f == targetfilename:
            found_path = os.path.join(root, targetfilename)
            break
    if found_path:
        break

if found_path:
    os.system('open -a TextMate "%s"' % found_path)
else:
    print("nothing found for '%s'" % (os.path.basename(targetfilename)))