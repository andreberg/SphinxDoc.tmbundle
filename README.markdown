# Introduction

This bundle aims to provide support for an effortless way of working on   
`Sphinx` documentation, with some goodies along the way.  

The main goal is to provide the closest thing to live editing capabilities,  
that is, seeing the result of changes to source files automatically reflected  
in the generated HTML build files. 

[RST]: http://docutils.sourceforge.net/rst.html  
[Sphinx]: http://sphinx.pocoo.org/index.html

# Features

## <span>Productive Ways to Generate the HTML</span>

Accomodates several ways to build and view the results.  

  Current options include:

  - Live Editing  
  
    By far the best option is to have <span style="color: red">_quasi live-editing_</span> capabilities.
    
    To enable this set the shell variable `TM_SPHINX_DOC_AUTOMAKE`  
    to any value so that a background build is performed whenever  
    you save via `⌘S` (`cmd+S`).  
    
    Next, find the generated HTML file you are interested in   
    in your build directory (usually `_build`), right-click it  
    in the project drawer and choose `Open <file> in New Window`.  
    Then from the menu choose `Window > Show Web Preview`.  
    
    From the window that appears, reveal the options by clicking  
    on the check box at the lower border and in the options drawer  
    make sure `Refresh after change` is ticked.  
    
    Since you opened the HTML file in a new window the Web Preview  
    Window will not close when you switch back to your project window  
    and change to another source file. This means whenever you make  
    changes to the underlying source file you just need to save to be    
    able to see the effect of your changes a second later in the  
    Web Preview Window. 
    
    Unfortunately I do not know of a way to have the change occur  
    instantly without the need to perform a background build.   
    If you know a way how to set this up in TextMate please do  
    get [in touch](mailto:andre.bergmedia@googlemail.com)!
  
  - Build

  - Build and view the result as HTML 
      
      This will preview the generated HTML file that has the same  
      _basename_ as the source file you are working on when you call  
      the command, unless there is no file with that _basename_.  

      In that case it will preview the master doc file as specified in  
      your `conf.py` file.
      
  - Build and open result in browser  
  
  - Build and refresh browser(s) (in background)
  
  - Build, switch to, and refresh browser  

## <span>Quick Navigation</span>

  Open file `<current word or selection>.<ext>` if present.  
        
  &lt;ext&gt; will normally be `.rst` or `.txt` but can be anything really as long as one  
  specifies the correct extension with the `source_suffix` option in the Sphinx   
  config file. 

  Note: does not search project folders which have names that would be  
  matched by the `exclude_patterns` option in the Sphinx config file.
  
## <span>Consolidated Syntax Validation</span>

  Uses `PyCheckmate` for Python files (say your `conf.py`) and `docutils`  
  or `sphinx-build` for your source files.
  
  And just as you would expect from a TextMate bundle, the error ouput is  
  parsed and styled into good looking and useful HTML output that shows  
  you a color-coded table of error messages, line numbers and clickable  
  file links.
  
  The error parser is able to distinguish between error messages from  
  `docutils` and from `sphinx-build`.  
   
  Additionally, whenever it makes sense, error messages are filtered to   
  show the messages relevant to the current file or to the whole project.  
  
  Basically whenever some sort of build with Sphinx takes place, e.g.  
  when using the Make HTML commands, when doing syntax checking or  
  when saving with `TM_SPHINX_DOC_AUTOMAKE` enabled etc., output from  
  `stderr` is parsed and transformed into human friendly tables and cross  
  links.  
  
  The goal is to automatically present errors to the user when there  
  happen to be some but otherwise to hold back with distractions.
  
## <span>Styling Presets</span>

  Macros and snippets for text markup anc quick fixes.  
  
  For example, with the cursor targeting some line, press `⇧⌃T` (`shift+ctrl+T`)  
  to fix the length of an underline that's to short or too long with  
  respect to the title near it.

## <span>Extended Help</span>

  Cheat sheets, quick refs, quick starts, demos - all at your fingertips.   
  
  You can access the help menu by pressing `⌥F1` (`alt+F1`).

# Execution Model

  Because Sphinx is (in its core) an extension to `reStructuredText`,   
  it makes sense to give you the option of feeding your source text  
  into either of the two builders. 
  
  To get you oriented for browsing the command menu of this bundle,  
  assume that the Sphinx compiler is used by default, unless indicated  
  otherwise. 
  
  Whenever you see a command name with an "`RST`" acronym in it, you can  
  be sure it is instead run through a `docutils` converter like `rst2html.py`.
  
  The "Preview…" line of commands, for example, used this scheme.  
  
  `Preview File as RST`, as you'd expect, uses `rst2html.py`, as does   
  its cousin `Preview File as RST in Browser`. The third command,   
  however, has been titled `Preview Selected Text using Sphinx` not just  
  for extra clarity but to illustrate the point that the previewed text  
  is fed into Sphinx directly, via Python code connection, as opposed   
  to being a product of `sphinx-build`. 
  
# Limitations

Currently completely Python centric. Support for other languages such as   
Ruby may be added at a later date.

Also, currently we only consider the HTML builder. There is rudimentary  
support for `docutils` converters like `rst2html.py` but these don't really  
support full Sphinx syntax.

I am not familiar with the state of Sphinx itself with regards to Python 3  
adoption, but for the Python script included in this bundle I made sure  
they could be used with a Python 3 interpreter. 
  
# Requirements

[Python](http://www.python.org) (v2.6+, see note below about Python 3 support)

[Sphinx][Sphinx] for the Python version in use by TextMate.

Sphinx can be installed using `easy_install`, e.g.:

    easy_install sphinx

<br>
**Python 3 Support**

All Python scripts that were created and maintained by myself have   
been converted to Python 3 using `2to3` with additional ironing out   
of the left-over kinks _whenever I could test them_.  

However, I have been unable to install `Sphinx 1.0.5` for my `Python 3.1.2`  
installation. This meant I needed to create dummy data and mock objects   
to be able to test the bits of Python under my personal control.  

If you have `Sphinx` and its dependency `docutils` installed under  
Python 3 you should be able to use the bundle as envisioned.

For the time being I recommed using this bundle with `Python 2.6`  
or `Python 2.7`.

# Syntax

Information about `reStructuredText (RST)` can be found [here][RST].  
Information about `Sphinx` can be found [here][Sphinx].

# Shell Variables

<table cellpadding="2">
    <tr>
        <td><code>TM_SPHINX_DOC_AUTOMAKE</code></td>
        <td>&nbsp;</td>
        <td><small>set to any value to enable automatic build on file save (default: <code>None</code>)</small></td>
    </tr>
    <tr>
        <td><code>TM_SPHINX_DOC_AUTOMAKE_SILENT</code></td>
        <td>&nbsp;</td>
        <td><small>suppress showing the output of the auto build (default: <code>None</code>)<br>Obviously this needs <code>TM_SPHINX_DOC_AUTOMAKE</code> to be set as well.</small></td>
    </tr>
    <tr>
        <td><code>TM_SPHINX_DOC_AUTOMAKE_GLOBAL_REPORT</code></td>
        <td>&nbsp;</td>
        <td><small>show issues related to all files in the project if set as opposed to<br>showing the issues for just the currently active file (default: <code>None</code>). <br>Obviously this needs <code>TM_SPHINX_DOC_AUTOMAKE</code> to be set as well</small></td>
    </tr>
    <tr>
        <td><code>TM_SPHINX_DOC_COLOR_INFOS</code></td>
        <td>&nbsp;</td>
        <td><small>a color to use for info labels (default: <code>dodgerblue</code>)<br>can be any valid CSS color value.</small></td>
    </tr>
    <tr>
        <td><code>TM_SPHINX_DOC_COLOR_WARNINGS</code></td>
        <td>&nbsp;</td>
        <td><small>a color to use for warning labels (default: <code>orange</code>)<br>can be any valid CSS color value.</small></td>
    </tr>
    <tr>
        <td><code>TM_SPHINX_DOC_COLOR_ERRORS</code></td>
        <td>&nbsp;</td>
        <td><small>a color to use for labels that imply a high alert level such as<br><code>ERROR</code> or <code>SEVERE</code>. (default: <code>red</code>). Can be any valid CSS color value.</small></td>
    </tr>
    <tr>
        <td><code>TM_SPHINX_DOCUTILS_DIR</code></td>
        <td>&nbsp;</td>
        <td><small>path, usually the <code>bin</code> directory of the current Python installation,<br> where <code>docutils</code> converters (<code>rst2html.py</code> and friends) can be found <br>(default: <code>None</code>)</small></td>
    </tr>
    <tr>
        <td><code>TM_SPHINX_BUILD</code></td>
        <td>&nbsp;</td>
        <td><small>path to <code>sphinx-build</code>, which is usually installed by Sphinx to the <code>bin</code><br>directory of the current Python installation. If set will also determine<br>the location of other Sphinx executables such as <code>sphinx-quickstart</code><br>(default: <code>None</code> or <code>TM_SPHINX_DOCUTILS_DIR/sphinx-build</code>) </small></td>
    </tr>
    <tr>
        <td><code>TM_SPHINX_BUILD_DIR</code></td>
        <td>&nbsp;</td>
        <td><small>set name or path of the build output folder (default: <code>_build</code>)</small></td>
    </tr>
    <tr>
        <td><code>TM_SPHINX_CONF_DIR</code></td>
        <td>&nbsp;</td>
        <td><small>set path where the config file is to be found (default: <code>&lt;project_dir&gt;</code>)<br>note: this setting expects a path to a folder and not a file</small></td>
    </tr>
    <tr>
        <td><code>TM_PREFERRED_BROWSER</code></td>
        <td>&nbsp;</td>
        <td><small>which browser to target on <code>open/preview in browser</code> type commands
            <br><code>Safari|Chrome|Firefox|OmniWeb|IE</code> where <code>&lt;no value&gt;</code> = refresh all<br>(default: None)</small></td>
    </tr>
    <tr>
        <td><code>PATH</code></td>
        <td>&nbsp;</td>
        <td><small>the PATH shell variable (set in TextMate) affects the search<br> order of directories for all bundles. <code>*</code></small></td>
    </tr>
</table>
<br> 
<small><code>*</code> if you include your custom Python installation's <code>bin</code> dir (which hosts prerequisites such as <code>docutils</code> and <code>sphinx</code> etc.)<br>before other installations in the <code>PATH</code>, <code>sphinx-build</code>, <code>rst2html.py</code> and other tools should be found automatically.</small>
<br>

# Copyright

Created by André Berg on 2010-12-07.  
Copyright Berg Media 2010. All rights reserved.

Licensed under the Apache License, Version 2.0 (the "License");  
you may not use this file except in compliance with the License.  
You may obtain a copy of the License at

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;[http://www.apache.org/licenses/LICENSE-2.0](http://www.apache.org/licenses/LICENSE-2.0)

Unless required by applicable law or agreed to in writing, software  
distributed under the License is distributed on an "AS IS" BASIS,  
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  
See the License for the specific language governing permissions and  
limitations under the License.

# Acknowledgements

Includes a modified version of `PyCheckmate` from the Python bundle.  
Includes modified versions of commands from the reStructuredText bundle.  
Includes a modified version of the `text.restructuredtext` syntax.  
Includes a modified version of the `refresh_all_running_browsers` script.  
Includes a copy of `util.py` from [rested](http://blog.enthought.com/enthought-tool-suite/a-renewed-restructured-text-editor) (file renamed to `rested_util.py`)  

