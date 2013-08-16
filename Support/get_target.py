##!/usr/bin/env python
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
#  in the Sphinx build dir. By default the script will 
#  look for a file that has the same name as the current
#  file in the editor (minus the file extension).
#  
#  Updated: 2012-08-17
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
from sphinxdoc import SphinxDocUtils as utils
from sphinxdoc import EXIT_SHOW_HTML


def print_error(err):
    utils.print_error(utils.format_error_as_html(err, sys.argv[0]))
    
def main(argv=None):
    
    program_name = sys.argv[0].split("/")[-1]
    program_version = "v0.2"
    program_build_date = "2012-08-17"
    
    version_message = '%%prog %s (%s)' % (program_version, program_build_date)
    help_message = '''\
%s is a script which can be used to get the path to a generated file 
in the Sphinx build dir. The script will look for a file that has the same name
as the current file in the editor minus the extension and a file extension that
reflects the mode (by default .html) passed with the --mode option.''' % program_name
    program_license = b"Copyright 2010 Andr\xe9 Berg (Berg Media)                                            \
                Licensed under the MIT License\nwww.opensource.org/licenses/miprogram_licensese.php".decode('latin-1')
    
    # -------- Handle Options ---------
    
    if argv is None:
        argv = sys.argv[1:]
    try:
        # setup option parser
        parser = OptionParser(version=version_message, epilog=help_message, description=program_license)
        parser.add_option("-c", "--conffilename", dest="conf_filename", help="name of the Sphinx config file [default: %default]", metavar="STR")
        parser.add_option("-b", "--builddirname", dest="build_dirname", help="name of the Sphinx build folder [default: %default]", metavar="STR")
        parser.add_option("-B", "--builddir", dest="build_dir", help="path to the Sphinx build folder [default: %default]", metavar="STR")
        parser.add_option("-C", "--confdir", dest="conf_dir", help="path to directory containing Sphinx config file [default: %default]", metavar="STR")
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
                
        if opts.conf_dir:
            conf_dir = opts.conf_dir
        else:
            conf_dir = utils.read_value_from_registry("conf_dir")
        if opts.conf_filename:
            conf_filename = opts.conf_filename
        else:
            conf_filename = utils.read_value_from_registry("conf_filename")
        if opts.build_dirname:
            build_dirname = opts.build_dirname
        else:
            build_dirname = utils.read_value_from_registry("build_dirname")
        if opts.build_dir:
            build_dir = opts.build_dir
        else:
            build_dir = utils.read_value_from_registry("build_dir")
        mode = opts.mode
        
        # since we need to support passing nothing for mode
        # we prepend the path sep ourselves so embedding it 
        # later in a format string doesn't contain a stray sep
        if opts.mode:
            mode = os.path.sep + opts.mode
        else:
            mode = ""
        
        # since we only support the HTML builder for now
        # this check is redundant
        if mode == "html":
            ext = "html"
        else:
            # default
            ext = "html"
        
        tmdir = args[0]
        tmfile = args[1]
        
        if conf_dir is None:
            conf_dir = tmdir
        
        config_filepath = "%s/%s" % (conf_dir, conf_filename)        
        
        if not os.path.exists(config_filepath):
            raise OSError("config file doesn't exist at %s" % config_filepath)
    
    except Exception as ex:
        exmsg = str(ex)
        if exmsg.find("config file doesn't exist") > -1:
            print_error([exmsg, "You can also set `TM_SHPINX_CONF_DIR` to point to the parent dir of the config file."])
        else:
            print_error(exmsg)
        return 2
    
    # -------- Source Config File ---------
    
    #try:
    #    
    #    # change directory to config file directory so that relative paths work
    #    saved_dir = os.path.abspath(os.curdir)
    #    os.chdir(conf_dir)
    #    
    #    # Here we take advatange of the fact that a Sphinx config files must 
    #    # be valid Python code and compile the config file as a Python source.
    #    # This will make it so we can access any 'setting = value' assignments
    #    # as if they were local variables of _this_ source file
    #    exec(compile(codecs.open(config_filepath).read(), config_filepath, 'exec'))
    #    # TODO: decouple the above exec call into its own method that both get_target.py and SphinxDocUtils.get_conf_value() use.
    #    # This has the advantage of maintaining in one location and depending on 
    #    # support in earlier Python versions could make use of elegant language
    #    # features such as the with dir contstruct so that changing the current
    #    # dir and changing back can be handled automatically. 
    #
    #    # change back to saved dir
    #    os.chdir(saved_dir)
    #    
    #except Exception as ex:
    #    print_error([str(ex), "", 
    #        "This error was caught while digesting the project's config file", 
    #        "for path lookups utilized by the Sphinx Doc bundle itself.", 
    #        "It can be ignored in most cases."
    #    ])
    
    # -------- Determine Target  ---------
    
    try:
        master_doc = utils.get_conf_value('master_doc', config_filepath, default="index")
        
        (unused_dirname, basename) = os.path.split(tmfile)      # IGNORE:W0612
        (filename, unused_fileext) = os.path.splitext(basename) # IGNORE:W0612
        
        # FIXME: dont't assume build dir is always contained by basedir
        # replace '%(basedir)s/%(build_dirname)s%(mode)s' with an abspath 
        # to a 'target' dir that will be passed as argument to this CLI script
        # this will actually make this script useful in optimizing lookup times
        # by using this script instead of the brute-force file-walking methods 
        # in SphinxDocUtils to find a dir or file. 
        #target = "%(basedir)s/%(build_dirname)s%(mode)s/%(filename)s.%(fileext)s" % \
        #{'basedir': tmdir, 'build_dirname': build_dirname, 'mode': mode, 'filename': filename, 'fileext': ext}
        target = "%(build_dir)s%(mode)s/%(filename)s.%(fileext)s" % \
                  {'build_dir': build_dir, 'mode': mode, 'filename': filename, 'fileext': ext}
        
        if not os.path.exists(target):
            #target = "%(basedir)s/%(build_dirname)s%(mode)s/%(filename)s.%(fileext)s" % \
            #{'basedir': tmdir, 'build_dirname': build_dirname, 'mode': mode, 'filename': master_doc, 'fileext': ext}
            target = "%(build_dir)s%(mode)s/%(filename)s.%(fileext)s" % \
                      {'build_dir': build_dir, 'mode': mode, 'filename': master_doc, 'fileext': ext}
        
        print(target.strip())
        
        return 0
    
    except Exception as ex:
        print_error(str(ex))
        return EXIT_SHOW_HTML

if __name__ == '__main__':
    if DEBUG:
        #sys.argv.append("-h")
        sys.argv.append("/Users/andre/Documents/Aptana Studio 2.0/Workspaces/Python/File Sequence Checker/doc/sphinx") # tmdir
        sys.argv.append("/Users/andre/Documents/Aptana Studio 2.0/Workspaces/Python/File Sequence Checker/doc/sphinx/checkfileseq.rst") # tmfile
    sys.exit(main())