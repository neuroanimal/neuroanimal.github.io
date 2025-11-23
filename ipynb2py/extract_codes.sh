#!/bin/bash -f
DIR=${1}
SCRIPT_PATH=$(dirname ${BASH_SOURCE[0]})"/extract_code.sh"
# echo "Internal script location: ${SCRIPT_PATH}"
# exit
if [[ "${DIR}" == "" ]]; then
  DIR="${PWD}"
fi
ls -1 "$DIR"/*.ipynb | xargs -Ixxx sh "${SCRIPT_PATH}" "xxx"
# ls -1 *_all.py | awk -F"[.]py" '{ fin=$0; fout=$1"_reformatted.py"; cmd1="cat "fin; cmd2="sed -r \"s_(\x5e[ ]*[-]{1})_# \\\\1_\""; cmd3="sed -r \"s_(\x5e[\x21])_# \\\\1_\""; cmd4="ruff format -"; cmd=cmd1" | "cmd2" | "cmd3" | "cmd4" > "fout; print("  Reformatted "fin" to "fout" with:\n    "cmd); system(cmd); }'
