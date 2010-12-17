#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
#  sphinxdoc.py
#  SphinxDoc.tmbundle
#  
#  Created by André Berg on 2010-12-14.
#  Copyright 2010 Berg Media. All rights reserved.
# 
#  Description: 
#  Contains reusable modules and methods for the
#  whole bundle. Mimmicks the Ruby version at
#  sphinxdoc.rb. The goal is to be as language
#  agnostic as possible.
#

import sys
import os
import compileall
if ("%x" % sys.hexversion)[0] == '3':
    import urllib.parse
else:
    import urllib

DEBUG = 0

if DEBUG:
    os.environ['TM_BUNDLE_SUPPORT'] = "/Users/andre/Library/Application Support/TextMate/Bundles/Sphinx Doc.tmbundle/Support"

class SphinxDocUtils(object):
    """ Handy utilities for text conversions etc. """
    
    @staticmethod
    def url_esc(url):
        if ("%x" % sys.hexversion)[0] == '3':
            result = urllib.parse.quote(url)
        else:
            result = urllib.quote(url)
        return result
    
    @staticmethod
    def html_esc(text):
        html_escape_table = {
            "&": "&amp;",
            '"': "&quot;",
            "'": "&apos;",
            ">": "&gt;",
            "<": "&lt;",
        }
        return "".join(html_escape_table.get(c, c) for c in text)
    
    @staticmethod
    def preify(text):
        """ Wrap text in <pre></pre> construct. """
        return '<pre style="word-wrap: break-word;">%s</pre>' % text
    
    @staticmethod
    def wrap_styled_span(text, style):
        return """<span style=\"%s\">%s</span>""" % (text, style)
    
    @staticmethod
    def prepend_error_label(text):
        """ Prepend text with error label markup. """
        clr = os.environ.get('TM_SPHINX_DOC_COLOR_ERRORS', "red")
        return '''<span style="color: red;">Error:&nbsp;</span>%s''' % text
    
    @staticmethod
    def nl_to_br(text):
        """ Replace newlines with <br>. """
        return text.replace('\n', '<br>')
    
    @staticmethod      
    def refresh_document():
        """ Refresh the current TextMate document. """
        return os.system("arch -i386 osascript -e 'tell app \"System Events\" to activate' -e 'tell app \"TextMate\" to activate'")
    
    @staticmethod
    def current_dir():
        """ Return the name of the currect TextMate directory. """
        try:
            curdir = os.environ.get('TM_PROJECT_DIRECTORY', os.environ.get('TM_DIRECTORY'))
            if os.path.exists(curdir):
                result = os.path.basename(curdir)
            else:
                result = None
            return result
        except Exception as e:
            return None
    
    @staticmethod
    def current_text(always=False):
        """ Return the currently selected text or the current line as fallback. 
        
        If always is True, return 'Nothing selected' instead of None. 
        """
        if always:
            default = "Nothing selected"
        else:
            default = None
        return os.environ.get('TM_SELECTED_TEXT', os.environ.get('TM_CURRENT_LINE', os.environ.get('TM_CURRENT_WORD', default)))
    
    @staticmethod
    def current_word(always=False):
        """ Return the currently selected text or the current word as fallback. 
        
        If always is True, return 'Nothing selected' instead of None. 
        """
        if always:
            default = "Nothing selected"
        else:
            default = None
        return os.environ.get('TM_SELECTED_TEXT', os.environ.get('TM_CURRENT_WORD', default))
    
    @staticmethod
    def get_conf_value(val, basedir, default=None, confname="conf.py"):
        """ Return the python value of conf.py or optionally a default if val is absent from conf.py """
        
        result = None
        conf_path = "%s/%s" % (basedir, confname)
        
        if not os.path.exists(conf_path):
            raise OSError("config file doesn't exist at %s" % conf_path)
            
        exec(compile(open(conf_path).read(), conf_path, 'exec'))
        lcls = locals()
        
        if val in lcls:
            result = lcls[val]
            
        return result
    
    @staticmethod
    def compile_support_files(quiet=True):
        """ Runs compileall.compile_dir for the TM_BUNDLE_SUPPORT directory. """
        return compileall.compile_dir(os.environ["TM_BUNDLE_SUPPORT"], quiet=True)
    


# class SphinxDocErrorParser(object):
#     """ Parses system and error messages from sphinx-build and docutils output. """
#     def __init__(self, tool="sphinx-build", verbose=True, header=True, footer=True):
#         super(SphinxDocErrorParser, self).__init__()
#         self.tool = tool
#         self.verbose = verbose
#         self.header = header
#         self.footer = footer
#         self.local = false  # report errors locally on a per-file basis,
#                             # or globally on a per-project basis?
        
def main(argv=None):
    """ Command line args and test runs. """
    try:
        if argv == None:
            argv = sys.argv[1:]
        text = ".. moduleauthor:: André Berg <andre.bergmedia@googlemail.com>"
        print(SphinxDocUtils.url_esc(text))
        print(SphinxDocUtils.html_esc(text))
        #print(SphinxDocUtils.refresh_document())
        print(SphinxDocUtils.preify(text))
        print(SphinxDocUtils.prepend_error_label(text))
        print(SphinxDocUtils.nl_to_br(text))
        print(SphinxDocUtils.current_dir())
        print(SphinxDocUtils.current_text())
        print(SphinxDocUtils.compile_support_files())
    except KeyboardInterrupt:
        print("Interrupted.")      
    return 0

if __name__ == '__main__':
    sys.exit(main())
    