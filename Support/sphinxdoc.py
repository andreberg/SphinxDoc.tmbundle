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
#  whole bundle.
#
# pylint: disable-msg=E1101

import sys
import os
import re
import compileall
import subprocess
import codecs
import shlex
import warnings
from contextlib import contextmanager
from functools import wraps

import ConfigParser
from debug import FuncTracerFilter

if ("%x" % sys.hexversion)[0] == '3':
    # pylint: disable=E0611,F0401
    import urllib.parse #@UnresolvedImport
    # pylint: enable=E0611,F0401
else:
    import urllib #@Reimport

from subprocess import Popen, PIPE

DEBUG = 0

if DEBUG:
    debug_curdir = "/Users/andre/source/OpenCV-2.4.2"
    debug_projdir = "/Users/andre/source/OpenCV-2.4.2" 
    debug_bundle_support = (os.path.expandvars("$HOME") + "/Library/Application Support/TextMate/Bundles/SphinxDoc.tmbundle/Support")
    os.environ['TM_BUNDLE_SUPPORT'] = debug_bundle_support
    os.environ['TM_DIRECTORY'] = debug_curdir
    os.environ['TM_PROJECT_DIRECTORY'] = debug_projdir
    print('W: DEBUG is enabled. Emulating TM env vars...')
    print("Setting TM_BUNDLE_SUPPORT to '{0}'".format(debug_bundle_support))
    print("Setting TM_DIRECTORY to '{0}'".format(debug_curdir))
    print("Setting TM_PROJECT_DIRECTORY to '{0}'".format(debug_projdir))

    
# -------- Module Variables ---------

REGISTRY_FILE_PATH = "/tmp/tm_sphinx_doc_registry.txt"

EXIT_DISCARD = 200
EXIT_REPLACE_TEXT = 201
EXIT_REPLACE_DOCUMENT = 202
EXIT_INSERT_TEXT = 203
EXIT_INSERT_SNIPPET = 204
EXIT_SHOW_HTML = 205
EXIT_SHOW_TOOL_TIP = 206
EXIT_CREATE_NEW_DOCUMENT = 207

DEFAULT_FILE_EXCLUDES = [
    '.DS_Store', 
    '.Trash', 
    '.Trashes', 
    '.fseventsd', 
    '.Spotlight-V100', 
    '.hotfiles.btree'
]

DEFAULT_DIR_EXCLUDES = ['.svn', '.git', '.hg', 'CVS']

# http or https schemes only
HTTP_URL_REGEX = r'''
\b
(                       # Capture 1: entire matched URL
  (?:
    https?://               # http or https protocol
    |                       #   or
    www\d{0,3}[.]           # "www.", "www1.", "www2." … "www999."
    |                           #   or
    [a-z0-9.\-]+[.][a-z]{2,4}/  # looks like domain name followed by a slash
  )
  (?:                       # One or more:
    [^\s()<>]+                  # Run of non-space, non-()<>
    |                           #   or
    \(([^\s()<>]+|(\([^\s()<>]+\)))*\)  # balanced parens, up to 2 levels
  )+
  (?:                       # End with:
    \(([^\s()<>]+|(\([^\s()<>]+\)))*\)  # balanced parens, up to 2 levels
    |                           #   or
    [^\s`!()\[\]{};:'".,<>?«»“”‘’]      # not a space or one of these punct chars
  )
)
'''
# lenient version, matches any scheme (existing or otherwise)
URL_REGEX = r''' 
\b
(                           # Capture 1: entire matched URL
  (?:
    [a-z][\w-]+:                # URL protocol and colon
    (?:
      /{1,3}                        # 1-3 slashes
      |                             #   or
      [a-z0-9%]                     # Single letter or digit or '%'
                                    # (Trying not to match e.g. "URI::Escape")
    )
    |                           #   or
    www\d{0,3}[.]               # "www.", "www1.", "www2." … "www999."
    |                           #   or
    [a-z0-9.\-]+[.][a-z]{2,4}/  # looks like domain name followed by a slash
  )
  (?:                           # One or more:
    [^\s()<>]+                      # Run of non-space, non-()<>
    |                               #   or
    \(([^\s()<>]+|(\([^\s()<>]+\)))*\)  # balanced parens, up to 2 levels
  )+
  (?:                           # End with:
    \(([^\s()<>]+|(\([^\s()<>]+\)))*\)  # balanced parens, up to 2 levels
    |                                   #   or
    [^\s`!()\[\]{};:'".,<>?«»“”‘’]        # not a space or one of these punct chars
  )
)
'''


__all__ = [ 
    EXIT_DISCARD, 
    EXIT_REPLACE_TEXT, 
    EXIT_REPLACE_DOCUMENT, 
    EXIT_INSERT_TEXT, 
    EXIT_INSERT_SNIPPET, 
    EXIT_SHOW_HTML, 
    EXIT_SHOW_TOOL_TIP, 
    EXIT_CREATE_NEW_DOCUMENT,
    DEFAULT_FILE_EXCLUDES,
    DEFAULT_DIR_EXCLUDES,
    URL_REGEX,
    HTTP_URL_REGEX,
    REGISTRY_FILE_PATH
]

# -------- Decorators ---------

def deprecated(level=2, since=None, info=None):
    """This decorator can be used to mark functions as deprecated.
        
    @param level: severity level. 
                  0 = warnings.warn(category=DeprecationWarning)
                  1 = warnings.warn_explicit(category=DeprecationWarning)
                  2 = raise DeprecationWarning()
    @type level: C{int}
    @param since: the version where deprecation was introduced.
    @type since: C{string} or C{int}
    @param info: additional info. normally used to refer to the new 
                 function now favored in place of the deprecated one.
    @type info: C{string}
    """
    def __decorate(func):
        if since is None:
            msg = 'Method %s() is deprecated.' % func.__name__
        else:
            msg = 'Method %s() has been deprecated since version %s.' % (func.__name__, str(since))
        if info:
            msg += ' ' + info
        @wraps(func)
        def __wrapped(*args, **kwargs): # IGNORE:C0111
            if level <= 0:
                warnings.warn(msg, category=DeprecationWarning, stacklevel=2)
                func(*args, **kwargs)
            elif level == 1:
                warnings.warn_explicit(msg, category=DeprecationWarning, 
                                       filename=func.func_code.co_filename, 
                                       lineno=func.func_code.co_firstlineno + 1)
            elif level >= 2:
                raise DeprecationWarning(msg)
        return __wrapped
    return __decorate

# -------- Context Managers ---------

# taken from grizzled-python lib
# see: http://software.clapper.org/grizzled-python/epydoc/grizzled.os-module.html#working_directory
# BSD license
@contextmanager
def working_directory(directory):
    """
    This function is intended to be used as a ``with`` statement context
    manager. It allows you to replace code like this:

    .. python::

        original_directory = _os.getcwd()
        try:
            os.chdir(some_dir)
            ... bunch of code ...
        finally:
            os.chdir(original_directory)

    with something simpler:

    .. python ::

        from __future__ import with_statement
        from sphinxdoc import working_directory

        with working_directory(some_dir):
            ... bunch of code ...

    :Parameters:
        directory : str
            directory in which to execute

    :return: yields the ``directory`` parameter
    """
    original_directory = os.getcwd()
    try:
        os.chdir(directory)
        yield directory
    finally:
        os.chdir(original_directory)
# end: taken from grizzled-python lib

# -------- Functions ---------
        
# -------- Classes ---------

class SphinxDocUtils(object):
    """Handy utilities and reusable components."""
    
    @staticmethod
    def extract_url(text, strict=False):
        if not strict:
            mat = re.match(URL_REGEX, text, re.UNICODE | re.VERBOSE)
            if mat:
                url = mat.group(1)
                return url
        else:
            mat = re.match(HTTP_URL_REGEX, text, re.UNICODE | re.VERBOSE)
            if mat:
                url = mat.group(1)
                return url
        return None
    
    @staticmethod
    def contains_url(text, strict=False):
        '''Return True if text contains an URL.
        
        Uses re.search. If strict is True, urls
        are valid only if they have http or https 
        as their I{scheme}.
        '''
        result = False
        if not strict:
            if re.search(URL_REGEX, text, re.UNICODE | re.VERBOSE):
                result = True
        else:
            if re.search(HTTP_URL_REGEX, text, re.UNICODE | re.VERBOSE):
                result = True
        return result

    @staticmethod
    def is_url(text, strict=False):
        '''Return True if text is an URL.
        
        Uses re.match. If strict is True, urls
        are valid only if they have http or https 
        as their I{scheme}.
        '''
        result = False
        if not strict:
            if re.match(URL_REGEX, text, re.UNICODE | re.VERBOSE):
                result = True
        else:
            if re.match(HTTP_URL_REGEX, text, re.UNICODE | re.VERBOSE):
                result = True
        return result
    
    @staticmethod
    def is_rel_path(apath):
        '''Return True if apath is a relative path.
        
        A path is considered relative if it contains '..' 
        or if C{os.path.isabs()} returns C{False}.
        '''
        no_rel_operator = ((apath.find("..") == -1) and (apath.find('./') == -1))
        is_abs = os.path.isabs(apath)
        return not (is_abs and no_rel_operator)
    
    @staticmethod
    def is_text_based_file(filepath):
        '''Return True, if C{/usr/bin/file} has C{text} in its output for filepath.'''
        # check if found_path is an ASCII file
        file_output = subprocess.check_output(["/usr/bin/file", "-b", filepath])
        file_output = file_output.strip() # IGNORE:E1103
        result = False
        if DEBUG:
            print "filepath = %s" % filepath
            print "file_output = %s" % file_output
        if file_output.find("text") > -1:
            result = True
        return result

    @staticmethod
    def make_locations_searched_message(target_filename, locations, relative=False, curdir=None, indent=4, display_limit=10):
        '''
        Construct a end user display message of locations 
        that were searched when trying to find a specific file.
        
        @param target_filename: name of the file that was searched for.
        @type target_filename: C{string}
        @param locations: list of paths that were visited during search.
        @type locations: C{list<string>}
        @param curdir: the path to the current directory. 
            Needed when relative is True.
        @type curdir: C{string}
        @param relative: if True, display paths as paths relative to curdir.
        @type relative: C{bool}
        @param indent: number of spaces to use for indentation.
        @type indent: C{int}
        @param display_limit: maximum number of paths to display.
            If there are more entries than this number 
            appends "..." as last line.
        @type display_limit: C{int}
        '''
        if len(locations) == 0:
            raise ValueError("locations can't be empty")
        target_filename = os.path.basename(target_filename)
        infomsg = "Nothing found for '%s'\n\n" % (target_filename)
        infomsg += "Locations searched:\n\n"
        indent_str = (" " * indent)
        i = 0
        for entry in locations:
            i += 1
            entry_str = entry
            if curdir and os.path.exists(curdir):
                # make entry a relative path to curdir
                if os.path.isabs(entry) and relative:
                    entry_str = os.path.relpath(entry, os.path.abspath(curdir))
            if i < display_limit:
                infomsg += indent_str + entry_str + "\n"
            else:
                infomsg += indent_str + "...\n"
                infomsg += indent_str + "(%d directories not shown)" % (len(locations) - display_limit) 
                break
        return infomsg

    
    @staticmethod
    def find_file(target_filename, source_dirs, # IGNORE:W0102
                  exclude_dirs=DEFAULT_DIR_EXCLUDES,   
                  exclude_files=DEFAULT_FILE_EXCLUDES): 
        '''
        Find a file by walking a set of source directories. 
                
        @param target_filename: the name of the file to find.
        @type target_filename: C{string}
        @param source_dirs: a list of file paths to walk 
        @type source_dirs: C{list<string>}
        @param exclude_dirs: skip over these directories
        @type exclude_dirs: C{list<string>}
        @param exclude_files: skip over these files
        @type exclude_files: C{list<string>}
        @return: a tuple with the found file path (if any) 
            and a list of the searched_dirs file paths.
        @rtype: C{tuple<string or None, list<string>>}
        '''
        searched_dirs = []
        found_path = None
        # unique list with one caveat: the path with the highest length 
        # is the most important as it is most specific
        source_dirs = list(sorted(set(source_dirs[:]), key=len, reverse=True))
        for source_dir in source_dirs:
            for root, dirs, files in os.walk(os.path.abspath(source_dir)):
                if DEBUG > 1: print("root = %s, dirs = %s" % (root, dirs))
                for exclude_dir in exclude_dirs:
                    if exclude_dir in dirs:
                        if DEBUG > 1: print("Removing excluded dir '%s'" % exclude_dir)
                        dirs.remove(exclude_dir)
                searched_dirs.append(root)
                for f in files:
                    if f in exclude_files or f[0] == ".":
                        if DEBUG > 1: print("excluding file '%s'..." % f)
                        continue
                    #if DEBUG: print("f == %s" % f)
                    if f == target_filename:
                        found_path = os.path.join(root, target_filename)
                        break
                if found_path:
                    break
            if found_path:
                break
        return (found_path, searched_dirs)

    @staticmethod
    def find_dir(target_dirname, source_dirs, exclude_dirs=DEFAULT_DIR_EXCLUDES): # IGNORE:W0102 
        '''
        Find a file by walking a set of source directories. 
        Returns a tuple with the found file path (if any) 
        and a list of the searched file paths. 
        
        This method supports target_dirnames in the form 
        dir1/dir2/... e.g. it will only return a found path
        if one of the source dirs includes all subdirs within 
        dir1.
            
        @see: L{find_file()} for parameter info.
        '''
        searched = []
        found_path = None
        continue_search = True
        if os.sep in target_dirname:
            comps = target_dirname.split(os.path.sep)
        else:
            comps = [target_dirname]
        num_hits_needed = len(comps)
        cur_hit_num = 0
        found_root = None
        found_path_comps = []
        # unique list with one caveat: the path with the highest length 
        # is the most important as it is most specific
        source_dirs = list(sorted(set(source_dirs[:]), key=len, reverse=True))
        for source_dir in source_dirs:
            for root, dirs, files in os.walk(os.path.abspath(source_dir)): #@UnusedVariable IGNORE:W0612
                if DEBUG > 1: print("root = %s, dirs = %s" % (root, dirs))
                for exclude_dir in exclude_dirs:
                    if exclude_dir in dirs:
                        if DEBUG > 1: print("Removing excluded dir '%s'" % exclude_dir)
                        dirs.remove(exclude_dir)
                root_base = os.path.basename(root)
                if root_base == comps[cur_hit_num]:
                    found_root = os.path.abspath(root)
                    found_path_comps.append(root_base)
                    cur_hit_num += 1
                else:
                    cur_hit_num = 0
                    found_root = None
                    found_path_comps = []
                    searched.append(root)
                if num_hits_needed == cur_hit_num:
                    continue_search = False
                    found_path = found_root
                    break
            if not continue_search:
                break
        return (found_path, searched)
    
    @staticmethod
    def system(cmd, shell=False, dryrun=False):
        '''
        Replacement for `cmd` statements.
        
        @param cmd: a list representing a shell command plus 
            arguments or a string representing just the shell 
            command without any arguments
        @type cmd: C{list} or C{string}
        @param shell: if True, cmd will be passed to a shell
            as script command, that is shell variables will 
            receive expansion starting with $0. Note that
            in that case the whole command incl arguments
            should be passed as one string.
        @type shell: C{bool}
   SphinxDocUtils@param dryrun: if True, print the Python command that 
            would be executed but do not actually execute it
        @type dryrun: C{bool}
 SphinxDocUtils  '''
        if isinstance(cmd, basestring):
            cmd = shlex.split(cmd)
        if dryrun:
            print "out, err = Popen(%s, stdout=PIPE, shell=%s).communicate()" % (cmd, str(shell))
            return (None, None)
        else:
            out, err = Popen(cmd, stdout=PIPE, shell=shell).communicate()
            return (out, err)

    @staticmethod
    def open(apath, app=None):
        if app:
            args = shlex.split('/usr/bin/open -a "%s" "%s"' % (app, apath))
        else:
            args = shlex.split('/usr/bin/open "%s"' % (apath))
        subprocess.call(args)


            
    @staticmethod
    def url_esc(url):
        if ("%x" % sys.hexversion)[0] == '3':
            result = urllib.parse.quote(url)
        else:
            result = urllib.quote(url)
        return result
    
    @staticmethod
    def err_msg_to_html(msg, filepath=None):
        indent = " " * len("Error: ")
        if filepath is not None and os.path.exists(filepath):
            file_link = SphinxDocUtils.convert_path_to_txmt_open_file_link(filepath)
            source_link = "\n\n%s(message originated in %s)" % (indent, file_link)
        else:
            source_link = ""
        errmsg = "%s%s" % (msg, source_link)
        errmsg = SphinxDocUtils.markup_to_html(errmsg)
        errmsg = SphinxDocUtils.prepend_error_label(errmsg)
        errmsg = SphinxDocUtils.preify(errmsg)
        return errmsg
        
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
        """Wrap text in <pre></pre> construct."""
        return '<pre style="word-wrap: break-word;">%s</pre>' % text
    
    @staticmethod
    def wrap_styled_span(text, style):
        return """<span style=\"%s\">%s</span>""" % (text, style)
    
    @staticmethod
    def prepend_error_label(text):
        """Prepend text with error label markup."""
        clr = os.environ.get('TM_SPHINX_DOC_COLOR_ERRORS', "red")
        return '''<span style="color: %s;">Error:&nbsp;</span>%s''' % (clr, text)
    
    @staticmethod
    def print_error(err):
        '''Print err to C{sys.stderr}'''
        sys.stderr.write(err)
    
    @staticmethod
    def nl_to_br(text):
        """Replace newlines with <br>."""
        return text.replace('\n', '<br>')
    
    @staticmethod
    def bt_to_code(text):
        """Replace backtick constructs with a <code></code> wrapper."""
        return re.sub(r'`{1,2}(.*?)`{1,2}', r'<code>\1</code>', text)
    
    @staticmethod
    def markup_to_html(text):
        """Replace lightweight markup constructs with their HTML counterparts."""
        result = text.replace('\n', '<br>')
        result = re.sub(r'`{1,2}(.*?)`{1,2}', r'<code>\1</code>', result)
        result = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', result)
        result = re.sub(r'\b[*_](.*?)[*_]\b', r'<i>\1</i>', result)
        result = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2">\1</a>', result)
        result = re.sub(r'<a href="(.*?)"></a>', r'<a href="\1">\1</a>', result) # fix empty links
        return result
    
    @staticmethod
    def convert_path_to_txmt_open_file_link(apath, label=None):
        """
        Create an HTML link for the txmt URL scheme so that 
        when clicked it will open apath in TextMate.
        """
        if os.path.exists(apath):
            if label == None:
                label = os.path.basename(apath)
            return "<a href=\"txmt://open/?url=file://%s\">%s</a>" % (SphinxDocUtils.url_esc(apath), label)
        else:
            return None
    
    @staticmethod      
    def refresh_document():
        """Refresh the current TextMate document."""
        return os.system("arch -i386 osascript -e 'tell app \"System Events\" to activate' -e 'tell app \"TextMate\" to activate'")

    @staticmethod
    def get_project_dir(strict=False):
        """
        Return path to TextMate's current project directory.
        
        Raise OSError if strict is True and finding the project 
        directory resulted in an exception.
        """
        result = None
        try:
            projdir = os.environ.get('TM_PROJECT_DIRECTORY')
            if os.path.exists(projdir) and os.path.isdir(projdir):
                result = projdir
            else:
                result = SphinxDocUtils.read_value_from_registry("project_dir", strict)
            return result
        except Exception: # IGNORE:W0703
            if strict:
                raise OSError("project directory couldn't be established")
            return None
    
    @staticmethod
    def get_current_dir(strict=False):
        """
        Return path to TextMate's current directory.
        
        Raise OSError if strict is True and finding the current
        directory resulted in an exception.
        """
        result = None
        try:
            curdir = os.environ.get('TM_DIRECTORY')
            if os.path.exists(curdir) and os.path.isdir(curdir):
                result = curdir
            elif not strict:
                result = SphinxDocUtils.read_value_from_registry("current_dir", strict)
            return result
        except Exception: # IGNORE:W0703
            if strict:
                raise OSError("current directory couldn't be established")
            return result
    
    @staticmethod
    def current_text(default="Nothing selected"):
        """Return the currently selected text or the current line as fallback."""
        return os.environ.get('TM_SELECTED_TEXT', 
                              os.environ.get('TM_CURRENT_LINE', 
                                             os.environ.get('TM_CURRENT_WORD', default)))
    
    @staticmethod
    def current_word(strict=False):
        """Return the currently selected text or the current word as fallback. 
        
        If strict is True, return 'Nothing selected' instead of None. 
        """
        if strict:
            default = "Nothing selected"
        else:
            default = None
        return os.environ.get('TM_SELECTED_TEXT', 
                              os.environ.get('TM_CURRENT_WORD', default))
    
    @staticmethod
    def find_config_dir(base_dirs=None):
        # TODO: implement find_config_dir()
        # 1. read value from registry
        # 2. do brute force file walk search if 1. failed.
        # If possible, return tuple (found, searched) like the other file walking based methods
        raise NotImplementedError("Not yet implemented")
    
    @staticmethod
    def find_config_file(base_dirs=None, targetname='conf.py'):
        """Find the absolute path to a config file named 'targetname'.
            
        Walks the file trees given by 'base_dirs', until 'targetname' is 
        found amongst the file contents of the currently examined directory.
            
        @param base_dirs: directories to search. If C{None}, use C{os.curdir} 
            and the current project dir (if it was read successfully from init.sh).
        @type base_dirs: C{list<string>}
        @param targetname: file name of the config file to be found.
        @type targetname: C{string}
        @return: path to the config file (if found) or None.
             Use os.path.dirname() on the found path as Sphinx 
             expects a config file directory.
        @rtype: C{string or None}
        @raise ValueError: if the file couldn't be found.
            The exception message includes a list of searched paths
            for end user display.
        """
        if os.environ.get('TM_SHPINX_CONF_DIR') is not None:
            candidate = os.environ['TM_SHPINX_CONF_DIR']
            if os.path.exists(candidate):
                return candidate
        if base_dirs is None:
            search_dirs = [os.curdir]
            project_dir = SphinxDocUtils.read_value_from_registry("project_dir")
            if project_dir:
                search_dirs.append(project_dir)
        else:
            search_dirs = base_dirs

        try_path = "%s/%s" % (base_dirs[0], targetname)
        
        if os.path.exists(try_path):
            found_path = try_path
        else:
            (found_path, searched_paths) = SphinxDocUtils.find_file(targetname, base_dirs) #@UnusedVariable
        
        if not found_path:
            msg = """a Sphinx config file is needed for this operation but wasn't found.
            
Are you running this command on a file that doesn't belong to a project?
Try opening the root folder of your documentation project with TextMate 
to make it a TextMate project. This will make the relative project structure 
clearer to SphinxDoc bundle and helps with commands that need to search specific
project locations. 
  

Locations searched: 

%s""" % (os.linesep.join(searched_paths))
            raise ValueError(msg)

        return found_path

    
    @staticmethod
    def get_conf_value(val, conf_filepath, default=None):
        """Return a value from Sphinx config file.
        
        To get a value from a generic config file (or settings file)
        as they are called elsewhere) use L{SphinxDocUtils.read_value_from_config_file()}.
        
        C{exec}s the file given by I{conf_filepath} and returns
        the python value for I{val} or a default value if I{val} 
        wasn't found in the config file.
        
        @param val: value or setting to find.
        @type val: C{string}
        @param conf_filepath: path to the config file.
        @type conf_filepath: C{string}
        @param default: L{default} value to return in case a config setting isn't found.
        @type default: C{string}
        @see: SphinxDocUtils.read_value_from_config_file()
        """
        result = None
        (dirname, unused_basename) = os.path.split(conf_filepath)      # IGNORE:W0612
        conf_dir = dirname
        if conf_filepath and os.path.isfile(conf_filepath):
            
            # change directory to config file directory so that 
            # relative paths in the config file work
            #saved_dir = os.path.abspath(os.curdir)
            #os.chdir(conf_dir)
            
            with working_directory(conf_dir):
                
                try:
                    # Here we take advatange of the fact that a Sphinx config files must 
                    # be valid Python code and compile the config file as a Python source.
                    # This will make it so we can access any 'setting = value' assignments
                    # as if they were local variables of _this_ source file
                    exec(compile(codecs.open(conf_filepath).read(), conf_filepath, 'exec')) # IGNORE:W0122
                
                except Exception as ex:
                    # TODO: add SphinxDoc bundle option for supressing errors emitted while parsing the sphinx conf file.
                    errmsg = [str(ex), "", 
                        "This error was caught while digesting the project's config file", 
                        "for lookups utilized by the Sphinx Doc bundle itself."
                    ]
                    SphinxDocUtils.print_error(SphinxDocUtils.format_error_as_html(errmsg, sys.argv[0]))
                #finally:
                #    # change back to saved dir
                #    os.chdir(saved_dir)
            
            # FIXME: look into alleviating side effects from overloading locals().
            # maybe try to save unaltered locals() and set them back after sourcing
            # via exec() above. Hopefully by doing this in a method changes will be 
            # restricted to the scope of this method. 
            lcls = locals()
            if val in lcls:
                result = lcls[val]
        if default and not result:
            return default
        return result
    
    @staticmethod
    def compile_support_files(quiet=True):
        """Runs compileall.compile_dir for the TM_BUNDLE_SUPPORT directory."""
        return compileall.compile_dir(os.environ["TM_BUNDLE_SUPPORT"], quiet=quiet)
    
    @staticmethod
    def expand_shell_variable(var):
        # FIXME: doesn't seem to support settings in the form "${variable1}/${variable2}"
        # I am not sure if just doing expansion this way works in all cases because
        # it should depend highly on the order of the execution chain, e.g.
        # TextMate menu command -> shell script command -> python script command and which
        # environment the subproccess inherits.
        # So for simple variables that mostly depend on environment variables set
        # by TextMate itself it might work but for composite variables (like the above)
        # this will most likely fail. 
        # Update: turns out, at least from outside the normal execution chain, i.e. when
        # debugging, only shell variables that have a default when they were defined
        # actually return the default as value, meaning the initializer was undefined.
        # e.g. ${var:-default} returns default not var.
        # Workarounds: 1) dump a config store file to $TEMP_DIR from shell land right after
        # init.sh has been run. Doesn't work for commands that don't call init.sh (ideally
        # there should be no such commands). Call this the "Registry".
        # 2) Try to do a "source init.sh" inside Popen? Seems a bit too hack-ish to me...  
        #    Nope. Tried. Doesn't work.
        """Expand a shell variable to its value representation.
        Returns a tuple (stdout, stderr) of which either, none or both can be None.
        """
        cmd = "%s" % var
        cmd = '"' + cmd.replace("'", "'\\''") + '"'
        p = Popen([r'/bin/sh -c "echo $0"', cmd], stdout=PIPE, stderr=PIPE, shell=True)
        out, err = p.communicate() # 0 = stdoutdata, 1 = stderrdata
        return (out, err)
    
    @staticmethod
    def read_value_from_shell_file(filepath, varname):
        """Parse file at C{filepath} and extract the value for a variable named C{varname}.
        
        Syntax present in file is excpected to be suitable for sourcing in a shell.
        
        Used for keeping up the idea of having all important variable names
        defined in one file which can be included at the beginning of each
        Shell based command that needs one or more of those variables.
            
        But sometimes we need one of those settings in Pythonland too.
            
        @param filepath: path to the file to parse.
        @type filepath: C{string}
        @param varname: the name of variable to look up. 
                        Must be defined as "^varname=<value>", 
                        where ^ beginning of a line and
                        where <value> may span multiple lines.
                        Tries to expand shell variables.
        @type varname: C{string}
        @return: the corresponding value string on success or the error 
                 message on failure.
        @rtype: C{string}
        """
        if not os.path.exists(filepath):
            return None
        pat = re.compile(r"^%s=(['\"])(?P<value>.*?)\1$" % varname, re.MULTILINE)
        value = None
        with open(filepath) as initsh:
            for line in initsh:
                mat = re.match(pat, line)
                if mat and mat.groupdict()['value'] is not None: 
                    value = mat.groupdict()['value']
                    out, err = SphinxDocUtils.expand_shell_variable(value)
                    if err:
                        return err.strip() # IGNORE:E1103
                    else:
                        return out.strip() # IGNORE:E1103
    
    
    @staticmethod
    def read_value_from_config_file(varname, section, filepath):
        """Read a value for variable C{varname} from a config file.
        
        The format of the config file must be readable by L{ConfigParser}.
        
        @param varname: the name of variable to look up. 
        @type varname: C{string}
        @param section: the section the variable resides in 
                        see ConfigParser docs for info.
        @type section: C{string}
        @param filepath: path to the config file
        @type filepath: C{string}
        """
        result = None
        if not os.path.exists(filepath):
            return None
        try: 
            config = ConfigParser.ConfigParser()
            config.readfp(codecs.open(filepath))
            result = config.get(section, varname)
            return result
        except Exception, e:
            print("Exception while parsing config file at path '{0!s}': {1!s}".format(filepath, str(e)))

    @staticmethod
    def read_value_from_registry(varname, section="Init", strict=True):
        """Read value for a variable C{varname} from the temporary registry file.
        
        @param varname: the name of variable to look up. 
        @type varname: C{string}
        @param section: the section name for varname.
                        see C{ConfigParser} docs for info.
        @type section: C{string}
        @param strict: if True, raise exceptions if a value for
                       varname can't be established.
        @type strict: C{boolean}
        @raise KeyError: if varname wasn't found in the registry.
        @raise OSError: if the registry file wasn't found. 
        """
        settingsfile = REGISTRY_FILE_PATH
        settingsfile_exists = os.path.exists(settingsfile)
        varname_value = None
        if settingsfile_exists:
            varname_value = SphinxDocUtils.read_value_from_config_file(varname, section, settingsfile)
            if strict is True and varname_value is None:
                raise KeyError("Variable %s wasn't found in the registry" % varname) 
        else:
            if strict is True: 
                raise OSError("E: Registry file not found at '{0!s}' (mode: strict)".format(settingsfile))
        return varname_value
    
    
    @staticmethod
    @deprecated(info="Use SphinxDocUtils.read_value_from_registry() instead.")
    def read_value_from_init_sh(varname):
        """Parse init.sh and extract the value for a variable named varname.
        
        @param varname: the name of variable to look up. 
                        Must be defined as "^varname=<value>", 
                        where ^ beginning of a line and
                        where <value> may span multiple lines.
        @type varname: C{string}
        @return: the corresponding value string on success or the error 
                 message on failure.
        @rtype: C{string}
        @see: SphinxDocUtils.read_value_from_shell_file()
        """
        initsh_path = "%s/init.sh" % os.environ.get('TM_BUNDLE_SUPPORT', os.curdir)
        if not os.path.exists(initsh_path):
            return None
        return SphinxDocUtils.read_value_from_shell_file(initsh_path, varname)
    
    @staticmethod
    def settings_file_exists():
        """Check if a SphinxDoc bundle settings file exists for the currently compiled project.
        
        To be clear a settings file should not be confused with Sphinx' config file.
        In fact it isn't used by Sphinx directly at all but rather allows per-project
        overwrites for settings like build and config dir paths for internal bundle
        routines like the build and preview commands.
        """
        settings_filepath = SphinxDocUtils.read_value_from_registry('txmt_settings_file')
        #print("settings_filepath = {0}".format(settings_filepath))
        if os.path.exists(settings_filepath):
            return True
        else:
            return False
        
    @staticmethod
    def format_error_as_html(msg, origin_path):
        """Format error messages as HTML for TextMate's Webpreview feature.
        
        @param msg: message string or list of messages to print. 
                    If the latter each string will be appended 
                    on a new line and indented.
        @type msg: C{string} or C{list<string>}
        @param origin_path: the path to the file where the error 
                            originated (usually C{sys.argv[0]}).
        @type origin_path: C{string}
        """
        messages = None
        if isinstance(msg, basestring):
            messages = [msg]
        elif isinstance(msg, list):
            messages = msg
        else:
            raise AttributeError("param 'msg' must be list or str")
        indent = " " * len("Error: ")
        filelink = SphinxDocUtils.convert_path_to_txmt_open_file_link(origin_path)
        errmsg = "%s" % (messages[0])
        if len(messages) > 1:
            messages = messages[1:]
            for m in messages:
                errmsg += "\n%s%s" % (indent, m)
        errmsg = "%s\n\n%s(message originated in %s)" % (errmsg, indent, filelink)
        errmsg = SphinxDocUtils.markup_to_html(errmsg)
        errmsg = SphinxDocUtils.prepend_error_label(errmsg)
        errmsg = SphinxDocUtils.preify(errmsg)
        return errmsg
    

def main(argv=None):
    """Command line args and test runs."""
    
    if argv == None:
        argv = sys.argv[1:]

    try:
        # IMPORTANT: as of 2012-08-19 init.sh settings
        # are read from the so called 'registry', a simple 
        # text file found at REGISTRY_FILE_PATH. This text
        # file however is created when building the current
        # project. This means you will need to build the
        # current project that is being debugged at least
        # once so this registry can be queried.  
        # The alternatives to using the registry file weren't
        # pretty since we have constant cross-reference of
        # what should be shared state between multiple shell
        # scripting languages (Shell, Python, Ruby)
        
        if DEBUG:
            from debug import FilteredFuncTracer
            tracer = FilteredFuncTracer(globals())
            filter = FuncTracerFilter(tracer)
            filter.customize(names=['extract_url'], events=['return'])
            tracer.set_filter(filter)
            tracer.enable()
            
        text = "http://stackoverflow.com/questions/4157170/maven-command-to-install-remote-dependency-locally"
        url = SphinxDocUtils.extract_url(text)
        print("url = %s" % url)
        
        # find file
        print("find file")
        target_filename = "index.html"
        curdir = SphinxDocUtils.get_current_dir()
        project_dir = SphinxDocUtils.get_project_dir()
        (found, searched) = SphinxDocUtils.find_file(target_filename, [curdir, project_dir])
        if found:
            print("file found = %s" % found)
        else:
            infomsg = SphinxDocUtils.make_locations_searched_message(target_filename, searched, curdir)
            print(infomsg)
        
        # find dir
        target_dirname = "_build"
        (found, searched) = SphinxDocUtils.find_dir(target_dirname, [curdir, project_dir])
        if found:
            print("build dir found = %s" % found)
        else:
            infomsg = SphinxDocUtils.make_locations_searched_message(target_dirname, searched, relative=True, curdir=curdir)
            print(infomsg)
            
        #found = SphinxDocUtils.find_config_dir([curdir, project_dir])
        #if found:
        #    print("config dir found = %s" % found)
        #else:
        #    infomsg = SphinxDocUtils.make_locations_searched_message(target_dirname, searched, relative=True, curdir=curdir)
        #    print(infomsg)

        text = ".. moduleauthor:: André Berg <andre.bergmedia@googlemail.com>"
        print("url escape = %s" % SphinxDocUtils.url_esc(text))
        print("html escape = %s" % SphinxDocUtils.html_esc(text))
        #print("refreshing textmate document = %s" % SphinxDocUtils.refresh_document())
        print("pre-ified text = %s" % SphinxDocUtils.preify(text))
        print("prepend error label  %s" % SphinxDocUtils.prepend_error_label(text))
        print("nl to br = %s" % SphinxDocUtils.nl_to_br(text))
        print("get current dir = %s" % SphinxDocUtils.get_current_dir())
        print("get project dir = %s" % SphinxDocUtils.get_project_dir(strict=True))
        print("current text = %s" % SphinxDocUtils.current_text())
        print("compiling support files = %s" % SphinxDocUtils.compile_support_files())
        print(SphinxDocUtils.read_value_from_init_sh("current_dir"))
        #print(SphinxDocUtils.read_value_from_init_sh("preferred_browser"))
        #print(SphinxDocUtils.read_value_from_init_sh("err_python_not_found_msg"))
        #print(SphinxDocUtils.find_config_dir("/Users/andre/source/OpenCV-2.4.2"))
        print("settings file exists = %s" % SphinxDocUtils.settings_file_exists())
        print("expanding shell variable = %s" % SphinxDocUtils.expand_shell_variable("txmt_settings_file"))
        print("read value 'python' from registry = %s" % SphinxDocUtils.read_value_from_registry("python", strict=True))
        print("read value 'err_python_modules_not_found' from registry = %s" % SphinxDocUtils.read_value_from_registry("err_python_modules_not_found", strict=True))

    except KeyboardInterrupt:
        print("Interrupted.")      
    return 0

if __name__ == '__main__':
    sys.exit(main())
    