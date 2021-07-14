#!/usr/bin/env bash

# This is run every time the docker container starts up.

set -e

# Trace and log if TRACE_ON is set
[[ ${TRACE_ON} ]] && set -x && export PS4='+ [${BASH_SOURCE##*/}:${LINENO}] '

# https://stackoverflow.com/questions/5947742/how-to-change-the-output-color-of-echo-in-linux
if [[ $(tput colors) -ge 8 ]]; then
    # LCOV_EXCL_START
    declare -x c_red=$(tput setaf 1)
    declare -x c_none=$(tput sgr0) # Keep this last so TRACE=true does not cause everything to be cyan
    # LCOV_EXCL_STOP
fi

say() { echo -e "$1"; }
# https://stackoverflow.com/a/25515370
yell() { >&2 say "$0: ${c_red}$*${c_none}"; }
die() {
    # LCOV_EXCL_START
    yell "$1"
    exit 112
    # LCOV_EXCL_STOP
}
try() { "$@" || die "${c_red}ERROR: could not run [$*]${c_none}" 112; }

[[ $PROJECT_ROOT ]] || die "Environment variable PROJECT_ROOT was not set. It should be set inside the Dockerfile"

STEP_CONFIG_FILE=${STEP_CONFIG_FILE:-/step-config.json}
DOCKERFILES_ROOT=${DOCKERFILES_ROOT:-/dockerfiles}
BAKERY_SCRIPTS_ROOT=${BAKERY_SCRIPTS_ROOT:-$PROJECT_ROOT/output-producer-service/bakery/src}
PYTHON_VENV_ROOT=${PYTHON_VENV_ROOT:-$PROJECT_ROOT/venv}
RECIPES_ROOT=${RECIPES_ROOT:-$PROJECT_ROOT/recipes}
MATHIFY_ROOT=${MATHIFY_ROOT:-$PROJECT_ROOT/mathify}
CNX_RECIPES_RECIPES_ROOT=${CNX_RECIPES_RECIPES_ROOT:-$PROJECT_ROOT/cnx-recipes/recipes/output}
CNX_RECIPES_STYLES_ROOT=${CNX_RECIPES_STYLES_ROOT:-$PROJECT_ROOT/cnx-recipes/styles/output}
XHTML_VALIDATOR_ROOT=${XHTML_VALIDATOR_ROOT:-$PROJECT_ROOT/xhtml-validator/build/libs}

source $PYTHON_VENV_ROOT/bin/activate

function ensure_arg() {
    local arg_name
    local pointer
    local value
    arg_name=$1
    message=${2:-"Environment variable '$arg_name' is missing. Set it"}
    pointer=$arg_name # https://stackoverflow.com/a/55331060
    value="${!pointer}"
    [[ $value ]] || die "$message"
}

function check_input_dir() {
    [[ $1 ]] || die "This function takes exactly one argument and it is missing"
    pointer=$1 # https://stackoverflow.com/a/55331060
    dir_name="${!pointer}"
    [[ -d $dir_name ]] || die "Expected directory to exist but it did not ($1='$dir_name'). Maybe an earlier step needs to run."
}
function check_output_dir() {
    [[ $1 ]] || die "This function takes exactly one argument and it is missing"
    pointer=$1 # https://stackoverflow.com/a/55331060
    dir_name="${!pointer}"
    [[ $dir_name ]] || die "This output directory name is not set ($1='$dir_name')"
    # Auto-create directories only in local dev mode. In Concourse Pip}elines these directories should already exist.
    if [[ $dir_name =~ \/data\/ && ! -d $dir_name ]]; then
        try mkdir -p $dir_name
    fi
    [[ -d $dir_name ]] || die "Expected output directory to exist but it was missing ($1='$dir_name'). it needs to be added to the concourse job"
}

function do_xhtml_validate() {
    failure=false
    dir_name=$1
    file_pattern=$2
    check=$3
    for xhtmlfile in $(find $dir_name -name "$file_pattern")
    do
        try java -cp $XHTML_VALIDATOR_ROOT/xhtml-validator.jar org.openstax.xml.Main "$xhtmlfile" $check broken-link || failure=true
    done
    if $failure; then
        exit 1 # LCOV_EXCL_LINE
    fi
}

function parse_book_dir() {
    check_input_dir IO_BOOK

    ARG_RECIPE_NAME="$(cat $IO_BOOK/style)"
    [[ -f $IO_BOOK/pdf_filename ]] && ARG_TARGET_PDF_FILENAME="$(cat $IO_BOOK/pdf_filename)"
    [[ -f $IO_BOOK/collection_id ]] && ARG_COLLECTION_ID="$(cat $IO_BOOK/collection_id)"
    [[ -f $IO_BOOK/server ]] && ARG_ARCHIVE_SERVER="$(cat $IO_BOOK/server)"
    [[ -f $IO_BOOK/server_shortname ]] && ARG_ARCHIVE_SHORTNAME="$(cat $IO_BOOK/server_shortname)"
    ARG_COLLECTION_VERSION="$(cat $IO_BOOK/version)"

    [[ -f $IO_BOOK/repo ]] && ARG_REPO_NAME="$(cat $IO_BOOK/repo)"
    [[ -f $IO_BOOK/slug ]] && ARG_TARGET_SLUG_NAME="$(cat $IO_BOOK/slug)"
    ARG_GIT_REF="$(cat $IO_BOOK/version)"
}

# Concourse-CI runs each step in a separate process so parse_book_dir() needs to
# reset between each step
function unset_book_vars() {
    unset ARG_RECIPE_NAME
    unset ARG_TARGET_PDF_FILENAME
    unset ARG_COLLECTION_ID
    unset ARG_ARCHIVE_SERVER
    unset ARG_ARCHIVE_SHORTNAME
    unset ARG_COLLECTION_VERSION
    unset ARG_REPO_NAME
    unset ARG_TARGET_SLUG_NAME
    unset ARG_GIT_REF
}

function do_step() {
    step_name=$1

    case $step_name in
        --help)
            steps=$(jq -r ".steps|keys" < $STEP_CONFIG_FILE)
            pipelines=$(jq -r ".pipelines|keys" < $STEP_CONFIG_FILE)
            say "Valid arguments are:\n$steps\n$pipelines"
            return
        ;;
        shell | '/bin/bash' | '/bin/sh')
            bash # LCOV_EXCL_LINE
            return # LCOV_EXCL_LINE
        ;;
        local-create-book-directory)
            # This step is normally done by the concourse resource but for local development it is done here

            collection_id=$2 # repo name or collection id
            recipe=$3
            version=$4 # repo branch/tag/commit or archive collection version
            archive_server=${5:-cnx.org}

            ensure_arg collection_id 'Specify repo name (or archive collection id)'
            ensure_arg recipe 'Specify recipe name'
            ensure_arg version 'Specify repo/branch/tag/commit or archive collection version (e.g. latest)'
            ensure_arg archive_server 'Specify archive server (e.g. cnx.org)'

            [[ -d $INPUT_SOURCE_DIR ]] || mkdir $INPUT_SOURCE_DIR

            check_output_dir INPUT_SOURCE_DIR

            # Write out the files
            echo "$collection_id" > $INPUT_SOURCE_DIR/collection_id
            echo "$recipe" > $INPUT_SOURCE_DIR/collection_style
            echo "$version" > $INPUT_SOURCE_DIR/version
            echo "$archive_server" > $INPUT_SOURCE_DIR/content_server
            # Dummy files
            echo '-123456' > $INPUT_SOURCE_DIR/id # job_id
            echo '{"content_server":{"name":"not_a_real_job_json_file"}}' > $INPUT_SOURCE_DIR/job.json

            return
        ;;
        look-up-book)
            ensure_arg INPUT_SOURCE_DIR

            check_input_dir INPUT_SOURCE_DIR
            check_output_dir IO_BOOK
            
            tail $INPUT_SOURCE_DIR/*
            cp $INPUT_SOURCE_DIR/id $IO_BOOK/job_id
            cp $INPUT_SOURCE_DIR/version $IO_BOOK/version
            cp $INPUT_SOURCE_DIR/collection_style $IO_BOOK/style

            # Detect if this is a git book or an archive book.
            # Git books have at least one slash in the collection_id
            temp_collection_id=$(cat $INPUT_SOURCE_DIR/collection_id)
            if [[ $temp_collection_id == */* ]]; then
                # Git book
                if [[ $(cat $INPUT_SOURCE_DIR/collection_id | awk -F'/' '{ print $3 }') ]]; then
                    cat $INPUT_SOURCE_DIR/collection_id | awk -F'/' '{ print $1 "/" $2 }' > $IO_BOOK/repo
                    cat $INPUT_SOURCE_DIR/collection_id | awk -F'/' '{ print $3 }' | sed 's/ *$//' > $IO_BOOK/slug
                else
                    # LCOV_EXCL_START
                    cat $INPUT_SOURCE_DIR/collection_id | awk -F'/' '{ print $1 }' > $IO_BOOK/repo
                    cat $INPUT_SOURCE_DIR/collection_id | awk -F'/' '{ print $2 }' | sed 's/ *$//' > $IO_BOOK/slug
                    # LCOV_EXCL_STOP
                fi
                pdf_filename="$(cat $IO_BOOK/slug)-$(cat $IO_BOOK/version)-git-$(cat $IO_BOOK/job_id).pdf"
                echo "$pdf_filename" > $IO_BOOK/pdf_filename
            else
                # Archive book
                cp $INPUT_SOURCE_DIR/collection_id $IO_BOOK/collection_id
                cp $INPUT_SOURCE_DIR/content_server $IO_BOOK/server

                server_shortname="$(cat $INPUT_SOURCE_DIR/job.json | jq -r '.content_server.name')"
                echo "$server_shortname" >$IO_BOOK/server_shortname
                pdf_filename="$(cat $IO_BOOK/collection_id)-$(cat $IO_BOOK/version)-$(cat $IO_BOOK/server_shortname)-$(cat $IO_BOOK/job_id).pdf"
                echo "$pdf_filename" > $IO_BOOK/pdf_filename
            fi
            
            return
        ;;
    esac

    # Check that the input dirs, output dirs, and environment variables are set before running the step:

    step_entry=$(jq  -r ".steps.\"$step_name\"|not|not" < $STEP_CONFIG_FILE)

    if [[ "$step_entry" == 'false' ]]; then
        die "ERROR: Could not find step or pipeline named '$step_name'. Type --help to see a list of valid steps" # LCOV_EXCL_LINE
    else
        input_dirs=$(jq  -r ".steps.\"$step_name\".inputDirs|@sh"  < $STEP_CONFIG_FILE)
        output_dirs=$(jq -r ".steps.\"$step_name\".outputDirs|@sh" < $STEP_CONFIG_FILE)
        required_envs=$(jq -r ".steps.\"$step_name\".requiredEnv|@sh" < $STEP_CONFIG_FILE)

        for required_env in $required_envs; do
            ensure_arg $(echo $required_env | tr -d "'")
        done        
        for input_dir in $input_dirs; do
            check_input_dir $(echo $input_dir | tr -d "'")
        done
        for output_dir in $output_dirs; do
            check_output_dir $(echo $output_dir | tr -d "'")
        done
    fi

    step_file="$DOCKERFILES_ROOT/steps/$step_name.bash"

    if [[ -f $step_file ]]; then
        source $step_file
    else
        die "Invalid command. The first argument needs to be a command like 'fetch'. Instead, it was '${step_name}'" # LCOV_EXCL_LINE
    fi
}

function do_step_named() {
    step_name=$1
    if [[ $START_AT_STEP == $step_name ]]; then
        unset START_AT_STEP
    elif [[ $START_AT_STEP ]]; then
        say "==> Skipping $*"
    fi
    if [[ $STOP_AT_STEP == $step_name ]]; then
        say "==> Done because STOP_AT_STEP='${STOP_AT_STEP}'"
        # Ensure no other steps run by setting START_AT_STEP to something invalid
        START_AT_STEP='__nonexistent_step__'
        exit 0
    fi
    if [[ ! $START_AT_STEP ]]; then
        say "==> Starting: $*"
        do_step $@
        unset_book_vars
        say "==> Finished: $*"
    fi
}


# Try to find if the command is in the pipeline first
first_arg=$1
pipeline_steps=$(jq -r ".pipelines.\"$first_arg\"|@sh" < $STEP_CONFIG_FILE)

if [[ $pipeline_steps = 'null' ]]; then
    do_step_named $(echo $first_arg | tr -d "'")
else
    do_step_named local-create-book-directory "${@:2}"
    do_step_named look-up-book
    
    for step_name in $pipeline_steps; do
        do_step_named $(echo $step_name | tr -d "'")
    done
fi
