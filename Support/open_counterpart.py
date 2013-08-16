##!/usr/bin/env python
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
#  from the config file (conf.py) but defaults to
#  the Sphinx default of .rst if this setting isn't
#  found.
#

import os
import sys

DEBUG = 0

if DEBUG:
    tmbundlesup = os.path.expandvars("$HOME") + "/Library/Application Support/TextMate/Bundles/SphinxDoc.tmbundle/Support"
else:
    tmbundlesup = os.environ['TM_BUNDLE_SUPPORT']
    
sys.path.append(tmbundlesup)
from sphinxdoc import SphinxDocUtils as util

if DEBUG:
    # current_dir= "/Users/andre/Documents/TextMate/SampledocTutorial/sampledoc"
    # project_dir = "/Users/andre/Documents/TextMate/SampledocTutorial"
    # current_dir= "/Users/andre/source/sphinx/hg/sphinx/doc/ext"
    # project_dir = "/Users/andre/source/sphinx/hg/sphinx"
    #current_dir= "/Users/andre/test/sphinxtest"
    #project_dir = "/Users/andre/test/sphinxtest"
    #tmpython = "/usr/local/bin/python2.7"
    #filename = "ifconfig.rst"
    #build_dir = "_build/html"
    current_dir= "/Users/andre/source/OpenCV-2.4.2"
    project_dir = "/Users/andre/source/OpenCV-2.4.2"
    tmpython = "/usr/local/bin/python2.7"
    filename = "index.rst"
    build_dir = "_build"
    filename, fileext = os.path.splitext(filename)
else:
    current_dir= util.read_value_from_registry('current_dir')   # current_dir"${TM_DIRECTORY:-$TM_PROJECT_DIRECTORY}" parent dir of active file
    project_dir = util.read_value_from_registry('project_dir')   # project_dir="${TM_PROJECT_DIRECTORY:-$TM_DIRECTORY}" selected dir in project drawer (if tmproject)
    tmpython = util.read_value_from_registry('python')
    build_dir = util.read_value_from_registry('build_dir')       # build_dir="${TM_SPHINX_BUILD_DIR:-_build/html}"
    #print("current_dir= %s" % (current_dir)
    #print("project_dir = %s" % (project_dir))
    #print("tmpython = %s" % (tmpython))
    #print("build_dir = %s" % (build_dir))
    
    if len(sys.argv) > 1:
        filename, fileext = os.path.splitext(sys.argv[1])
    else:
        sys.exit(1)

config_filepath = util.find_config_file(base_dirs=[current_dir, project_dir])
srcsuffix = util.get_conf_value("source_suffix", config_filepath, default=".rst")

# sanitize
if current_dir[-1] == os.path.sep:
    current_dir= current_dir[0:-1]
if project_dir[-1] == os.path.sep:
    project_dir = project_dir[0:-1]
if tmpython[-1] == os.path.sep:
    tmpython = tmpython[0:-1]
if build_dir[-1] == os.path.sep:
    build_dir = build_dir[0:-1]

# makes the operation reversible, e.g.
# go from source to counterpart and back again
if fileext == srcsuffix:
    target_ext = ".html"
    target_filetype = "htmlfile"
    (build_dir, searched_dirs) = util.find_dir(build_dir, [current_dir, project_dir])
    if build_dir is None:
        source_dirs = [project_dir] # fall back to project dir if the source dir wasn't found
    else:
        source_dirs = [build_dir, project_dir]
else:
    target_ext = srcsuffix
    target_filetype = "sourcefile"
    source_dirs = [current_dir, project_dir]

target_filename = "%s%s" % (os.path.basename(filename), target_ext)

if DEBUG:
    print("filename = %s, fileext = %s" % (filename, fileext))
    print("current_dir= %s" % (current_dir))
    print("source_dirs = %s" % (source_dirs))
    print("project_dir = %s" % (project_dir))
    print("build_dir = %s" % build_dir)
    print("tmpython = %s" % tmpython)
    print("targetfilename = %s" % target_filename)

found = None

(found, searched) = util.find_file(target_filename, source_dirs)

if found:
    util.open(found, app='TextMate')
else:
    infomsg = util.make_locations_searched_message(target_filename, searched, relative=True, curdir=current_dir)
    print(infomsg)
    
    