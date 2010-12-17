#!/usr/bin/env python
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

def main(argv=None):
    
    program_name = os.path.basename(sys.argv[0])
    program_version = "v0.1"
    program_build_date = "2010-12-04"

    version_message = '%%prog %s (%s)' % (program_version, program_build_date)
    help_message = '''\
%s is a script which can be used to get the value of a setting from Sphinx' config
file (conf.py by default).''' % program_name
    license = "Copyright 2010 Andr\xe9 Berg (Berg Media)                                            \
                Licensed under the MIT License\nwww.opensource.org/licenses/mit-license.php"
                
    if argv is None:
        argv = sys.argv[1:]
    try:
        # setup option parser
        parser = OptionParser(version=version_message, epilog=help_message, description=license)
        parser.add_option("-c", "--conffilename", dest="conf_filename", help="name of the Sphinx config file [default: %default]", metavar="STR")
        #parser.add_option("-v", "--verbose", dest="verbose", action="count", help="set verbosity level [default: %default]")
        
        parser.set_defaults(conf_filename="conf.py")
        
        # process options
        (opts, args) = parser.parse_args(argv)
        
        # args should be:
        # 1. TM_DIRECTORY or TM_PROJECT_DIRECTORY - the folder of the current document (may not be set) or the top-level folder in the project drawer (may not be set).
        # 2. OPTION_NAME  - the name of a setting from the Sphinx config file.
        
        required_arglen = 2
        actual_arglen = len(args)
        
        if actual_arglen != required_arglen:
            parser.error("incorrect number of required arguments: need %d (tmdir, option_name) but got %d\nargs = %s" % (required_arglen, actual_arglen, args))  
        
        conf_filename = opts.conf_filename
        
        tmdir = args[0]
        option_name = args[1]
        
        conf_path = "%s/%s" % (tmdir, conf_filename)
        
        #if DEBUG: print(conf_path)
        
        if not os.path.exists(conf_path):
            raise OSError("config file doesn't exist at %s" % conf_path)
        
        if ("%x" % sys.hexversion)[0] == '3':
            try:
                exec(compile(open(conf_path, encoding="utf-8").read(), conf_path, 'exec'))
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
        if ("%x" % sys.hexversion)[0] == '3':
            sys.stderr.write(sys.argv[0].split("/")[-1] + ": " + str(e))
            sys.stderr.write("\n%s  for help use --help" % (" " * len(sys.argv[0].split("/")[-1])))
        else:
            sys.stderr.write(sys.argv[0].split("/")[-1] + ": " + str(e).decode('unicode_escape'))
            sys.stderr.write("\n%s  for help use --help\n" % (" " * len(sys.argv[0].split("/")[-1])))
        # Python 2:
        # print >> sys.stderr, sys.argv[0].split(u"/")[-1] + u": " + unicode(e).decode('unicode_escape')
        # print >> sys.stderr, "\t for help use --help"
        # Python 3
        # print(sys.argv[0].split("/")[-1] + ": " + str(e).decode('unicode_escape'), file=sys.stderr)
        # print("\t for help use --help", file=sys.stderr)
        return 2
    

if __name__ == '__main__':
    if DEBUG:
        #sys.argv.append("-h")
        sys.argv.append("/Users/andre/Documents/Aptana Studio 2.0/Workspaces/Python/File Sequence Checker/doc/sphinx") # tmdir
        sys.argv.append("source_suffix")
        #sys.argv.append("/Users/andre/Documents/Aptana Studio 2.0/Workspaces/Python/File Sequence Checker/doc/sphinx/checkfileseq.rst") # tmfile
    sys.exit(main())