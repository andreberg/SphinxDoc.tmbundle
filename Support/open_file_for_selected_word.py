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
#  It has since been expanded to include functionality
#  for resolving the selected text as path relative
#  to the outdir (_build by default).
#
#  That is, given:
# 
#  - source_suffix is "rst", and outdir is "_build" 
#
#  - if the cursor is in "word", try to find "word.rst" 
#    in any dir under outdir whose name is *NOT* matched
#    by the conf.py setting 'exclude_patterns'.
#
#  - if "path1/path2/index.html" is selected, try to find 
#    "/Macintosh HD/some/absolute/base/path/_build/path1/path2/index.html"
#    This doesn't care about 'exclude_patterns'.
#  
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

class FileLinkResolver(object):
    """Provides methods for resolving counterparts and relative file links."""
    
    exclude_files = ['.DS_Store', '.Trash', '.Trashes', '.fseventsd', '.Spotlight-V100', '.hotfiles.btree']
    
    def __init__(self, basedir):
        super(FileLinkResolver, self).__init__()
        
        _tmpresult = util.get_conf_value('exclude_patterns', basedir)
        if _tmpresult is not None:
            if isinstance(_tmpresult, list):
                exclude_patterns = _tmpresult
            else:
                exclude_patterns = [str(_tmpresult)]
        else:
            exclude_patterns = []
        
        _tmpresult = util.get_conf_value('source_suffix', basedir)
        if _tmpresult is not None:
            if isinstance(_tmpresult, list):
                supported_exts = _tmpresult
            else:
                supported_exts = [str(_tmpresult)]
        else:
            supported_exts = ['.rst', '.rest', '.txt']
            
        self.exclude_patterns = exclude_patterns
        self.supported_exts = supported_exts
        self.basedir = basedir
        self.resolved_path = None
    
    @classmethod
    def is_rel_path(cls, apath):
        """Return True if apath is a relative path."""
        return (not (os.path.isabs(apath)) and apath.find(os.path.sep) > -1)
    
    def resolve_rel_path(self, relpath, basedir=None):
        """Return the absolute path for basedir+relpath."""
        if basedir == None:
            basedir = self.basedir
        
        oldcurdir = os.curdir
        
        os.chdir(self.basedir)
        resolved_path = os.path.abspath(relpath)
        if os.path.exists(resolved_path):
            found_path = resolved_path
            self.resolved_path = found_path
        else:
            # try one more time in the immediate parent dir of the rel path
            # this is neccesary because when only one builder is used, as is
            # by default the html builder, Sphinx may not produce one subdir 
            # per builder, e.g. outdir/<builder>/outfile.ext may be outdir/outfile.ext 
            # instead.
            parts = relpath.split(os.path.sep)
            try_path = os.path.sep.join(parts[0:-2]) + os.path.sep + parts[-1]
            resolved_path = os.path.abspath(try_path)
            if os.path.exists(resolved_path):
                found_path = resolved_path
                self.resolved_path = found_path
            else:
                found_path = None
            
        os.chdir(oldcurdir)
        return found_path
    
    def find_source_file(self, word, basedir=None):
        """Given a word, find the source which corresponds to `<word>.<ext>` by walking basedir until found."""
        
        if basedir == None:
            basedir = self.basedir
        found_path = None
        for root, dirs, files in os.walk(basedir):
            if DEBUG: print("root = %s, dirs = %s<br>" % (root, dirs))
            for pat in self.exclude_patterns:
                if DEBUG: print("trying to exclude pattern '%s'" % pat)
                if pat in root:
                    if DEBUG: print("excluding... pattern '%s'" % pat)
                    continue
                for f in files:
                    (filename, fileext) = os.path.splitext(f)
                    
                    #print "f = %s<br>" % f
                    #print "filename = %s, fileext = %s<br>" % (filename, fileext)
                    #print "root = %s<br>" % root
                    
                    if f in FileLinkResolver.exclude_files:
                        continue
                    for ext in self.supported_exts:
                        if ext[:1] != ".":
                            ext = "." + ext
                        try_fname = word + ext
                        try_path = root + os.sep + try_fname
                        
                        #print "try_fname = %s<br>" % try_fname
                        #print("try_path = %s<br>" % try_path)
                        
                        if os.path.exists(try_path):
                            found_path = try_path
                            if DEBUG: print("found_path = %s" % found_path + "<br>")
                            self.resolved_path = found_path
                        if found_path:
                            break
                    if found_path:
                        break
                if found_path:
                    break
            if found_path:
                break
        return found_path
    


def main(argv=None):
    '''Command line options.'''
    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)
    try:
        if DEBUG:
            tmdir = "/Users/andre/Documents/Aptana Studio 2.0/Workspaces/Python/File Sequence Checker/doc/sphinx"
            tmpython = "/usr/local/bin/python2.7"
            cursor_word = "checkfileseq"
            #cursor_path = "_build/html/index.html"
            #cursor_word = cursor_path
        else:
            tmdir = os.environ.get('TM_PROJECT_DIRECTORY', os.environ.get('TM_DIRECTORY', None))
            tmpython = os.environ.get('TM_PYTHON', 'python')
            cursor_word = util.current_word()
            
        if cursor_word is None or tmdir is None:
            print("Can't get current word or nothing selected")
            sys.exit(1)
        
        found_path = None
        flr = FileLinkResolver(tmdir)
                
        if FileLinkResolver.is_rel_path(cursor_word):
            # see if the selected text constitutes a relative path
            # before we try to find <current_word>.<ext> in a walk
            found_path = flr.resolve_rel_path(cursor_word)
        else:
            found_path = flr.find_source_file(cursor_word)    
        
        if found_path:
            os.system('open -a TextMate "%s"' % found_path)
        else:
            if DEBUG:
                print("type exclude_patterns = %s" % type(flr.exclude_patterns))
                print("type supported_exts = %s" % type(flr.supported_exts))
                print("exclude_patterns = %s" %  flr.exclude_patterns)
                print("supported_exts = %s" %  flr.supported_exts)
                print("flr.resolved_path = %s" % flr.resolved_path)
            if len(flr.supported_exts) == 1:
                supported_exts = flr.supported_exts[0]
            
            print("nothing found for '%s%s'" % (cursor_word, str(supported_exts)))
            print("if applicable, try selecting the whole path")
        return 0
    except KeyboardInterrupt:
        # handle keyboard interrupt
        return 0
    except Exception as e:
        if ("%x" % sys.hexversion)[0] == '3':
            sys.stderr.write(sys.argv[0].split("/")[-1] + ": " + str(e))
            sys.stderr.write("\n%s  for help use --help" % (" " * len(sys.argv[0].split("/")[-1])))
        else:
            sys.stderr.write(sys.argv[0].split("/")[-1] + ": " + str(e).decode('unicode_escape'))
            sys.stderr.write("\n%s  for help use --help\n" % (" " * len(sys.argv[0].split("/")[-1])))
        return 2

if __name__ == '__main__':
    main()
