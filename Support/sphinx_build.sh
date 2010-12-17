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

. "$TM_BUNDLE_SUPPORT/init.sh"

function run_sphinx_build() {
    
    # the check here should be superfluous since we source init.sh
    # at the beginning where it should have already happened.
    # require_cmd "$sphinx_build" "$err_sphinx_not_found_msg"

    source_dir="$current_dir"
    target_dir="$source_dir/$build_dir"

    # remove residue
    if [[ -d "$target_dir" ]]; then
        rm -rf "$target_dir"
    fi
    if [[ -s "$errors_tmp_file" ]]; then
        rm "$errors_tmp_file"
    fi
    if [[ -s "$output_tmp_file" ]]; then
        rm "$output_tmp_file"
    fi
    if [[ -s "$output_tmp_file_html" ]]; then
        rm "$output_tmp_file_html"
    fi
    
    if [[ "${1}" = "redirect_stdout" ]]; then
        "$sphinx_build" "$source_dir" "$build_dir" 1> "$output_tmp_file" | pre
    elif [[ "${1}" = "redirect_stderr" ]]; then
        "$sphinx_build" "$source_dir" "$build_dir" 2> "$errors_tmp_file" | pre
    elif [[ "${1}" = "mute_stdout_redirect_stderr" ]]; then
        "$sphinx_build" "$source_dir" "$build_dir" > /dev/null 2> "$errors_tmp_file"
    elif [[ "${1}" = "mute_stderr_redirect_stdout" ]]; then
        "$sphinx_build" "$source_dir" "$build_dir" > "$output_tmp_file" 2> /dev/null
    elif [[ "${1}" = "mute_stdout_and_stderr" ]]; then
        "$sphinx_build" "$source_dir" "$build_dir" &> /dev/null
    else
        "$sphinx_build" "$source_dir" "$build_dir" | pre
    fi
}