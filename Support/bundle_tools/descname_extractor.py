#!/usr/local/bin/python2.7
# -*- coding: utf-8 -*-
# 
#  descname_extractor.py
#  SphinxDoc.tmbundle
#  
#  Created by André Berg on 2010-12-22.
#  Copyright 2010 Berg Media. All rights reserved.
#
'''
descname_extractor.py -- build word list out of names extracted from sphinx homepage files

descname_extractor eases the creation of word lists from 
HTML files found at the Sphinx homepage. These word lists 
can then be used for bundle completions. 

The modus operandi is very simple:

    given a regex

    1. parse HTML file, 
    2. extract matched regex groups, 
    3. construct list, 
    4. sort and uniq list 
    5. write repr of list and additional info to stdout or outfile

@author:     André Berg
             
@copyright:  2010 Berg Media. All rights reserved.
             
@license:    Licensed under the Apache License, Version 2.0 (the "License");\n
             you may not use this file except in compliance with the License.
             You may obtain a copy of the License at
             
             U{http://www.apache.org/licenses/LICENSE-2.0}
             
             Unless required by applicable law or agreed to in writing, software
             distributed under the License is distributed on an B{"AS IS"} B{BASIS},
             B{WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND}, either express or implied.
             See the License for the specific language governing permissions and
             limitations under the License.

@contact:    andre.bergmedia@googlemail.com
@deffield    updated: Updated
'''


import sys
import os
import re

from re import error
from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter

__all__ = []
__version__ = 0.1
__date__ = '2010-12-22'
__updated__ = '2010-12-22'

DEBUG = 1
TESTRUN = 0
PROFILE = 0

class CLIError(Exception):
    '''Generic exception to raise and log different fatal errors.'''
    def __init__(self, msg):
        super(CLIError).__init__(type(self))
        self.msg = u"E: %s" % msg
    def __str__(self):
        return self.msg
    def __unicode__(self):
        return self.msg

def main(argv=None):
    '''Command line options.'''
    if argv is None:
        argv = sys.argv
    else:
        sys.argv.extend(argv)
        
    program_name = "descname_extractor.py" # IGNORE:W0612 @UnusedVariable
    program_version = "v%s" % __version__
    program_build_date = str(__updated__)
    program_version_message = '%%(prog)s %s (%s)' % (program_version, program_build_date)
    program_shortdesc = '''descname_extractor.py -- build word list out of names extracted from sphinx homepage files'''
    program_license = u'''%s
        
  Created by André Berg on %s.
  Copyright 2010 Berg Media. All rights reserved.
  
  Licensed under the Apache License 2.0
  http://www.apache.org/licenses/LICENSE-2.0
  
  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied.
  
USAGE
''' % (program_shortdesc, str(__date__))        
    try:
        # Setup argument parser
        parser = ArgumentParser(description=program_license, formatter_class=RawDescriptionHelpFormatter)
        parser.add_argument('-V', '--version', action='version', version=program_version_message)
        parser.add_argument('-o', '--outfile', dest='outfile', help="location of a file to save the results or 'mangled' to produce a file name from the infile name [default: %(default)s]", metavar="PATH")
        parser.add_argument(dest="regex", help="a regular expression the groups of which should capture the words to include in the output. NB: don't forget to wrap in quotes. [default: %(default)s]", metavar="RE")
        parser.add_argument(dest="infiles", help="the file(s) to process [default: %(default)s]", metavar="FILE", nargs='+')
        
        # Process arguments
        args = parser.parse_args()
        
        regex = args.regex
        infiles = args.infiles
        outfile = args.outfile
        
        try:
            regex = re.compile(regex)
        except error as e:
            raise CLIError('regex pattern invalid: %s' % e)
        
        for inpath in infiles:
            if os.path.exists(inpath):
                f = open(inpath, "r")
                try:
                    file_contents = f.read()
                    found_items = re.findall(regex, file_contents)
                finally:
                    f.close()
                if len(found_items) > 0:
                    try:
                        found_items = sorted(set(found_items))
                    except:
                        # might be needed because the above method
                        # doesn't work for non-hashable types and
                        # we don't know what structures the capture
                        # groups return.
                        import itertools, operator # IGNORE:W0702
                        def sort_uniq(sequence):
                            """Sort and uniq-ify sequence.
                            This version is save in that it may take non-hashable object types.
                            
                            @param sequence: the sequence object to process
                            @type sequence: C{iterable}
                            @return: iterator over the sorted and uniq-ified sequence
                            @rtype: C{iterator}
                            """
                            return itertools.imap(
                                operator.itemgetter(0),
                                itertools.groupby(sorted(sequence)))
                        
                        found_items = list(sort_uniq(found_items))
                        
                    outtext = "File %s:\n" % inpath
                    outtext += "%d results for %r\n\n" % (len(found_items), regex.pattern)
                    outtext += repr(found_items)
                    outtext += "\n\n"
                    outtext += "\n".join(found_items)
                    
                    if outfile:
                        if outfile == 'mangled':
                            outfile = inpath.replace('.', '_')
                            outfile += '_values.txt'                          
                        o = open(outfile, "w")
                        try:
                            o.write(outtext)
                        finally:
                            o.close()
                    else:
                        print outtext
                else:
                    print "Nothing found for %r." % regex.pattern
        return 0
    except KeyboardInterrupt:
        return 0
    except Exception, e:
        if DEBUG or TESTRUN:
            raise(e)
        print >> sys.stderr, sys.argv[0].split("/")[-1] + ": " + unicode(e).decode('unicode_escape')
        print >> sys.stderr, "\t for help use --help"
        return 2

if __name__ == '__main__':
    if DEBUG:
        #sys.argv.append("-h")
        #sys.argv.append("--outfile=mangled")
        sys.argv.append(r'<tt class="descname">(.*?)</tt>')
        sys.argv.append("config.html")
    if TESTRUN:
        import doctest
        doctest.testmod()
    if PROFILE:
        import cProfile
        import pstats
        sys.argv.append(r'<tt class="descname">(.*?)</tt>')
        sys.argv.append("config.html")
        profile_filename = 'descname_extractor_profile.txt'
        cProfile.run('main()', profile_filename)
        statsfile = open("profile_stats.txt", "wb")
        p = pstats.Stats(profile_filename, stream=statsfile)
        stats = p.strip_dirs().sort_stats('cumulative')
        print >> statsfile, stats.print_stats()
        statsfile.close()
        sys.exit(0)
    sys.exit(main())
