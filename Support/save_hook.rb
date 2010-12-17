#!/usr/bin/env ruby
# -*- coding: utf-8 -*-
# 
#  save_hook.rb
#  SphinxDoc.tmbundle
#  
#  Created by Andre Berg on 2010-12-07.
#  Copyright 2010 Berg Media. All rights reserved.
# 
#  Used for providing automake on save functionality.
#
#  Especially useful in conjunction with auto validation,
#  which outputs to Show as HTML preview and with Window > 
#  Show Web Preview, run from a generated HTML file of 
#  interest in the build dir. Tip: open the generated HTML
#  file into a new editor window outside of your project 
#  drawer tabs and you can keep the Show Preview Window
#  window open at all times while you jump around in your
#  source RST files in your project. This is extremely useful
#  because the Show Web Preview window actually has a live
#  refresh on change option so that when you save a source
#  file, auto make kicks in with sphinx-build and you will
#  see the changes of the new generated HTML file a fraction
#  later in the preview window.
#  
#  See also: Help - ⎇F1 or Alt+F1 by default
# 

if ENV['TM_SPHINX_DOC_AUTOMAKE'].nil?
  exit(2)
end

$LOAD_PATH << "#{ENV["TM_SUPPORT_PATH"]}/lib"
require "exit_codes"
require "web_preview"
require "escape"
require 'open3'

if $DEBUG
  require "/Users/andre/Library/Application Support/TextMate/Bundles/Sphinx Doc.tmbundle/Support/sphinxdoc"
else
  require "#{ENV["TM_BUNDLE_SUPPORT"]}/sphinxdoc"
end

errors = ""
output = ""
exit_status = -1
title = "Auto Make on Save"
ok_msg = "Auto Make OK - No Issues"

if RUBY_VERSION == /1\.9/ then
  Open3.popen3('source "$TM_BUNDLE_SUPPORT/sphinx_build.sh"; run_sphinx_build') do |stdin, stdout, stderr, wait_thr|
    while line = stdout.gets
      output += line
    end
    while line = stderr.gets
      errors += line
    end
    exit_status = wait_thr.value
  end
else
  stdin, stdout, stderr = Open3.popen3('source "$TM_BUNDLE_SUPPORT/sphinx_build.sh"; run_sphinx_build')
  while line = stdout.gets
    output += line
  end
  while line = stderr.gets
    errors += line
  end
end

if $DEBUG
  puts "errors = #{errors}"
  puts "output = #{output}"
end

SphinxDocUtils::refresh_document

if RUBY_VERSION == /1\.9/ then
  succ = exit_status.success?
else
  succ = ($? == 0)
end
  
if succ && errors == ""
  if $DEBUG then
    html_header(title, "Sphinx")
  
    puts <<-END_HTML
      <h1>Output</h1>
      #{output}
    END_HTML
   
    html_footer
    TextMate.exit_show_html
  else
    if ENV['TM_SPHINX_DOC_AUTOMAKE_SILENT'].nil? then
      TextMate.exit_show_tool_tip(ok_msg)
    end
  end
else
  if ENV['TM_SPHINX_DOC_AUTOMAKE_SILENT'].nil? then
    
    
    errors_tmp_file = ENV['TM_SPHINX_DOC_ERRORS_TMP_FILE']
    
    #TextMate.exit_show_tool_tip("errors_tmp_file = #{errors_tmp_file}")
    #TextMate.exit_show_tool_tip("TM_SPHINX_DOC_AUTOMAKE_GLOBAL_REPORT = #{!ENV['TM_SPHINX_DOC_AUTOMAKE_GLOBAL_REPORT'].nil?}")
    
    # if File.exists? errors_tmp_file then
    #   File.delete errors_tmp_file
    # end
    
    File.open(errors_tmp_file, "w") do |file|
      file.puts(errors)
    end
    
    ep = SphinxDoc::ErrorParser.new
    
    if File.size(errors_tmp_file) > 0 && ENV['TM_SPHINX_DOC_AUTOMAKE_GLOBAL_REPORT'].nil? then
      result = ep.parse_error_file(errors_tmp_file, ARGV[0])
    elsif errors.length > 0 then
      result = ep.parse_errors(errors)
    end

    if result == true then
      TextMate.exit_show_tool_tip(ok_msg)
    else
      html_header(title, "Sphinx Doc")
      
      puts <<-END_HTML
        #{result}
      END_HTML

      html_footer
      TextMate.exit_show_html
    end

  end
end