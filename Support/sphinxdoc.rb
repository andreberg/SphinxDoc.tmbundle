#!/usr/bin/env ruby
# -*- coding: utf-8 -*-
# 
#  sphinxdoc.rb
#  SphinxDoc.tmbundle
#  
#  Created by Andre Berg on 2010-12-07.
#  Copyright 2010 Berg Media. All rights reserved.
# 
#  Description: 
#  Contains reusable modules and methods for the
#  whole bundle. Mirrored by the Python version 
#  sphinxdoc.py. The goal is to be as language
#  agnostic as possible.
#

DEBUG = 0

module SphinxDocUtils
   require 'uri'
   
   # mixins
   
   def url_esc(url)
      begin
         url.gsub(/[^a-zA-Z0-9.-\/]/) { |m| sprintf("%%%02X", m[0]) }
      rescue
         URI.escape(url)
      end
   end
   
   def html_esc(text)
      text.gsub(/&/, '&amp;').gsub(/</, '&lt;')
   end
   
   def preify(text)
    "<pre style=\"word-wrap: break-word;\">#{text}</pre>"
   end
   
   def prepend_error_label(text)
    "<span style=\"color: red;\">Error:&nbsp;</span>#{text}"
   end
   
   def wrap_styled_span(text, style)
    "<span style=\"#{style}\">#{text}</span>"
   end
   
   def nl_to_br(text)
      text.gsub(/\n/, '<br>')
   end
   
   # "static" methods
   
   def SphinxDocUtils.refresh_document
      `arch -i386 osascript -e 'tell app "System Events" to activate' -e 'tell app "TextMate" to activate'`
   end
   
   def SphinxDocUtils.current_dir
      begin
         result = File.basename(ENV['TM_PROJECT_DIRECTORY'] || ENV['TM_DIRECTORY'])
      rescue TypeError
         result = nil
      end
      return result
   end
   
   def SphinxDocUtils.current_text
      ENV['TM_SELECTED_TEXT'] || ENV['TM_CURRENT_LINE'] || ENV['TM_CURRENT_WORD'] || "Nothing selected"
   end
   
   def SphinxDocUtils.current_word
      ENV['TM_SELECTED_TEXT'] || ENV['TM_CURRENT_WORD'] || "Nothing selected"
   end
   
end


module SphinxDoc
   
   class ErrorParser
      include SphinxDocUtils
      
      @@error_format1 = /^(.*?):(\d*): \((.+?)\/(?:\d+)\) (.+)/ # for docutils, e.g. rst2html.py etc.
      @@error_format2 = /^(.*?):(\d*): (.+?):\s?(.*?)$/ # for sphinx-build
      #@@error_format3 = /^SystemMessage: (?<severity>\w+)\/(?<level>\d+) \((?<file>.+?), line (?<no>\d+?)\);$/ # unused
      @@no_err_messages = ["Making output directory..."] # these lines are not regarded as error
      @@no_err_regexes = [/^Exiting due to/] # lines matching these regexes are not regarded as error
      @@autodoc_errpath_format = /(\/.*\/)(.+?)(\..+?):.*/ # unused
      
      attr_reader :errcount
      
      def initialize(tool="sphinx-build", verbose=true, nodupe=true, header=true, footer=true)
         @tool = tool
         @verbose = verbose
         @nodupe = nodupe
         @header = header
         @footer = footer
         @errcount = 0
         @errcache = []
         @local = false # report errors locally on a per-file basis,
         # or globally on a per-project basis?
      end
      
      def label_color(severity)
         color = ENV['TM_SPHINX_DOC_COLOR_INFOS'] || "dodgerblue"
         case severity
            when "ERROR" then
            color = ENV['TM_SPHINX_DOC_COLOR_ERRORS'] || "red"
            when "SEVERE" then
            color = ENV['TM_SPHINX_DOC_COLOR_ERRORS'] || "red"
            when "WARNING" then
            color = ENV['TM_SPHINX_DOC_COLOR_WARNINGS'] || "orange"
            when "FILENAME" then
            color = ENV['TM_SPHINX_DOC_COLOR_FILENAMES'] || "#555"
         end
         color
      end
      
      def filter_errors(input, restrictor)
         # Add a trailing / because the last entry will not
         # be followed by a next file path.
         # Wo only need to do this when we are filtering 
         # the output to a specific file.
         
         # return true so validate_syntax.sh can put up a "Syntax OK" tool tip
         return true if input.size == 0
         input = input + "/"
         re = /(?:#{restrictor}):(?:\d*):(?:.*?)(?=^\/)/m
         m = input.scan(re)
         if m.length > 0 then
            puts "re1: found #{m.length} specifics for file '#{restrictor}'" if DEBUG > 0
            return m.join("\n")
         else
            re = /^#{restrictor}:.*?(?!#{restrictor})$/m
            m = input.scan(re)
            if m.length > 0 then
               puts "re2: found #{m.length} specifics for file '#{restrictor}'" if DEBUG > 0
               return m.join("\n")
            else
               re = /^#{restrictor}:.*$/
               m = input.scan(re)
               if m.length > 0 then
                  puts "re3: found #{m.length} specifics for file '#{restrictor}'" if DEBUG > 0
                  return m.join("\n")
               else
                  puts "no specifics found for file '#{restrictor}'" if DEBUG > 0
                  return input
               end
            end
         end
      end
      
      def parse_error_file(path, restrict=nil)
         # restrictor is the path to a an existing file 
         # the errors of which we are interested in only
         if File.exists? path then
            f = open(path)
            input = f.read()
            f.close()
            # if current_file, e.g. TM_CURRENT_FILE, is not nil, 
            # we are interested in the subset of errors spit out 
            # by sphinx-build that show errors from the file at 
            # the path passed in with current_file. 
            # To blend out all other errors we apply two regex tries 
            # and fall back to showing all errors if those are unsuccessful. 
            # The tricky part here is that an error can have 
            # additional info in arbitrary format if @verbose is true. 
            if restrict then
               @local = true
               reduced = filter_errors(input, restrict)
               if reduced.class == TrueClass then
                  return true
               else
                  return parse_errors(reduced)
               end
            else
               return parse_errors(input)
            end
         end
      end
      
      def parse_errors(text)
         # @verbose = if true, print additional info lines that do not match one of the error formats
         result = ""
         severity = ""
         errid = ""
         if @tool
            toolstr = " by #{@tool}:"
         else
            toolstr = ""
         end
         if @header then
            result += "<h3>The following issues were found#{toolstr}</h3>\n"
            result += "<hr>\n"
         end
         pre_start = "<pre style=\"word-wrap: break-word;\">\n"
         pre_end = '</pre>'
         result += pre_start
         parts = text.split("\n")
         classification = parts[0]
         if parts.length > 1 then
            description = parts[1..-1].join("<br>")
         else
            description = ""
         end
         if DEBUG > 0
            puts "description = #{description}"
            puts "classification = #{classification}"
         end
         fncol = "color: #{label_color "FILENAME"};"
         text.each_line do |line|
            if line.strip().size == 0 then
               # skip empty lines
               next
            end
            line = line.chop
            if m = @@error_format1.match(line) then
               file, no, severity, error = m[1..4]
               errid = "#{file}:#{no}:#{severity}:#{error}"
               unless @errcache.include? errid && @nodupe then
                  @errcount += 1
                  puts "format1: #{errid}" if DEBUG > 0
                  file = fix_autodoc_error_paths(file)            
                  file = File.expand_path(file, ENV['PWD'])
                  filename = File.basename(file)
                  if @local == false then
                     filenamestr = %Q{&nbsp;&nbsp;#{wrap_styled_span("[#{filename}]", fncol)}}
                  else
                     filenamestr = ""
                  end
                  if File.exists?(file)
                     result += "<p><span style=\"color: #{label_color severity};\">#{severity}</span>:&nbsp;"
                     result += "<a href='txmt://open?url=file://#{url_esc file}"
                     result += "&line=#{no}" unless no.nil?
                     result += "'>#{html_esc error}</a>#{filenamestr}<br></p>"
                  else
                     if @verbose
                        result += line + '<br>'
                     end
                  end
               end
            elsif m = @@error_format2.match(line) then
               file, no, severity, error = m[1..4]
               errid = "#{file}:#{no}:#{severity}:#{error}"
               unless @errcache.include? errid && @nodupe then
                  @errcount += 1
                  puts "format2: #{errid}" if DEBUG > 0
                  file = fix_autodoc_error_paths(file)            
                  file = File.expand_path(file, ENV['PWD'])
                  filename = File.basename(file)
                  if @local == false then # only show filenames when we're reporting errors globally
                     filenamestr = %Q{&nbsp;&nbsp;#{wrap_styled_span("[#{filename}]", fncol)}}
                  else
                     filenamestr = ""
                  end
                  if File.exists?(file) then
                     result += "<p><span style=\"color: #{label_color severity};\">#{severity}</span>:&nbsp;"
                     result += "<a href='txmt://open?url=file://#{url_esc file}"
                     result += "'>#{html_esc error}</a>#{filenamestr}<br></p>\n"
                  else
                     if @verbose
                        result += line + '<br>'
                     end
                  end
               end
            else
               is_err = true
               if @@no_err_messages.include? line then
                  is_err = false
               end
               @@no_err_regexes.each do |re|
                  if re.match line then
                     is_err = false
                  end
               end
               skip_err = (@errcache.include?(errid) && @nodupe)
               if is_err && @verbose != false && !skip_err then
                  @errcount += 1
                  result += line + '<br>'
               end
            end
         end
         result += pre_end
         if @footer then
            result += "<hr>"
            if @local
               result += "<p>showing results for <code>#{File.basename(ENV['TM_FILEPATH'])}</code></p>"
            else
               result += "<p>showing results for project/directory <code>#{SphinxDocUtils::current_dir}</code></p>"
            end
            if @tool == "docutils" then
               result += "<p>Keep in mind that <code>docutils</code> may flag constructs used by <code>Sphinx</code> as errors even though for Sphinx they are valid</p>"
            end
            # since we may find errors that don't have a corresponding line/file 
            # the following doesn't always apply so leave it out
            #result += "<p><small>(click on description to go to the line in the source file)</small></p>"
         end
         if @errcount == 0 then
            # if no errors where matched return true 
            # to let error_parser.rb know not to print anything
            return true
         else
            return result        
         end
      end
      
      def fix_autodoc_error_paths file
         # fix file paths as reported by the autodoc extension 
         # when a file has errors. Usually this looks like
         # <dirname>/<basename>:<thing> of <qualified_id>
         if file.include? ":"
            file = file.split(":")[0..-2]
            file = file.join ":"
         end
         file
      end
      private :fix_autodoc_error_paths
   end
end


if $0 == __FILE__ then
   #text = "Making output directory...\n/Users/andre/Documents/Aptana Studio 2.0/Workspaces/Python/File Sequence Checker/doc/sphinx/example.rst:: WARNING: image file not readable: image.png\n/Users/andre/Documents/Aptana Studio 2.0/Workspaces/Python/File Sequence Checker/doc/sphinx/index.rst:7: (WARNING/2) Title underline too short.\n\nWelcome to File Sequence Checker's documentation!\n================================================\n\n/Users/andre/Documents/Aptana Studio 2.0/Workspaces/Python/File Sequence Checker/doc/sphinx/index.rst:18: (ERROR/3) Error in \"module\" directive:\nunknown option: \"members\".\n\n.. module:: checkfileseq\n   :members:\n\n\n/Users/andre/Documents/Aptana Studio 2.0/Workspaces/Python/File Sequence Checker/doc/sphinx/test.rst:20: WARNING: duplicate object description of checkfileseq.FileSequenceChecker, other instance in /Users/andre/Documents/Aptana Studio 2.0/Workspaces/Python/File Sequence Checker/doc/sphinx/checkfileseq.rst, use :noindex: for one of them\n/Users/andre/Documents/Aptana Studio 2.0/Workspaces/Python/File Sequence Checker/doc/sphinx/checkfileseq.rst:: WARNING: document isn't included in any toctree\n/Users/andre/Documents/Aptana Studio 2.0/Workspaces/Python/File Sequence Checker/doc/sphinx/example.rst:: WARNING: document isn't included in any toctree\n"
   
   ep = SphinxDoc::ErrorParser.new
   #p ep.parse_errors(text)
   
   #parsed = ep.parse_error_file("/tmp/tm_sphinx_doc_errors.txt", "/U1sers/andre/Documents/Aptana Studio 2.0/Workspaces/Python/File Sequence Checker/doc/sphinx/index.rst")
   #parsed = ep.parse_error_file("/tmp/tm_sphinx_doc_errors.txt", "/Users/andre/Documents/Aptana Studio 2.0/Workspaces/Python/File Sequence Checker/doc/sphinx/example.rst")
   #parsed = ep.parse_error_file("/tmp/tm_sphinx_doc_errors.txt", "/Users/andre/Documents/Aptana Studio 2.0/Workspaces/Python/File Sequence Checker/doc/sphinx/index.rst")
   #parsed = ep.parse_error_file("/tmp/tm_sphinx_doc_errors.txt", "/Users/andre/Documents/Eclipse/Projects/Python/fileseq/doc/sphinx/index.rst")
   parsed = ep.parse_error_file("/tmp/tm_sphinx_doc_errors.txt")
   
   #p parsed
   File.open("/Users/andre/sphinxdoc-out.html", "w") do |file|
      file.puts "<!DOCTYPE html PUBLIC \"-//W3C//DTD HTML 4.01//EN\"\n   \"http://www.w3.org/TR/html4/strict.dtd\">\n\n<html lang=\"en\">\n<head>\n\t<meta http-equiv=\"Content-Type\" content=\"text/html; charset=utf-8\">\n\t<title>sphinxdoc.rb debug output</title>\n\t<meta name=\"generator\" content=\"TextMate http://macromates.com/\">\n\t<meta name=\"author\" content=\"Andre Berg\">\n\t<!-- Date: 2010-12-14 -->\n</head>\n<body>\n#{parsed}\n</body>\n</html>"
   end 
   
   #p SphinxDocUtils.current_text
end