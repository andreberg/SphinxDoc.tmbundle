# 
#  sphinx_build.sh
#  SphinxDoc.tmbundle
#  
#  Created by Andre Berg on 2010-12-07.
#  Copyright 2010 Berg Media. All rights reserved.
# 
#  allows for running sphinx-build while providing
#  options for what output should be printed out 
#  and what output should be redirected to one of
#  the tmp files. Output means streams to stdout 
#  or stderr.

DEBUG=0

if [[ $DEBUG = 1 ]]; then
    . "$HOME/Library/Application Support/TextMate/Bundles/SphinxDoc.tmbundle/Support/init.sh"
else
    . "$TM_BUNDLE_SUPPORT/init.sh"
fi

function run_sphinx_build() {
    # $1: redirect_stdout|redirect_stderr|mute_stdout_redirect_stderr|mute_stderr_redirect_stdout|mute_stdout_and_stderr|pre
    # $2: which builder to use (default: html)
    
    # the check here should be superfluous since we source init.sh
    # at the beginning where it should have already happened.
    # require_cmd "$sphinx_build" "$err_sphinx_not_found_msg"

    source_dir="${project_dir}"
    conf_dir="${conf_dir}"
    build_dir="${build_dir}"
    
    #echo "source_dir=$source_dir"
    #echo "conf_dir=$conf_dir"
        
    # not entirely sure if we need to cd into the config dir, either 
    # if config dir isn't the same as the source dir or if it is,
    # so that relative paths given in config file just work.
    #cd "$conf_dir"
    
    if [[ -n "$2" ]]; then
        builder="${2}"
    else
        builder="html"
    fi
    
    # I think the following rm -rf is too risky. this bundle depends on so many
    # environment variables where paths get constructed from (just see init.sh)
    # so that it may actually happen that a variable contributing a crucial part
    # of a path is not set or is set incorrectly. If we follow this through blindly
    # we may actually end up deleting something very important such as "/"
    # Better leave the cleaning up to the user. If she really wants a completely
    # fresh start all she has to do is delete the parent output folder.
    # Also this has the benefit that if nothing changed Sphinx runs much quicker
    # as it knows not to re-render.
    
    # if [[ "$target_dir" == "/" || -z "$source_dir" ]]; then
    #     echo "<p>E: cannot delete target dirtree because the target dir is equal to file system root or the variable is empty</p>"
    #     return 2
    #elif [[ -d "$target_dir" ]]; then
    #   # remove residue
    #   rm -rf "$target_dir"
    # fi

    if [[ -s "$errors_tmp_file" ]]; then
        rm "$errors_tmp_file"
    fi
    if [[ -s "$output_tmp_file" ]]; then
        rm "$output_tmp_file"
    fi
    if [[ -s "$output_tmp_file_html" ]]; then
        rm "$output_tmp_file_html"
    fi
    
    # need to add source_dir to Python's PATH because of 
    # extensions that the user may include in her conf.py
    export PYTHONPATH="$source_dir:$PYTHONPATH"
    
    if [[ "${1}" = "redirect_stdout" ]]; then
        cmd="\"$sphinx_build\" -N -c \"$conf_dir\" -b \"$builder\" \"$source_dir\" \"$build_dir\" 1> \"$output_tmp_file\" | pre"
    elif [[ "${1}" = "redirect_stderr" ]]; then
        cmd="\"$sphinx_build\" -N -c \"$conf_dir\" -b \"$builder\" \"$source_dir\" \"$build_dir\" 2> \"$errors_tmp_file\" | pre"
    elif [[ "${1}" = "mute_stdout_redirect_stderr" ]]; then
        cmd="\"$sphinx_build\" -N -c \"$conf_dir\" -b \"$builder\" \"$source_dir\" \"$build_dir\" > /dev/null 2> \"$errors_tmp_file\""
    elif [[ "${1}" = "mute_stderr_redirect_stdout" ]]; then
        cmd="\"$sphinx_build\" -N -c \"$conf_dir\" -b \"$builder\" \"$source_dir\" \"$build_dir\" > \"$output_tmp_file\" 2> /dev/null"
    elif [[ "${1}" = "mute_stdout_and_stderr" ]]; then
        cmd="\"$sphinx_build\" -N -c \"$conf_dir\" -b \"$builder\" \"$source_dir\" \"$build_dir\" &> /dev/null"
    elif [[ "${1}" = "pre" ]]; then
        cmd="\"$sphinx_build\" -N -c \"$conf_dir\" -b \"$builder\" \"$source_dir\" \"$build_dir\" | pre"
    else
        echo "Error: run_sphinx_build() must be called with at least one argument!"
        echo "See $TM_BUNDLE_SUPPORT/sphinx_build.sh for infos"
        return 1
    fi
    
    if [[ $DEBUG = 1 ]]; then
        echo "source_dir=$source_dir<br>"
        echo "build_dir=$build_dir<br>"
        echo "conf_dir=$conf_dir<br>"
        echo "errors_tmp_file=$errors_tmp_file<br>"
        echo "output_tmp_file=$output_tmp_file<br>"
        echo "builder=$builder<br>"
        echo "sphinx_build=$sphinx_build<br>"
        echo "cmd=$cmd<br>"
        echo "PATH=$PATH<br>"
        echo "PYTHONPATH=$PYTHONPATH<br>"
    fi
    
    output=`eval $cmd` 
    
    IFS=$'\n'
    for line in "$output"; do
      echo "$line<br>"
    done 
    
    if [[ -s "$errors_tmp_file" ]]; then
    	"$ruby" "$TM_BUNDLE_SUPPORT/error_parser.rb" "$errors_tmp_file"
    	return 2
    else
        return 0
    fi
    
    # cd back to where we came from 
    # note that this is highly volatile if cd history is changed
    # in a subsequent included script that we call from here!
    #cd -
}