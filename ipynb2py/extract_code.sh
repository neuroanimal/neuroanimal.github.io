#!/bin/bash -f
echo "+============================================================================+"
echo "| Code Extractor from (iPython / Jupyter / JupyterLab / JupyterHub) Notebook |"
echo "| (A) (C) (TM) 2026 by Grzegorz Stadnik NEUROANIMAL                          |"
echo "| For more information go to website: https://neuroanimal.github.io/         |"
echo "+============================================================================+"
echo ""
if [[ "${1}" == "" ]]; then
    echo -e "Usage:\n  $SHELL $0 INPUT_FILE"
    exit
fi
STA=$(date +"%Y%m%d_%H%M%S")
INP="$1" # "exercise_2_6.ipynb"
NAM="${INP%.*}"
EXT="${INP##*.}"
LEN=$(yq --input-format json --output-format yaml --indent 2 ".cells | length" "${INP}")
ALL="${NAM}_${STA}_all.py"
DON="no"
echo "Found ${LEN} codes in input file ${INP}"
for ((IND=0;IND<LEN;IND++)); do
  IDX=$(printf "%03d" "${IND}")
  OUT="${NAM}_${STA}_${IDX}.ipy"
  OMD="${NAM}_${STA}_${IDX}.md"
  OTX="${NAM}_${STA}_${IDX}.txt"
  WHE=".cells[${IND}].source"
  TYP=".cells[${IND}].cell_type"
  TPE=$(yq --input-format json --output-format yaml --indent 2 "${TYP}" "${INP}")
  if [[ "${TPE}" == "code" ]]; then
    echo -e "  Write ${TPE} ${IND} to output file ${OUT} with:\n    yq --input-format json --output-format yaml --indent 2 \"${WHE}\" \"${INP}\" > \"${OUT}\""
    yq --input-format json --output-format yaml --indent 2 "${WHE}" "${INP}" > "${OUT}"
    printf "##### SOURCE ${IDX} OF TYPE ${TPE^^} #####\n\n" >> "${ALL}"
    yq --input-format json --output-format yaml --indent 2 "${WHE}" "${INP}" | sed -r "s_(^[!])_# \1_" >> "${ALL}"
    printf "\n\n" >> "${ALL}"
    DON="yes"
  elif [[ "${TPE}" == "markdown" ]]; then
    echo -e "  Write ${TPE} ${IND} to output file ${OUT} with:\n    yq --input-format json --output-format yaml --indent 2 \"${WHE}\" \"${INP}\" > \"${OMD}\""
    yq --input-format json --output-format yaml --indent 2 "${WHE}" "${INP}" > "${OMD}"
    printf "##### SOURCE ${IDX} OF TYPE ${TPE^^} #####\n\n" >> "${ALL}"
    yq --input-format json --output-format yaml --indent 2 "${WHE}" "${INP}" | sed -r "s_^_  # _g" >> "${ALL}"
    printf "\n\n" >> "${ALL}"
  else
    echo -e "  Write ${TPE} ${IND} to output file ${OUT} with:\n    yq --input-format json --output-format yaml --indent 2 \"${WHE}\" \"${INP}\" > \"${OTX}\""
    yq --input-format json --output-format yaml --indent 2 "${WHE}" "${INP}" > "${OTX}"
    printf "##### SOURCE ${IDX} OF TYPE ${TPE^^} #####\n\n" >> "${ALL}"
    yq --input-format json --output-format yaml --indent 2 "${WHE}" "${INP}" | sed -r "s_^_  ## _g" >> "${ALL}"
    printf "\n\n" >> "${ALL}"
  fi
  if [[ `expr ${IND} + 1` -eq ${LEN} ]]; then
    echo "  Written also all above codes into overal output file ${ALL}"
  fi
done
if [[ "${DON}" == "yes" ]]; then
  isort --float-to-top "${ALL}"
  ruff check --select E402,I001,RUF022 --fix --unsafe-fixes "${ALL}"
  ruff format "${ALL}"
  cat "${ALL}" | grep -E "([!]|[%])pip install " | awk -F"pip install " '{ print($2" "); }' | sed "s/-q //g" | tr -s " " "\n" >> requirements.txt
  cat requirements.txt | tee | sort | uniq > requirements.txt
fi
echo "Finished processing input file ${INP} and produced at least ${LEN} output files"
echo ""
