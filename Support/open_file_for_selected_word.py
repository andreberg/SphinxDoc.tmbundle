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
#  to the outdir (_build by default) as well as opening
#  absolute file paths.
#
#  For example, given source_suffix is "rst", and 
#  outdir is "_build":
#
#  - if the cursor is in "word", try to find "word.rst" 
#    in any dir under outdir whose name is *NOT* matched
#    by the conf.py setting 'exclude_patterns'.
#
#  - if "path1/path2/index.html" is selected, try to find 
#    "/Macintosh HD/some/absolute/base/path/_build/path1/path2/index.html"
#    This doesn't care about 'exclude_patterns'.
#
#  - fall back to walking the tree under the project
#    root, if selected text describes filename incl. some
#    file extension.
#
#  - if selected text looks like it contains an URL open
#    that with the default system app.  
#

import os
import sys
import subprocess
import shlex
from glob import glob


DEBUG = 0

if DEBUG:
    tmbundlesup = os.path.expandvars("$HOME") + "/Library/Application Support/TextMate/Bundles/Sphinx Doc.tmbundle/Support"
else:
    tmbundlesup = os.environ['TM_BUNDLE_SUPPORT']
    
sys.path.append(tmbundlesup)

from sphinxdoc import SphinxDocUtils as utils
from sphinxdoc import DEFAULT_FILE_EXCLUDES, URL_REGEX # IGNORE:W0611 @UnusedImport
from sphinxdoc import working_directory

class PathResolver(object):
    '''
    Provides methods for resolving paths contained 
    within the currently selected text.
    '''
    exclude_files = DEFAULT_FILE_EXCLUDES
    
    def __init__(self, base_dirs):
        super(PathResolver, self).__init__()
        
        #config_filepath = utils.find_config_file(base_dirs=base_dirs)
        config_filepath = utils.read_value_from_registry('conf_dir')

        _tmpresult = utils.get_conf_value('exclude_patterns', config_filepath)
        
        if _tmpresult is not None:
            if isinstance(_tmpresult, list):
                exclude_patterns = []
                for entry in _tmpresult:
                    tmpglob = glob(entry)
                    if len(tmpglob) > 0:
                        exclude_patterns += tmpglob
            else:
                exclude_patterns = [str(_tmpresult)]
        else:
            exclude_patterns = []

        _tmpresult = utils.get_conf_value('source_suffix', config_filepath, default=".rst")
        
        supported_exts = ['.py', '.rst', '.rest', '.txt', '.test', '.fest']
        
        if _tmpresult is not None:
            if isinstance(_tmpresult, list):
                supported_exts.extend(_tmpresult)
            else:
                supported_exts.append(str(_tmpresult))
        
        # unique
        supported_exts = list(set(supported_exts))

        self.exclude_patterns = exclude_patterns
        self.supported_exts = supported_exts
        self.base_dirs = base_dirs
        self.resolved_path = None
    
    def resolve_rel_path(self, relpath):
        '''Return the absolute path for basedir+relpath.'''
        
        for basedir in self.base_dirs:
        
            found_path = None
            with working_directory(basedir):
                resolved_path = os.path.abspath(relpath)
                if os.path.exists(resolved_path):
                    found_path = resolved_path
                    self.resolved_path = found_path
                    break
                else:
                    # FIXME: get rid of this one more time test because it makes assumptions about the build dir layout.
                    # Ideally there should be no assumptions at all and the base dirs to work with should be meaningful
                    # enough to begin with.
                     
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
                        break                        

            #os.chdir(oldcurdir)
        return found_path
    
    # TODO: rewrite find_source_file to use SphinxDocUtils.find_file instead.
    # not entirely sure why this isn't using find_file. From what I can see
    # doesn't modify internal state of PathResolver.
    def find_source_file(self, word):
        '''Given a word, find the source which corresponds to `<word>.<ext>` by walking basedir until found.'''
        found_path = None
        for basedir in self.base_dirs:
            for root, dirs, files in os.walk(basedir):
                if DEBUG > 1: print "root = %s, dirs = %s<br>" % (root, dirs)
                for pat in self.exclude_patterns:
                    if DEBUG > 1: print "trying to exclude pattern '%s'" % pat
                    if pat in root:
                        if DEBUG > 1: print "excluding... pattern '%s'" % pat
                        continue
                for f in files:
                    (filename, fileext) = os.path.splitext(f)
                    
                    if DEBUG > 1:
                        print "f = %s" % f
                        print "filename = %s, fileext = %s<br>" % (filename, fileext)
                        print "root = %s<br>" % root
                    
                    if f in PathResolver.exclude_files:
                        continue
                    for ext in self.supported_exts:
                        if ext[:1] != ".":
                            ext = "." + ext
                        try_fname = word + ext
                        try_path = root + os.sep + try_fname
                        
                        if DEBUG > 1:
                            print "try_fname = %s<br>" % try_fname
                            print "try_path = %s<br>" % try_path
                        
                        if os.path.exists(try_path):
                            found_path = try_path
                            if DEBUG > 1: print "found_path = %s" % found_path + "<br>"
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
    

def selection_is_valid(selection):
    result = True
    # add additional logic here if needed
    if os.linesep in selection:
        result = False
    return result

def main(argv=None):
    '''Command line options.'''
    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)
    try:
        if DEBUG:
            tmdir = "/Users/andre/source/OpenCV-2.4.2/doc/tutorials/gpu/gpu-basics-similarity"
            projectdir = "/Users/andre/source/OpenCV-2.4.2"
            #selected_text = "samples/cpp/tutorial_code/gpu/gpu-basics-similarity/gpu-basics-similarity"
            selected_text = "../../../../samples/cpp/tutorial_code/gpu/gpu-basics-similarity/gpu-basics-similarity.cpp"
            #selected_text = "/Users/andre/test/test.txt"
            #cursor_path = "_build/html/index.html"
            #selected_text = cursor_path
        else:
            tmdir = utils.read_value_from_registry("current_dir")
            projectdir = utils.read_value_from_registry("project_dir")
            selected_text = utils.current_word().strip()
        
        if selected_text == "":
            return 0
        if selected_text is None:
            print "Can't get current word or nothing selected"
            sys.exit(1)
        if (tmdir is None or not os.path.exists(tmdir)) and \
           (projectdir is None or not os.path.exists(projectdir)):
            print "TM_DIRECTORY and TM_PROJECT_DIRECTORY are both undefined. Can't continue..."
            sys.exit(1)
        
        if not selection_is_valid(selected_text):
            raise ValueError("Error while trying to open file for selected text:\nnot a valid selection")
        
        if utils.contains_url(selected_text):
            url = utils.extract_url(selected_text)
            if url:
                #preferred_browser = utils.read_value_from_registry('preferred_browser')
                #utils.system("/usr/bin/open -a '%s' '%s'" % (preferred_browser, url))
                utils.open(url)
                return 0           
        
        # Two scenarios:
        #
        # 1. the selected word is a complete file name incl. an extension 
        # 2. the selected word is doesn't include any file extension
        # 
        # for 1. walk the complete tree with no restrictions starting from project base
        # for 2. walk the complete tree same as in 1. but do restrict the set of possible
        # candidates to files that have a file extensions matching source_suffix as defined 
        # in config file (or .rst if absent) and do not visit dirs matching the exclude_dirs 
        # setting in the config file
        
        with working_directory(tmdir):
            
            #olddir = os.path.abspath(os.curdir)
            #os.chdir(tmdir)
            
            found_path = None
            if not utils.is_rel_path(selected_text) and os.path.exists(selected_text):
                found_path = selected_text
            
            if not found_path:
                # see if the selected text constitutes a relative path
                # before we try to find <current_word>.<ext> in a walk
                resolver = PathResolver([tmdir, projectdir])
                found_path = resolver.resolve_rel_path(selected_text)
                if not found_path:
                    unused_root, ext = os.path.splitext(selected_text) # IGNORE:W0612
                    if len(ext) == 0:
                        found_path, unused_searched = utils.find_dir(selected_text, resolver.base_dirs)
                        if found_path:
                            utils.open(found_path)
                            return 0
                        else:
                            found_path = resolver.find_source_file(selected_text)
                    else:
                        found_path, unused_searched = utils.find_file(selected_text, resolver.base_dirs) # IGNORE:W0612
                    
            if found_path:
                # check if found_path is a text based file
                is_text = utils.is_text_based_file(found_path)
                if is_text:
                    utils.open(found_path, app='TextMate')
                    return 0
                else:
                    # open in system default viewer
                    utils.open(found_path)
                    return 0      
            else:
                if DEBUG:
                    print "type exclude_patterns = %s" % type(resolver.exclude_patterns)
                    print "type supported_exts = %s" % type(resolver.supported_exts)
                    print "exclude_patterns = %s" %  resolver.exclude_patterns
                    print "supported_exts = %s" %  resolver.supported_exts
                    print "resolver.resolved_path = %s" % resolver.resolved_path
                
                # TODO: constructing the "nothing found for ..." message should be handled by the PathResolver itself.
                searched_filenames = ""
                buildup_len = len("nothing found for ")
                maxlen = len(resolver.supported_exts)
                max_line_len = 70
                i = 1
                for ext in resolver.supported_exts:
                    filename = "'" + selected_text + ext + "'"
                    if i == maxlen:
                        text = " or " + filename
                        buildup_len += len(text)
                        if buildup_len >= max_line_len:
                            text = " or\n" + filename
                            buildup_len = 0
                    elif i == maxlen-1:
                        text = filename
                        buildup_len += len(text)
                        if buildup_len >= max_line_len:
                            text = "\n" + filename
                            buildup_len = 0
                    else:
                        text = filename + ", "
                        buildup_len += len(text)
                        if buildup_len >= max_line_len:
                            text = "\n" + filename + ", "
                            buildup_len = 0
                    searched_filenames += text
                    buildup_len += len(text)
                    i += 1
                print "nothing found for %s\n" % (searched_filenames)
                print "if applicable, try appending the correct file ext"
                print "or try selecting the whole path if it is absolute"
                
            #os.chdir(olddir)
        return 0
    except KeyboardInterrupt:
        return 0
    except Exception as e:
        try:
            msg = str(e)
        except UnicodeDecodeError:
            msg = repr(e)
        except UnicodeEncodeError:
            msg = repr(e)
        # html_err_msg = utils.err_msg_to_html(msg, sys.argv[0])
        tooltip_err_msg = msg
        sys.stderr.write(tooltip_err_msg)
        return 2

if __name__ == '__main__':
    main()
