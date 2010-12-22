# 
#  init.sh
#  SphinxDoc.tmbundle
#  
#  Created by Andre Berg on 2010-12-07.
#  Copyright 2010 Berg Media. All rights reserved.
# 
#  Init values that can be sourced

. "$TM_SUPPORT_PATH/lib/bash_init.sh"

# --------------------------------------------------------------------
#                      Settings / Variables 
# --------------------------------------------------------------------

# variables shared throughout the whole bundle

errors_tmp_file="/tmp/tm_sphinx_doc_errors.txt"
output_tmp_file="/tmp/tm_sphinx_doc_output.txt"
output_tmp_file_html="${output_tmp_file%%.*}.html"

current_dir="${TM_PROJECT_DIRECTORY:-$TM_DIRECTORY}"
current_file="${TM_FILEPATH:-untitled}"
current_text="${TM_SELECTED_TEXT:-${TM_CURRENT_LINE:-${TM_CURRENT_WORD:-Nothing selected}}}"

build_dir="${TM_SPHINX_BUILD_DIR:-${current_dir}/_build}"
project_name=`basename "$current_dir"`

rst2html="${TM_SPHINX_DOCUTILS_DIR}${TM_SPHINX_DOCUTILS_DIR:+/}rst2html.py"
rst2xml="${TM_SPHINX_DOCUTILS_DIR}${TM_SPHINX_DOCUTILS_DIR:+/}rst2xml.py"
rst2latex="${TM_SPHINX_DOCUTILS_DIR}${TM_SPHINX_DOCUTILS_DIR:+/}rst2latex.py"
rst2newlatex="${TM_SPHINX_DOCUTILS_DIR}${TM_SPHINX_DOCUTILS_DIR:+/}rst2newlatex.py"
rst2s5="${TM_SPHINX_DOCUTILS_DIR}${TM_SPHINX_DOCUTILS_DIR:+/}rst2s5.py"

if [[ -s "$TM_SPHINX_BUILD" ]]; then
    sphinx_build="$TM_SPHINX_BUILD"
else
    if [[ -s "${TM_SPHINX_DOCUTILS_DIR}/sphinx-build" ]]; then
        sphinx_build="${TM_SPHINX_DOCUTILS_DIR}/sphinx-build"
    else
        sphinx_build="sphinx-build"
    fi
fi

spqsdir=$(dirname "$TM_SPHINX_BUILD")

if [[ -s "$spqsdir/sphinx-quickstart" ]]; then
    sphinx_quickstart="$spqsdir/sphinx-quickstart"
else
    if [[ -s "${TM_SPHINX_DOCUTILS_DIR}/sphinx-quickstart" ]]; then
        sphinx_quickstart="${TM_SPHINX_DOCUTILS_DIR}/sphinx-quickstart"
    else
        sphinx_quickstart="sphinx-quickstart"
    fi 
fi

sphinx_conf="${TM_SPHINX_CONF_DIR:.}"

preferred_browser="${TM_PREFERRED_BROWSER:-Safari}"

python="${TM_PYTHON:-python}"
ruby_="${TM_RUBY:-ruby}"
if [[ `"$ruby_" -v` =~ "1.9" ]]; then
	ruby_encflag="-E utf-8" # ruby 1.9
else
	ruby_encflag="-KU" # ruby 1.8
fi
ruby="$ruby_"

# colors (CSS) used for HTML styling

# note: these aren't used universely
# they are only here as a fall back
# for use as default value in shell scripts 
# The user also has a say in what color
# is used for a label by means of setting
# the TM_SPHINX_DOC_COLOR... shell vars.
color_infos="dodgerblue"
color_warnings="orange"
color_errors="red"
color_files="#555"

# -----------------------------------------------------------------
#                      Initial Functions 
# -----------------------------------------------------------------

# Note: functions should only be stored here when absolutely 
# neccessary in terms of load order!

function islink() {
    if [[ -L "${1}" ]]; then
        echo 1
    else
        echo 0
    fi
}

function resolve_link() {
    if [[ -L "${1}" ]]; then
        curdir="`pwd`"
        if [[ -d "${1}" ]]; then
            cd "${1}"
        else
            cd `dirname "${1}"`
            #echo "pwd = `pwd`"
        fi
        target=`stat -n -f '%Y' "${1}"`
        echo "$target"
        cd "$curdir"
    else
        echo "${1}"
    fi
}

function abspath () {
    if [[ "${1}" =~ "../" || "${1}" =~ "./" ]]; then
        # $2 = which base path to resolve against
        if [[ -d "$2" ]]; then
            cd "$2"
        else
            cd $(dirname "$2")
            #echo "pwd3 = `pwd`"
        fi
        if [[ -d "$1" ]]; then
            cd "$1"
        else
            cd $(dirname "$1")
        fi
        echo `pwd`
    else
        echo "${1}"
    fi
}

function python_version () {
    # $1 = python interpreter (path or file) 
    # Python 3.1.2 => 312
    # Python 2.7.1 => 271
    # ...
    # should be backwards compatible to at
    # least Python 2.5.
    if [[ -n "${1}" ]]; then
        echo -n $("${1}" -c 'import sys; hexv = "%x" % sys.hexversion; print(hexv[0]+hexv[2]+hexv[4])') 
    else
        echo -n $(python -c 'import sys; hexv = "%x" % sys.hexversion; print(hexv[0]+hexv[2]+hexv[4])') 
    fi
}

function entitify_keyboard_shortcuts() {
    # a function to replace constructs such as "alt+F1"
    # with the symbolic counterpart: ⌥F1. Works for "alt+"
    # "ctrl+" and "cmd+" or "command+" and case variations.
    echo "${1}" | sed -E 's/(alt|Alt)\+/\&#x2325;/g' | \
    sed -E 's/(cmd|Cmd|command|Command)\+/\&#x2318;/g' | \
    sed -E 's/(ctrl|Ctrl|Control|control)\+/\&#x2303;/g' | \
    sed -E 's/(shift|Shift)\+/\&#x21E7;/g'
}

# a modified version of TextMate's default require_cmd
# which can be found at $TM_SUPPORT_PATH/bash_init.sh
# It runs $1 through basename if $1 appears to be a path
# instead of a executable name, adds the dirname of this
# path to PATH so it can be presented, and also removes 
# duplicate entries from the PATH presented to the user.
#
# The original info about require_cmd is reprinted 
# here:
#
# "this will check for the presence of a command and
# prints an (HTML) error + exists if it's not there""
function requires () {
    if [[ "$1" =~ "/" ]]; then
        cmddirname=`dirname "$1"`
        cmdbasename=`basename "$1"`
        PATH="$cmddirname:${PATH}"
    else
        cmddirname=""
        cmdbasename="$1"
    fi
    if ! type -p "$1" >/dev/null; then
	    cat <<HTML
<h3 class="error">Couldn't find $cmdbasename</h3>
${2:+<p>$2</p>}
<p>Locations searched:</p>
<p><pre>
`echo "${PATH//:/
}" | uniq`
</pre></p>
HTML
	    exit_show_html;
    fi
}


# --------------------------------------------------------------
#                      Error Messages 
# --------------------------------------------------------------

# to be used primarily with the require_cmd

err_help_hint=$(entitify_keyboard_shortcuts "Please see the bundle help (alt+F1) for more info.")

err_python_modules_not_found=`cat <<EOF
One or more modules couldn't be found.
Prerequisites include <code>docutils</code> and <code>Sphinx</code>.

$err_help_hint

If you have multiple Python installations, make sure 
the PATH in TextMates Shell Variables preferences 
is set up properly to point to the Python installation 
which has all the required modules.

Or point to the <code>python</code> executable directly by 
setting a <code>TM_PYTHON</code> variable.
EOF
`

err_python_not_found_msg="To tell TextMate where to find a valid Python installation, go to <code>Preferences &rarr; Advanced &rarr; Shell Variables</code> and either add a <code>PATH</code> setting that includes the <code>bin</code> directory of your Python installation or point to the <code>python</code> executable directly by setting a <code>TM_PYTHON</code> variable.<br><br>${err_help_hint}"

err_ruby_not_found_msg="To tell TextMate where to find a valid Ruby installation, go to <code>Preferences → Advanced &rarr; Shell Variables</code> and either add a <code>PATH</code> setting that includes the <code>bin</code> directory of your Ruby installation or point to the <code>ruby</code> executable directly by setting a <code>TM_RUBY</code> variable.<br><br> ${err_help_hint}"

err_sphinx_not_found_msg="To tell TextMate where to find a valid Sphinx installation, go to <code>Preferences &rarr; Advanced &rarr; Shell Variables</code> and either add a <code>PATH</code> setting that includes the <code>bin</code> directory of the correct Python installation (the correct one being the one that has the <code>Sphinx</code> executables) or point to the <code>sphinx-build</code> executable directly by setting a <code>TM_SPHINX_BUILD</code> variable.<br><br>Note: if <code>TM_SPHINX_DOCUTILS_DIR</code> is set the directory it points to will also be searched for <code>sphinx-build</code>.<br><br>${err_help_hint}"

err_docutils_not_found_msg="To tell TextMate where to find valid docutils installation, go to <code>Preferences &rarr; Advanced &rarr; Shell Variables</code> and either add a <code>PATH</code> setting that includes the <code>bin</code> directory of your Python installation (or wherever else you chose to install <code>rst2html.py</code> and friends) or point to the directory containing <code>rst2html.py</code> and friends directly by setting a <code>TM_SPHINX_DOCUTILS_DIR</code> variable. <br><br>${err_help_hint}"


# ------------------------------------------------------------------
#                      Check Requirements 
# ------------------------------------------------------------------


requires "$python" "$err_python_not_found_msg"

if [[ $((`python_version "$python"`)) < 260 ]]; then 
    cat <<-HTML
<h3 class="error">Unsupported Python Version</h3>
<p>Requirement not met:<br><br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;need at least <code>Python 2.6</code>.</p>
<p>`entitify_keyboard_shortcuts "$err_python_not_found_msg"`</p>
<p></p>
<p>Locations searched:</p>
<p><pre>
`echo "${PATH//:/
}" | uniq`
</pre></p>
HTML
	exit_show_html
fi

# the following may seem complex - and it really is. 
# a situation arises from the many possibilities
# in combinations between shell variables, python versions
# and default paths.
# In principle we try to go from special case (e.g. shell 
# variables set) to general case (e.g. no TM_PYTHON set 
# and no shell variables like TM_SPHINX_BUILD set) and we
# try to infer what information we can by following, 
# for example, the absolute path to the current Python 
# installation's bin dir etc. We then try different 
# combinations of <bin path> + <toolname we are looking for>
# to see what's there. Of course we also need to watch
# out for not breaking the ability to set locations
# to essential executables by using shell variables. 

if [[ -n "$TM_PYTHON" && -L "$TM_PYTHON" ]]; then
    # case 1: TM_PYTHON is set and is a symbolic link
    pythonbin=`abspath $(resolve_link "$python") "$python"`
    if [[ ! -d "${TM_SPHINX_DOCUTILS_DIR}" && ! -s "$TM_SPHINX_BUILD" ]]; then
        # re-adjust inferred path to sphinx-build 
        # but only if the user hasn't set any shell 
        # variables. Remember: specific > general
        sphinx_build="$pythonbin/sphinx-build"
    fi
    if [[ ! -d "${TM_SPHINX_DOCUTILS_DIR}" && -s "${TM_SPHINX_DOCUTILS_DIR}/rst2html.py" ]]; then
        # re-adjust inferred path to rst2html.py
        # but only if the user hasn't set any shell 
        # variables. 
        
        # FIXME: maybe check for all other essential
        # docutils tools (e.g. rst2s5, rst2xml etc.)?
        export TM_SPHINX_DOCUTILS_DIR="$pythonbin"
    fi
    
elif [[ -n "$TM_PYTHON" && -s "$TM_PYTHON" ]]; then
    # case 2: TM_PYTHON is defined and points to 
    # a non-zero byte sized file/executable.
    pythonbin=`dirname "$TM_PYTHON"`
fi

if [[ -n "$pythonbin" ]]; then
    # case 1/2 cont'd
    # if pythonbin is set it should now point to the
    # absolute path of the user's Python bin dir, so
    # try different tool names, and see what is there
    if [[ ! -s "${pythonbin}/sphinx-build" ]]; then
        requires "$sphinx_build" "$err_sphinx_not_found_msg"
    else
        sphinx_build="$pythonbin/sphinx-build"
    fi
    if [[ ! -s "${pythonbin}/sphinx-quickstart" ]]; then
        requires "$sphinx_quickstart" "$err_sphinx_not_found_msg"
    else
        sphinx_quickstart="$pythonbin/sphinx-quickstart"
    fi
    if [[ ! -s "${pythonbin}/rst2html.py" ]]; then
        requires "$rst2html" "$err_docutils_not_found_msg"
    else
        # FIXME: maybe check for all other essential
        # docutils tools (e.g. rst2s5, rst2xml etc.)?
        export TM_SPHINX_DOCUTILS_DIR="$pythonbin"
    fi
elif [[ "$python" = "python" ]]; then
    # case 3: nothing defined - let's try to see what 
    # can be found in PATH. 
    if [[ ! -s "`which sphinx-build`" ]]; then
        requires "$sphinx_build" "$err_sphinx_not_found_msg"
    fi
    if [[ ! -s "`which rst2html.py`" ]]; then
        requires "$rst2html" "$err_docutils_not_found_msg"
    fi
else
    # case 4: all is lost? - let's try on more time 
    # in the most general way possible...
    requires "python" "$err_python_not_found_msg"
fi

requires "$ruby" "$err_ruby_not_found_msg"

# ------------------------------------------------------------------------
#                      Preparation Steps /Hooks 
# ------------------------------------------------------------------------

# add steps here which are beneficial to the execution of other commands

# compile all Python files 
# (only re-compiles if mod dates of the source .py files are different from the corresponding .pyc files)
#"$python" -c "import compileall; compileall.compile_dir(\"${TM_BUNDLE_SUPPORT}\", quiet=True)"