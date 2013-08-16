# 
#  init.sh
#  SphinxDoc.tmbundle
#  
#  Created by Andre Berg on 2010-12-07.
#  Copyright 2010 Berg Media. All rights reserved.
# 
#  this file houses project-wide variables and 
#  basic functions. it is intended to be included
#  as a first step in every shell based command.
#

. "$TM_SUPPORT_PATH/lib/bash_init.sh"

# --------------------------------------------------------------------
#                      Settings / Variables 
# --------------------------------------------------------------------

# variables shared throughout the whole bundle
errors_tmp_file="/tmp/tm_sphinx_doc_errors.txt"
output_tmp_file="/tmp/tm_sphinx_doc_output.txt"
output_tmp_file_html="${output_tmp_file%%.*}.html"

current_dir="${TM_DIRECTORY:-$TM_PROJECT_DIRECTORY}"
project_dir="${TM_PROJECT_DIRECTORY:-$TM_DIRECTORY}"
current_file="${TM_FILEPATH:-untitled}"
current_text="${TM_SELECTED_TEXT:-${TM_CURRENT_LINE:-${TM_CURRENT_WORD:-Nothing selected}}}"

project_name=`basename "$project_dir"`

build_dir="${TM_SPHINX_BUILD_DIR:-$project_dir/_build}"
conf_dir="${TM_SPHINX_CONF_DIR:-$project_dir}"
conf_filename="${TM_SPHINX_CONF_FILENAME:-conf.py}"

txmt_settings_file_name="${TM_SPHINX_DOC_SETTINGS_FILE_NAME:-.txmt_sphinxdoc_settings}"
txmt_settings_file="${project_dir}/${txmt_settings_file_name}"

preferred_browser="${TM_PREFERRED_BROWSER:-Safari}"

if [[ -s "$TM_SPHINX_BUILD" ]]; then
    sphinx_build="$TM_SPHINX_BUILD"
else
    if [[ -s "${TM_SPHINX_DOCUTILS_DIR}/sphinx-build" ]]; then
        sphinx_build="${TM_SPHINX_DOCUTILS_DIR}/sphinx-build"
    else
        sphinx_build="sphinx-build"
    fi
fi

sbdir=$(dirname "$TM_SPHINX_BUILD")

if [[ -s "$sbdir/sphinx-quickstart" ]]; then
    sphinx_quickstart="$sbdir/sphinx-quickstart"
else
    if [[ -s "${TM_SPHINX_DOCUTILS_DIR}/sphinx-quickstart" ]]; then
        sphinx_quickstart="${TM_SPHINX_DOCUTILS_DIR}/sphinx-quickstart"
    else
        sphinx_quickstart="sphinx-quickstart"
    fi 
fi

# NB: sphinx and docutils related variables will be adjusted once we have found 
# the user's preferred and valid Python installation because paths to tools from 
# Sphinx and docutils can be inferred when we know the path <python installation>/bin
# for example. This adjustment only happens though, if more specific user shell vars
# like TM_SPHINX_DOCUTILS_DIR are not set.

# rst2html="${TM_SPHINX_DOCUTILS_DIR}${TM_SPHINX_DOCUTILS_DIR:+/}rst2html.py"
# rst2xml="${TM_SPHINX_DOCUTILS_DIR}${TM_SPHINX_DOCUTILS_DIR:+/}rst2xml.py"
# rst2latex="${TM_SPHINX_DOCUTILS_DIR}${TM_SPHINX_DOCUTILS_DIR:+/}rst2latex.py"
# rst2newlatex="${TM_SPHINX_DOCUTILS_DIR}${TM_SPHINX_DOCUTILS_DIR:+/}rst2newlatex.py"
# rst2s5="${TM_SPHINX_DOCUTILS_DIR}${TM_SPHINX_DOCUTILS_DIR:+/}rst2s5.py"

if [[ -s "$sbdir/rst2html.py" ]]; then
    rst2html="$sbdir/rst2html.py"
else
    if [[ -s "${TM_SPHINX_DOCUTILS_DIR}/rst2html.py" ]]; then
        rst2html="${TM_SPHINX_DOCUTILS_DIR}/rst2html.py"
    else
        rst2html="rst2html.py"
    fi 
fi
if [[ -s "$sbdir/rst2xml.py" ]]; then
    rst2xml="$sbdir/rst2html.py"
else
    if [[ -s "${TM_SPHINX_DOCUTILS_DIR}/rst2xml.py" ]]; then
        rst2xml="${TM_SPHINX_DOCUTILS_DIR}/rst2xml.py"
    else
        rst2xml="rst2xml.py"
    fi 
fi
if [[ -s "$sbdir/rst2latex.py" ]]; then
    rst2latex="$sbdir/rst2latex.py"
else
    if [[ -s "${TM_SPHINX_DOCUTILS_DIR}/rst2latex.py" ]]; then
        rst2latex="${TM_SPHINX_DOCUTILS_DIR}/rst2latex.py"
    else
        rst2latex="rst2latex.py"
    fi 
fi
if [[ -s "$sbdir/rst2newlatex.py" ]]; then
    rst2newlatex="$sbdir/rst2newlatex.py"
else
    if [[ -s "${TM_SPHINX_DOCUTILS_DIR}/rst2newlatex.py" ]]; then
        rst2newlatex="${TM_SPHINX_DOCUTILS_DIR}/rst2newlatex.py"
    else
        rst2newlatex="rst2newlatex.py"
    fi 
fi
if [[ -s "$sbdir/rst2s5.py" ]]; then
    rst2s5="$sbdir/rst2s5.py"
else
    if [[ -s "${TM_SPHINX_DOCUTILS_DIR}/rst2s5.py" ]]; then
        rst2s5="${TM_SPHINX_DOCUTILS_DIR}/rst2s5.py"
    else
        rst2s5="rst2s5.py"
    fi 
fi


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

function islink () {
    if [[ -L "${1}" ]]; then
        echo 1
    else
        echo 0
    fi
}

# function resolve_link() {
#     # resolves a path given by $1 to its absolute path
#     # returns $1 as-is if it isn't a symbolic link
#     if [[ -L "${1}" ]]; then
#         # curdir="`pwd`"
#         # if [[ -d "${1}" ]]; then
#         #     cd "${1}"
#         # else
#         #     cd `dirname "${1}"`
#         # fi
#         target=`stat -n -f '%Y' "${1}"`
#         if [[ ! "$target" =~ "/" && "${1}" =~ "/" ]]; then
#             parentdir=`dirname "$1"`
#             target="$parentdir/$target"
#         fi
#         echo -n "$target"
#         cd "$curdir"
#     else
#         echo "${1}"
#     fi
# }

function resolve_link () {
    # resolves a path given by $1 to its absolute path
    # returns $1 as-is if it isn't a symbolic link
    # return codes:
    #   -1 - no resolving needed. file at "$1" isn't a symlink.
    #    0 - resolving succeeded
    #    1 - error: file at "$1" doesn't exist
    #    2 - error while trying to resolve a relative path further
    if [[ -L "$1" ]]; then
        curdir=`pwd`
        resolved=`stat -n -f '%Y' "${1}"`
        #echo "resolved = $resolved"
        if [[ ! "$resolved" =~ "/" && "$1" =~ "/" ]]; then
            # if $resolved doesn't look like a path, but "$1" did,
            # $resolved should be relative to `dirname $1`
            parentdir=`dirname "$1"`
            resolved="$parentdir/$resolved"
        elif [[ "$resolved" =~ "../" || "$resolved" =~ "./" ]]; then
            # resolve relative path result
            # a relative path result should happen when 
            # `dirname "$1"` != `dirname "$PWD"`
            if [[ -d "$resolved" ]]; then
                # if $resolved is a dir we can cd into
                # that should suffice
                cd "$resolved"
            elif [[ "$1" =~ "/" ]]; then
                # if $1 was given as absolute path to the symbolic link,
                # then $resolved is relative to `dirname $1`
                cd `dirname "$1"` && cd `dirname "$resolved"`
            else
                echo "E: can't resolve relative path ($resolved)"
                return 2
            fi
            parentdir=`pwd`
            name=`basename "$resolved"`
            resolved="$parentdir/$name"
        fi
        echo -n "$resolved"
        cd "$curdir"
        return 0
    elif [[ ! -s "$1" ]]; then
        echo "E: file '$1' doesn't exist!"
        return 1
    else
        echo -n "$1"
        return -1
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

function entitify_keyboard_shortcuts () {
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

function strrepeat () {
    # $1: string
    # $2: times
    for (( c=1; c<=$2; c++)); do 
        echo -en "$1";
    done
}

function strlen () {
    echo "${#1}"
}

# dump all variables contained in a shell file to a tmp file
# variables must have strict shell syntax, e.g. "var=value"
# arg1: path to shell file containing the variables to dump
# arg2: path to output file
# options: 
#   -v|--verbose echo variables as they are appended to outfile
#
function dump_variables () {
    verbose=
    while test $# -gt 2; do
        case "$1" in
            -*=*) optarg=`echo "$1" | sed 's/[-_a-zA-Z0-9]*=//'` ;;
            *) optarg= ;;
        esac
        case $1 in
            -v|--verbose)
                verbose=1
                ;;
            *)
                echo "${usage}" 1>&2
                exit 1
                ;;
        esac
        shift
    done
    infile="$1"
    outfile="$2"
    #echo "infile=$infile"
    #echo "outfile=$outfile"
    #echo "\$@=$@"
    #echo "verbose=$verbose"
    if [[ ! -s "$infile" ]]; then
        return 1
    fi
    result=`grep -o -E '[-_a-zA-Z0-9]+=' <<< cat "$infile"`
    set_output="`set`"
    echo "result=$result"
    #echo "set_output=$set_output"
    if [[ -e "$outfile" ]]; then
        rm "$outfile"
    fi
    for i in "$result"; do
        if [[ ${#i} > 2 ]]; then # ignore 1-letter variables
            cur_variable=`echo "$i" | tr -d '='`
            cur_variable_expanded="$cur_variable=$(eval echo $`echo $cur_variable`)"
            if [[ verbose = 1 ]]; then
                echo "$cur_variable_expanded"
            fi
            echo "$cur_variable_expanded" >> "$outfile"
        fi 
    done
    return 0
}

function read_txmt_project_settings() {
    if [[ -s "$txmt_settings_file" ]]; then
        #echo "sourcing project settings file at $txmt_settings_file...<br>"
        source "$txmt_settings_file"
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

# check required executables and adjust previous variable settings
# when new, more correct info can be inferred.

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
    pythonbin=`dirname $(resolve_link "$python")`
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

# read per-project settings file

#echo "conf_dir=$conf_dir<br>"
#echo "build_dir=$build_dir<br>"

read_txmt_project_settings

# qualify paths - need to do this here since
# the project settings file could have overwritten
# the values set earlier

if [[ "${conf_dir:0:1}" = "/" || "${conf_dir:0:1}" = "." ]]; then
    # if conf_dir is absolute (or if it uses the default fall back value) 
    # use it as-is
    :
else
    # otherwise append conf_dir to current_dir
    conf_dir="$project_dir/$conf_dir"
fi

if [[ "${build_dir:0:1}" = "/" ]]; then
    # if build_dir is absolute use it as-is
    :
else
    # otherwise append build_dir to current_dir
    if [[ "`basename ${project_dir}`" != "${build_dir}" ]]; then
        # Special case: if there is no TextMate project project_dir will be the current_dir
        # in which case it could very well be that the current_dir already is the build_dir.
        # In that case we don't want to append the build_dir again.
        build_dir="$project_dir/$build_dir"
    fi
fi

conf_dirname=`basename "$conf_dir"`
build_dirname=`basename "$build_dir"`

#echo "conf_dir=$conf_dir<br>"
#echo "build_dir=$build_dir<br>"

# dump variables and their values to a file in /tmp so that we can read those values in places
# where going through the environment won't work, e.g. when transitioning from one command system
# to another i.e. shell > python > ruby etc...
#
# IMPORTANT: this setting is not intended to be changed by an end user of SphinxDoc bundle.
# It is used in other places throughout the bundle and is thus reserved for internal use only!
#
registry_tmp_file="/tmp/tm_sphinx_doc_registry.txt"
export __tm_sphinx_doc_registry_tmp_file="$registry_tmp_file"

registry_vars=(registry_tmp_file errors_tmp_file output_tmp_file output_tmp_file_html current_dir project_dir current_file project_name build_dir build_dirname conf_dir conf_dirname conf_filename txmt_settings_file_name txmt_settings_file preferred_browser sphinx_build sphinx_quickstart rst2html rst2xml rst2latex rst2newlatex rst2s5 python ruby color_infos color_warnings color_errors color_files err_help_hint err_python_modules_not_found err_python_not_found_msg err_ruby_not_found_msg err_sphinx_not_found_msg err_docutils_not_found_msg)

if [[ -s "$registry_tmp_file" ]]; then
    rm "$registry_tmp_file"
fi
echo "[Init]" >> "$registry_tmp_file"
for i in ${registry_vars[@]}; do
    var_name="$i"
    var_value="$(eval echo \$`echo $var_name`)"
    echo "$var_name=$var_value" >> "$registry_tmp_file"
done

#echo "$important_variables_registry"
#echo dump_variables -v "$0" "$registry_tmp_file"`
