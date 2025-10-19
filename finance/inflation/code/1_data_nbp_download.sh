#!/bin/bash -f
pushd data/nbp
wget https://static.nbp.pl/dane/kursy/Archiwum/archiwum_tab_a_2025.csv
wget https://static.nbp.pl/dane/kursy/Archiwum/archiwum_tab_a_2025.xls
popd

