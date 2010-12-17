#!/usr/bin/env ruby
# -*- coding: utf-8 -*-
# 
#  error_parser.rb
#  SphinxDoc.tmbundle
#  
#  Created by Andre Berg on 2010-12-07.
#  Copyright 2010 Berg Media. All rights reserved.
# 
#  Provides a command line abstraction to SphinxDoc
#  ::ErrorParser so that its functionality can be 
#  used easily from shell scripts.
#

$LOAD_PATH << "#{ENV["TM_BUNDLE_SUPPORT"]}"
begin
  require 'sphinxdoc'
rescue LoadError => e
  require "/Users/andre/Library/Application Support/TextMate/Bundles/Sphinx Doc.tmbundle/Support/sphinxdoc"
end

def main(args=nil)
  
  if args then
    _argv = args
  else
    _argv = ARGV
  end
  
  _argc = _argv.length
  
  if _argc == 1
    error_filepath = _argv[0]
    tm_filepath = nil
    command_name = nil
  elsif _argc == 2
    error_filepath = _argv[0]
    tm_filepath = _argv[1]
    command_name = nil
  elsif _argc == 3
    error_filepath = _argv[0]
    tm_filepath = _argv[1]
    command_name = _argv[2]
  else
    exit 1
  end

  if command_name
    ep = SphinxDoc::ErrorParser.new(tool=command_name)
  else
    ep = SphinxDoc::ErrorParser.new
  end
  
  if File.exists?(error_filepath) then
    if File.size(error_filepath) > 0 then
      result = ep.parse_error_file(error_filepath, tm_filepath)
      if result.class != TrueClass
        print result
      end
    end
  else
    result = ep.parse_errors(STDIN)
    if result.class != TrueClass
      print result
    end
  end
  
end

if $0 == __FILE__ then
  #main(["/tmp/tm_sphinx_doc_errors.txt", "sphinx-build"])
  main()
end
