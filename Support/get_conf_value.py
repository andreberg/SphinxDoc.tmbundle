##!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
#  get_conf_value.py
#  SphinxDoc.tmlbundle
#  
#  Created by André Berg on 2010-12-14.
#  Copyright 2010 Berg Media. All rights reserved.
# 
#  This command line utility can be used to 
#  get the value of config settings from the 
#  current project's config file (conf.py).
#

import sys
import os
from optparse import OptionParser

DEBUG = 0

if DEBUG:
    tmbundlesup = os.path.expandvars("$HOME") + "/Library/Application Support/TextMate/Bundles/SphinxDoc.tmbundle/Support"
else:
    tmbundlesup = os.environ['TM_BUNDLE_SUPPORT']

sys.path.append(tmbundlesup)
from sphinxdoc import EXIT_SHOW_HTML
from sphinxdoc import SphinxDocUtils as utils


def print_error(err):
    html_errmsg = utils.format_error_as_html(err, sys.argv[0])
    sys.stderr.write(html_errmsg)

def main(argv=None):
    
    program_name = os.path.basename(sys.argv[0])
    program_version = "v0.1"
    program_build_date = "2010-12-04"

    version_message = '%%prog %s (%s)' % (program_version, program_build_date)
    help_message = '''\
%s is a script which can be used to get the value of a setting from Sphinx' config
file (conf.py by default).''' % program_name
    program_license = "Copyright 2010 André Berg (Berg Media)                                            \
                Licensed under the MIT License\nwww.opensource.org/licenses/miprogram_licensese.php"
    
    # -------- Handle Options ---------
             
    if argv is None:
        argv = sys.argv[1:]
    try:
        # setup option parser
        parser = OptionParser(version=version_message, epilog=help_message, description=program_license)
        parser.add_option("-c", "--conffilepath", dest="conf_filepath", help="path to the Sphinx config file [default: %default]", metavar="STR")
        #parser.add_option("-v", "--verbose", dest="verbose", action="count", help="set verbosity level [default: %default]")
        
        parser.set_defaults(conf_filepath="conf.py")
        
        # process options
        (opts, args) = parser.parse_args(argv)
        
        # args should be:
        # 1. OPTION_NAME  - the name of a setting from the Sphinx config file.
        
        required_arglen = 1
        actual_arglen = len(args)
        
        if actual_arglen != required_arglen:
            parser.error("incorrect number of required arguments: need %d (option_name) but got %d\nargs = %s" % (required_arglen, actual_arglen, args))  
        
        conf_filepath = opts.conf_filepath
        
        option_name = args[0]
        
        conf_path = conf_filepath
        
        #if DEBUG: print(conf_path)
        
        if not os.path.exists(conf_path):
            raise OSError("config file doesn't exist at %s" % conf_path)
        
        if ("%x" % sys.hexversion)[0] == '3':
            try:
                exec(compile(open(conf_path, encoding="utf-8").read(), conf_path, 'exec')) # IGNORE:W0122
            except SyntaxError:
                return 3
        else:
            execfile(conf_path)
            
        lcls = locals()
        
        if option_name in lcls:
            result = lcls[option_name]
            retval = 0
        else:
            result = "not found"
            retval = 1

        print(result.strip())
        
        return retval
        
    except Exception as e:
        indent = "       " # len("Error: ")
        exmsg = str(e)
        
        if exmsg.find("config file doesn't exist") > -1:
            exmsg += "\n%sYou can also set `TM_SHPINX_CONF_DIR` to point to the parent dir of the config file." % (indent)

        filelink = utils.convert_path_to_txmt_open_file_link(sys.argv[0])
        errmsg = "%s\n\n%s(message originated in %s)" % (exmsg, indent, filelink)
        errmsg = utils.markup_to_html(errmsg)
        errmsg = utils.prepend_error_label(errmsg)
        errmsg = utils.preify(errmsg)

        sys.stderr.write(errmsg)
        
        return EXIT_SHOW_HTML    

if __name__ == '__main__':
    if DEBUG:
        #sys.argv.append("-h")
        sys.argv.append("/Users/andre/Documents/Aptana Studio 2.0/Workspaces/Python/File Sequence Checker/doc/sphinxs") # tmdir
        sys.argv.append("source_suffix")
        #sys.argv.append("/Users/andre/Documents/Aptana Studio 2.0/Workspaces/Python/File Sequence Checker/doc/sphinx/checkfileseq.rst") # tmfile
    sys.exit(main())