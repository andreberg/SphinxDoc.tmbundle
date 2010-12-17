#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 
#  get_target.py
#  SphinxDoc.tmbundle
#  
#  Created by André Berg on 2010-12-14.
#  Copyright 2010 Berg Media. All rights reserved.
# 
#  Command line interface which can be used from shell
#  based commands to get the path to a generated file 
#  in the Sphinx build dir. The script will look for a 
#  file that has the same name as the current file in 
#  the editor (minus the file extension).
#

import sys
from optparse import OptionParser
import os

DEBUG = 0

def main(argv=None):
    
    program_name = sys.argv[0]
    program_version = "v0.1"
    program_build_date = "2010-12-04"

    version_message = '%%prog %s (%s)' % (program_version, program_build_date)
    help_message = '''\
%s is a script which can be used to get the path to a generated file 
in the Sphinx build dir. The script will look for a file that has the same name
as the current file in the editor minus the extension and a file extension that
reflects the mode (by default .html) passed with the --mode option.''' % program_name
    license = b"Copyright 2010 Andr\xe9 Berg (Berg Media)                                            \
                Licensed under the MIT License\nwww.opensource.org/licenses/mit-license.php".decode('latin-1')
                
    if argv is None:
        argv = sys.argv[1:]
    try:
        # setup option parser
        parser = OptionParser(version=version_message, epilog=help_message, description=license)
        parser.add_option("-c", "--conffilename", dest="conf_filename", help="name of the Sphinx config file [default: %default]", metavar="STR")
        parser.add_option("-b", "--builddirname", dest="build_dirname", help="name of the Sphinx build folder [default: %default]", metavar="STR")
        parser.add_option("-m", "--mode", dest="mode", help="build mode [default: %default]", metavar="STR")
        #parser.add_option("-v", "--verbose", dest="verbose", action="count", help="set verbosity level [default: %default]")
        
        parser.set_defaults(conf_filename="conf.py", build_dirname="_build")
        
        # process options
        (opts, args) = parser.parse_args(argv)
        
        # args should be:
        # 1. TM_DIRECTORY or TM_PROJECT_DIRECTORY - the folder of the current document (may not be set) or the top-level folder in the project drawer (may not be set).
        # 2. TM_FILEPATH - path (including file name) for the current document (may not be set).
        
        required_arglen = 2
        actual_arglen = len(args)
        
        if actual_arglen != required_arglen:
            parser.error("incorrect number of required arguments: need %i (tmdir, tmfile) but got %i\nargs = %s" % (required_arglen, len(args), args))  
        
        conf_filename = opts.conf_filename
        build_dirname = opts.build_dirname
        
        if opts.mode:
            mode = os.path.sep + opts.mode
        else:
            mode = ""
        
        if mode == "html":
            ext = "html"
        else:
            # default
            ext = "html"
        # TODO: add file extensions for other build modes 
        
        tmdir = args[0]
        tmfile = args[1]
        
        conf_path = "%s/%s" % (tmdir, conf_filename)
        
        #if DEBUG: print(conf_path)
        
        if not os.path.exists(conf_path):
            raise OSError("config file doesn't exist at %s" % conf_path)
            
        exec(compile(open(conf_path).read(), conf_path, 'exec'))
        
        if 'master_doc' in locals():
            pass
        else:
            # fall back
            master_doc = "index"

        (dirname, basename) = os.path.split(tmfile)
        (filename, fileext) = os.path.splitext(basename)
        
        target = "%(basedir)s/%(build_dirname)s%(mode)s/%(filename)s.%(fileext)s" % \
        {'basedir': tmdir, 'build_dirname': build_dirname, 'mode': mode, 'filename': filename, 'fileext': ext}
        
        if not os.path.exists(target):
            target = "%(basedir)s/%(build_dirname)s%(mode)s/%(filename)s.%(fileext)s" % \
            {'basedir': tmdir, 'build_dirname': build_dirname, 'mode': mode, 'filename': master_doc, 'fileext': ext}
        
        print(target.strip())
        
        return 0
        
    except Exception as e:
        sysv = ("%x" % sys.hexversion)
        if sysv[0] == '3':
            sys.stderr.write(sys.argv[0].split("/")[-1] + ": " + str(e))
            sys.stderr.write("\n%s  for help use --help" % (" " * len(sys.argv[0].split("/")[-1])))
        else:
            sys.stderr.write(sys.argv[0].split("/")[-1] + ": " + str(e).decode('unicode_escape'))
            sys.stderr.write("\n%s  for help use --help\n" % (" " * len(sys.argv[0].split("/")[-1])))
        return 2
    

if __name__ == '__main__':
    if DEBUG:
        #sys.argv.append("-h")
        sys.argv.append("/Users/andre/Documents/Aptana Studio 2.0/Workspaces/Python/File Sequence Checker/doc/sphinx") # tmdir
        sys.argv.append("/Users/andre/Documents/Aptana Studio 2.0/Workspaces/Python/File Sequence Checker/doc/sphinx/checkfileseq.rst") # tmfile
    sys.exit(main())