#!/usr/bin/python3

### Author: ESTAGRZ (Grzegorz.Stadnik@Ericsson.COM)
### Date: 2024-05-17 01:20

###############
# Preparation #
###############

### 3PP dependencies

import json
import re
import sys

from collections import Counter
from pathlib import Path
from IPython.display import display

import numpy as np
import pandas as pd
import dask.dataframe as dd
import spacy as spacy

from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer

# !{sys.executable} -m spacy download en
# nlp = spacy.load("")
# nlp = spacy.load("en")

# spacy.load('en')
# exit(0)
nlp = spacy.load("en_core_web_sm")
# spacy.load('en_core_web_sm')
# exit(0)

# import en
# nlp = en.load()
# exit(0)

# import en_core_web_sm
# nlp = en_core_web_sm.load()
# exit(0)

from spacy import displacy
from spacy.lang.en.stop_words import STOP_WORDS
from spacy.matcher import Matcher
from spacy.util import filter_spans

### Show welcome message

print("Applied Data Science SILO.AI Camp")
print()
print("Ericsson Cohort: 15th")
print("February 19th - May 22nd, 2024")
print("Team: 3B, Project 4: TS_Advisor")
print()
print("Author: ESTAGRZ")
print()

### Flags

debug = False
use_sample_dataset = True
use_full_dataset = False

### Path variables definition

cur_dir = Path.cwd()
par_dir = cur_dir.parent
cod_dir = par_dir / "code"
dat_dir = par_dir / "data"
inp_dir = dat_dir / "input"
med_dir = dat_dir / "intermediate"
out_dir = dat_dir / "output"
plt_dir = out_dir / "plots"

### Path variables showing

print(f"Parent dir: {par_dir}")
print(f"Current dir: {cur_dir}")
print(f"Code dir: {cod_dir}")
print(f"Data dir: {dat_dir}")
print(f"Data Input dir: {inp_dir}")
print(f"Data Intermediate dir: {med_dir}")
print(f"Data Output dir: {out_dir}")
print(f"Data Output Plots dir: {plt_dir}")

### Create dirs if missing

plt_dir.mkdir(parents=True, exist_ok=True)

### Define input files

if use_sample_dataset:
    trs_sample_path = inp_dir / '4G5G_trr_trs_20000_sample.csv'
if use_full_dataset:
    trs_full_path = inp_dir / '4G5G_trr_trs_20000.csv.zip'
mho_grp_map_path = inp_dir / '4G5G_trr_trs_20000_MHO_Groups.json'

###################
# Read input data #
###################

### Read TRs sample CSV file

## Attempt 1:

# trs_sample = pd.read_csv(trs_sample_path, low_memory=False)

## Attempt 2:

# df = pd.DataFrame()
# trs_sample = df.to_csv(trs_sample_path)

## Attempt 3:

# print(f'Reading input file: {trs_sample_path}')
# trs_sample_bin = open(trs_sample_path, mode='rb').read()
# trs_sample_str = trs_sample_bin.decode("UTF-8", "replace")
# trs_sample_cols = trs_sample_str.split("\n")[0].split(",")
# # display(trs_sample_bin)
# # exit(0)
# # display(trs_sample_str)
# # exit(0)
# print('Columns detected:')
# display(trs_sample_cols)
# # exit(0)
# ## trs_sample = pd.read_csv(trs_sample_path, usecols=trs_sample_cols, low_memory=False, quoting=2, doublequote=False, encoding_errors='ignore')
# trs_sample_ddf = dd.read_csv(trs_sample_path, usecols=trs_sample_cols)
# ## trs_sample = trs_sample_ddf.compute()
# trs_sample_parts = trs_sample_ddf.map_partitions(lambda x:x.to_dict(orient="records"))
# trs_sample_ds = list(trs_sample_parts)
# trs_sample = pd.DataFrame(trs_sample_ds)
# display(trs_sample.head(3))
# exit(0)

## Attempt 4:

if use_sample_dataset:
    print("Reading TRs sample data-set:", end='')
    trs_sample = pd.read_csv(trs_sample_path, engine='python', encoding='utf-8', on_bad_lines='skip')
    print(" DONE")

### Read TRs full CSV file

if use_full_dataset:
    print("Reading TRs full data-set:", end='')
    trs_full = pd.read_csv(trs_full_path, compression='zip', low_memory=False)
    print(" DONE")

### Read MHO groups mappings JSON file

print("Reading MHO groups mappings:", end='')
# mho_grp_map = pd.read_json(mho_grp_map_path)
mho_grp_map_file = open(mho_grp_map_path, "r")
mho_grp_map = json.load(mho_grp_map_file)
print(" DONE")

### Apply mappings from MHO group to MHO as subsystem

def get_subsystem(row):
    mho = row['Faulty product.Design Responsible MHO']
    if mho in mho_grp_map:
        return mho
    for key, value in mho_grp_map.items():
        if any(mho == v for v in value):
            return key
    return None

def add_subsystem(trs):
    trs['subsystem'] = trs.apply(get_subsystem, axis=1)

#######################
# Feature Engineering #
#######################

### Remove duplicate TRs

def drop_duplets(trs):
    uniq_TRs = trs['General.Eriref'].unique()
    for TR_id in uniq_TRs:
        TRs_with_id = trs[trs['General.Eriref'] == TR_id]
        len_TRs_with_id = len(TRs_with_id)
        if len_TRs_with_id < 2:
            continue
        TRs_duples = TRs_with_id['General.Duplicate TRs'].sort_values()
        TRs_duples_str = str(list(TRs_duples))
        for idx, row in TRs_with_id.iterrows():
            trs.loc[idx, 'General.Duplicate TRs'] = TRs_duples_str
    trs = trs.drop_duplicates()
    return trs

if use_sample_dataset:
    trs_sample_ori_len = len(trs_sample)
    print("Removing duplicates from sample data-set:", end='')
    trs_sample = drop_duplets(trs_sample)
    print(" DONE")
    trs_sample_cls_len = len(trs_sample)
    print(f'\tNumber of rows before removing duplicated rows: {trs_sample_ori_len}')
    print(f'\tNumber of rows after removing duplicated rows: {trs_sample_cls_len}')

if use_full_dataset:
    trs_full_ori_len = len(trs_full)
    print("Removing duplicates from full data-set:", end='')
    trs_full = drop_duplets(trs_full)
    print(" DONE")
    trs_full_cls_len = len(trs_full)
    print(f'\tNumber of rows before removing duplicated rows: {trs_full_ori_len}')
    print(f'\tNumber of rows after removing duplicated rows: {trs_full_cls_len}')

### Add subsystem column

if use_sample_dataset:
    print("Adding mapped MHO subsystem column to sample data-set:", end='')
    add_subsystem(trs_sample)
    print(" DONE")

if use_full_dataset:
    print("Adding mapped MHO subsystem column to full data-set:", end='')
    add_subsystem(trs_full)
    print(" DONE")

### Convert text data to features

unsupported_titles = []
title_mappings = {
    # sections
    '': "PRE",
    'EFFECT': "SUM",
    'TROUBLEDESCRIPTION': "SUM",
    'TROUBLE DESCRIPTION': 'SUM',
    'MEASURES': "MEAS",
    'MISC ': "MISC",
    'MISC (Not valid for Maintenance TRs)': "MISC",
    'M I S C  (Not valid for Maintenance TRs)': "MISC",
    'CSR Consultation': "CONSULT",
    'CSR Consultation (Mandatory for maintenance application TRs)': "CONSULT",
    'Feature details': "FEAT",
    'Feature details (Mandatory for Feature Verification TRs)': "FEAT",
    'Suspected Duplicates': "DUPLE",
    'Hardware Inventory': 'HW',
    'Hardware Inventory (invh)': 'HW',
    'Information from core network:': "CN",
    'PMD Stack Trace': "TRACE.pmg_gcpu",
    'Trace And Error': "TRACE.pmg_gcpu",
    'Trace And Error (from PMD and GCPU dump if applicable)': "TRACE.pmg_gcpu",
    'Logs (lgaoevspm)': "LOG.lgao",
    'CDAE Output': "OUT.cdae",
    'Llog output': "LOG.llog",
    'Llog output (llog -l)': "LOG.llog",
    'lgg output': "OUT.lgg_lgp",
    'lgp output': "OUT.lgg_lgp",
    'lgg/lgp output': "OUT.lgg_lgp",
    # subsections
    'Trouble Summary': "sum",
    'Trouble summary': "sum",
    'Trouble summary and/or commercial effect': "sum",
    'Trouble description': "sum",
    'Trouble Description': "sum",
    'Trouble Description and commercial effect': "sum",
    'Trouble Description and Commercial effect': "sum",
    'Trouble Description and Commercial Effect': "sum",
    'Commercial effect': "sum",
    'Commercial Effect': "sum",
    'Earlier projects/releases': "ver_ok",
    'Last working SW version': "ver_ok",
    'Last working SW version, where the fault has NOT been seen': "ver_ok",
    'Last working SW version (Upgrade Package or Lm etc), where the fault has NOT been see': "ver_ok",
    'Last working SW version (Upgrade Package or Lm etc), where the fault has NOT been seen': "ver_ok",
    'Last working SW version (Upgrade Package or LM etc.), where the KPI deviation has NOT been seen': "ver_ok",
    'Project impact': "impact",
    'Observed System impact': "impact",
    'Condition': "cond",
    'Conditions': "cond",
    'Detailed trouble description': "descr",
    'Configuration Data': "cfg",
    'Troubleshooting': "cfg",
    'Troubleshooting Data': "cfg",
    'Troubleshooting Data Collection': "cfg",
    'Configuration and Troubleshooting Dat': "cfg",
    'Configuration and Troubleshooting Data': "cfg",
    'Frequency of fault': "freq",
    'Frequency of fault (fails/trials)': "freq",
    'Frequency and number of nodes affecte': "freq",
    'Frequency and number of nodes affected': "freq",
    'Is the fault reproducible': "reprod_can",
    'Is the fault reproducible?': "reprod_can",
    'Step-by-step procedure in order to reproduce the fault': "reprod_how",
    'Steps to reproduc': "reprod_how",
    'Steps to reproduce': "reprod_how",
    'Workaround': "workar",
    'Recovery': "workar",
    'Workaround and Recover': "workar",
    'Workaround and Recovery': "workar",
}


def map_subsec_title(title, debug=False):
    if not title in title_mappings:
        if debug:
            print(f'WARNING! Unsupported mapping for (sub)section title: {title}')
        if not title in unsupported_titles:
            unsupported_titles.append(title)
        return None
    return title_mappings[title]


def extract_subsec_info(sec_level, row_offset, row_str_curr, row_str_next, title=True, sepa=r'^([=\-_]{3,})$', debug=False):

    skip_next_row = False
    row_header_start = row_offset
    row_header_end = row_offset
    final_title = None

    regex_prefix = '([0-9]{1,2})(?:[._]{1})' * sec_level
    regex_affix = '([0-9]{1,2})(?:[._]{0,1})'
    regex_suffix = '([ \t]{1,})(.*)'
    regex_full = f'^{regex_prefix}{regex_affix}{regex_suffix}$'
    regex_pattern = re.compile(regex_full)
    if debug:
        print(f"Subsection regex: {regex_pattern}")

    subsec_l1_lvl = sec_level + 1

    subsec_l1_sep = None
    if not row_str_next is None:
        regex_sepa_str = sepa
        regex_sepa_pattern = re.compile(regex_sepa_str)
        subsec_l1_sep = re.match(regex_sepa_pattern, row_str_next)
        if debug:
            print(f"Subsection separator regex: {regex_sepa_pattern}")
            print(f"Subsection separator matched? {subsec_l1_sep}")

    subsec_l1_num = re.match(regex_pattern, row_str_curr)
    if not subsec_l1_num is None:

        row_header_start = row_offset
        
        for level in range(1, subsec_l1_lvl + 1):
            subsec_li_number = subsec_l1_num.group(level)
            if debug:
                print(f"Subsection level {level} number: '{subsec_li_number}'")
            
        subsec_l1_delim = subsec_l1_num.group(subsec_l1_lvl + 1)
        if debug:
            print(f"Subsection delimiter: '{subsec_l1_delim}'")
            
        subsec_l1_title = subsec_l1_num.group(subsec_l1_lvl + 2)
        if debug:
            print(f"Subsection title original : '{subsec_l1_title}'")

        subsec_l1_title_no_ws = subsec_l1_title.strip()
        subsec_l1_title_no_ws_match = re.match(r'(([A-Z]{1})(?:[ ]{1})([ ]{0,}))+', subsec_l1_title.strip() + " ")
        if not subsec_l1_title_no_ws_match is None:
            subsec_l1_title_no_ws = subsec_l1_title_no_ws_match.group(0)
            subsec_l1_title_no_ws_new = ''
            skip_space = False
            for index in range(0, len(subsec_l1_title_no_ws)):
                if skip_space:
                    skip_space = False
                    continue
                char_curr = subsec_l1_title_no_ws[index]
                if index + 1 < len(subsec_l1_title_no_ws):
                    char_next = subsec_l1_title_no_ws[index + 1]
                else:
                    char_next = None
                if char_curr >= 'A' and char_curr <= 'Z' and char_next == ' ':
                    subsec_l1_title_no_ws_new += char_curr
                    skip_space = True
                else:
                    subsec_l1_title_no_ws_new += char_curr
            subsec_l1_title_no_ws = subsec_l1_title_no_ws_new
        if debug:
            print(f"Subsection title cleaned  : '{subsec_l1_title_no_ws}'")

        if title:
            subsec_l1_title_mapped = map_subsec_title(subsec_l1_title_no_ws)
            if debug:
                print(f"Subsection title mapped   : '{subsec_l1_title_mapped}'")
            final_title = subsec_l1_title_mapped
        else:
            final_title = subsec_l1_title_no_ws

        row_header_end = row_header_start

        if not subsec_l1_sep is None:
            subsec_l1_separator = subsec_l1_sep.group(1)
            if debug:
                print(f"Subsection title separator: '{subsec_l1_separator}'")
            skip_next_row = True
            row_header_end += 1

        row_content_start = row_header_end + 1
        
        if debug:
            print(f"Subsection header start row   : {row_header_start}")
            print(f"Subsection header ending row  : {row_header_end}")
            print(f"Subsection content start row  : {row_content_start}")
            # print(f"Row offset for subsection content ending : {row_content_end}")
            
        #     print("Subsection content:")
        #
        # else:
        #     print(f"Subsection content row: {row_str_curr}")
    
    return skip_next_row, final_title, row_header_start, row_header_end


def extract_info_from_text(obs, debug=False):
    tree = {}
    rows = obs.splitlines()
    skip_next_row = False
    current_title = None
    current_title0 = None
    current_title1 = None
    current_title2 = None
    current_title3 = None
    current_section = None
    current_subsection = None
    current_subsubsection = None
    previous_section = None
    previous_subsection = None
    previous_subsubsection = None
    for row_offset in range(0, len(rows)):
        if skip_next_row:
            skip_next_row = False
            continue
        row_str_prev = None
        row_str_curr = None
        row_str_next = None
        if row_offset - 1 >= 0:
            row_str_prev = rows[row_offset - 1]
        row_str_curr = rows[row_offset + 0]
        if row_offset + 1 < len(rows):
            row_str_next = rows[row_offset + 1]
        if debug:
            print(f'Row prev: {row_str_prev}')
            print(f'Row curr: {row_str_curr}')
            print(f'Row next: {row_str_next}')
            print(f'')

        title = True  # not row_looks_as_content
        skip_next_row0, final_title0, row_header_start0, row_header_end0 = extract_subsec_info(0, row_offset, row_str_curr, row_str_next, title=title, debug=debug)
        skip_next_row1, final_title1, row_header_start1, row_header_end1 = False, None, row_offset, row_offset
        skip_next_row2, final_title2, row_header_start2, row_header_end2 = False, None, row_offset, row_offset
        skip_next_row3, final_title3, row_header_start3, row_header_end3 = False, None, row_offset, row_offset
        if not final_title0:
            skip_next_row1, final_title1, row_header_start1, row_header_end1 = extract_subsec_info(1, row_offset, row_str_curr, row_str_next, title=title, debug=debug)
            if not final_title1:
                skip_next_row2, final_title2, row_header_start2, row_header_end2 = extract_subsec_info(2, row_offset, row_str_curr, row_str_next, title=title, debug=debug)
                if not final_title2:
                    skip_next_row3, final_title3, row_header_start3, row_header_end3 = extract_subsec_info(3, row_offset, row_str_curr, row_str_next, title=title, debug=debug)
                else:
                    current_subsubsection = final_title2
            else:
                current_subsection = final_title1
                current_subsubsection = None
        else:
            current_section = final_title0
            current_subsection = None
            current_subsubsection = None

        skip_next_row = skip_next_row0 or skip_next_row1 or skip_next_row2 or skip_next_row3
        row_header_start = min(row_header_start0, row_header_start1, row_header_start2, row_header_start3)
        row_header_end = max(row_header_end3, row_header_end2, row_header_end1, row_header_end0)
        row_content_start = row_header_end + 1

        content_has_finished = False
        we_took = False
        if not content_has_finished:
            row_looks_as_content = True
            if final_title0 is None:
                if not we_took:
                    final_title0 = current_title0
                    # we_took = 1
            else:
                current_title0 = final_title0
                row_looks_as_content = False
            if final_title1 is None:
                if not we_took:
                    # if final_title0 == current_title0:
                    final_title1 = current_title1
                    # we_took = 2
            else:
                current_title1 = final_title1
                row_looks_as_content = False
            if debug:
                if f"{final_title0}.{final_title1}" in ['CONSULT.workar', 'MEAS.reprod_how']:
                    print(f'DEBUG1: final_title0 == {final_title0}')
                    print(f'DEBUG1: final_title1 == {final_title1}')
                    print(f'DEBUG1: current_title0 == {current_title0}')
                    print(f'DEBUG1: current_title1 == {current_title1}')
            if final_title0 == current_title0 and final_title1 == current_title1 and current_title1 != current_title0:
                current_title1 = None
            if debug:
                if f"{final_title0}.{final_title1}" in ['CONSULT.workar', 'MEAS.reprod_how']:
                    print(f'DEBUG2: final_title0 == {final_title0}')
                    print(f'DEBUG2: final_title1 == {final_title1}')
                    print(f'DEBUG2: current_title0 == {current_title0}')
                    print(f'DEBUG2: current_title1 == {current_title1}')

        if row_looks_as_content == True:
            if current_title is not None:
                final_title = current_title
            else:
                final_title = 'PRE'
        elif not final_title3 is None:
            final_title = f"{final_title0}.{final_title1}.{final_title2}.{final_title3}"
        elif not final_title2 is None:
            final_title = f"{final_title0}.{final_title1}.{final_title2}"
        elif not final_title1 is None:
            final_title = f"{final_title0}.{final_title1}"
        elif not final_title0 is None:
            final_title = f"{final_title0}"
        else:
            if debug:
                print("Warning! Cannot identify title")
            continue

        if debug:
            print(f'Row identified as content            : {row_looks_as_content}')
            print(f'Row identified header / title        : {final_title}')
            print(f'Row offset for section header start  : {row_header_start}')
            print(f'Row offset for section header ending : {row_header_end}')
            print(f'Row offset for section content start : {row_content_start}')

        cnt = ""
        if row_looks_as_content == True:
            if debug:
                print(f'Content of the (sub)section row      : {row_str_curr}')
            cnt = row_str_curr
            previous_subsubsection = current_subsubsection
            previous_subsection = current_subsection
            previous_section = current_section
        else:
            current_title = final_title

        if debug:
            print(f'')

        if not final_title in tree:
            tree[final_title] = ""
        tree[final_title] += cnt + "\n"

    tree_new = {}
    for (key, value) in tree.items():
        value = value.strip("\r\n\t ")
        if value:
            tree_new[key] = value
    return tree_new


def pretty(_dict):
    json_str = json.dumps(_dict, indent=2)
    return json_str.replace("\\n", "\n")


def p(_obj):
    return display(pretty(_obj))


if use_sample_dataset:
    trs = trs_sample
    tmp = extract_info_from_text(trs_sample['Observation.Observation'][4])

if use_full_dataset:
    trs = trs_full
    tmp = extract_info_from_text(trs_sample['Observation.Observation'][12])

MHO_FULL_DF = trs  ##########

# p(tmp)
# p(unsupported_titles)

all_keys = []
for idx in trs.index:
    tree = extract_info_from_text(str(trs['Observation.Observation'][idx]))
    for key in tree.keys():
        if not key in all_keys:
            all_keys.append(key)

all_keys_last=[]
key_last_mappings = {
    'cdae': 'out',
    'lgg_lgp': 'out',
    'llog': 'log',
    'lgao': 'log',
    'pmg_gcpu': 'trace',
}


def map_key_last(key):
    key_last=key.split('.')[-1].lower()
    if key_last in key_last_mappings:
        key_last = key_last_mappings[key_last]
    key_last=f"txt.{key_last}"
    if not key_last in all_keys_last:
        all_keys_last.append(key_last)
    return key_last


df_tmp = pd.DataFrame(index=all_keys_last).T
all_keys_last = []

# for key in all_keys:
#    df_tmp[key_last] = None
# for idx in MHO_FULL_DF.index:
#     for key in all_keys:
#         # df_tmp[idx] = pd.concat(axis=1) # pd.Series()
#         df_tmp.loc[idx, key_last] = None

for idx in MHO_FULL_DF.index:
    tree = extract_info_from_text(str(MHO_FULL_DF['Observation.Observation'][idx]))
    row_last_kvps = {}
    for key in all_keys:
        # tree[key]
        key_last = map_key_last(key)
        if not key_last in all_keys_last:
            all_keys_last.append(key_last)

        # if key_last in df_tmp.iloc[idx]:
        #     val_prev = df_tmp.loc[idx, key_last]
        # else:
        #     val_prev = None

        if key_last in row_last_kvps:
            val_prev = row_last_kvps[key_last]
        else:
            val_prev = None

        if not key in tree:
            if val_prev is None:
                val = None
            else:
                val = val_prev
        else:
            if val_prev is None:
                val = tree[key]
                # print(f"{key} -> {key_last}:\n{val}\n")
            else:
                val = f"{val_prev}\n\n{tree[key]}"
                # print(f"{key} -> {key_last}:\n{val_prev}\n->\n{val}\n")

        # df_tmp.loc[idx, key_last] = val
        # df_tmp.at[idx, key_last] = val
        row_last_kvps[key_last] = val

        MHO_FULL_DF.loc[idx, key_last] = val


### print("Unsupported section titles detected:")
### p(unsupported_titles)


###################################
# EDA (Exploratory Data Analysis) #
###################################

### Text mining NLP techniques

def tab(doc):
    rows = []
    for token in doc:
        rows.append((token.text, token.lemma_, token.pos_, token.tag_,
                     token.dep_, token.shape_, token.is_alpha, token.is_stop))
    df_out = pd.DataFrame(
        rows,
        columns=["Text", "Lemma", "Coarse POS (pos)", "Fine POS (tag)", "Syntactic dependency", "Shape", "Alphanumeric", "Stop"]
    )
    return df_out

def tab_NP(doc):
    olist = []
    for chunk in doc.noun_chunks:
        olist.append([chunk.text, chunk.label_, chunk.root.text])
    odf = pd.DataFrame(olist)
    odf.columns = ["NounPhrase", "Label", "RootWord"]
    return odf

def tab_VP_old(nlp, doc):
    pattern = [{'POS': 'VERB', 'OP': '?'},
           {'POS': 'ADV', 'OP': '*'},
           {'POS': 'AUX', 'OP': '*'},
           {'POS': 'VERB', 'OP': '+'}]
    # instantiate a Matcher instance
    matcher = Matcher(nlp.vocab)
    matcher.add("Verb phrase", [pattern])
    # call the matcher to find matches 
    matches = matcher(doc)
    spans = [doc[start:end] for _, start, end in matches]
    odf = pd.DataFrame(filter_spans(spans))
    odf.columns = ["VerbPhrase"]
    return odf   


def tab_VP(nlp, doc):
    pattern = [{'POS': 'VERB', 'OP': '?'},
           {'POS': 'ADV', 'OP': '*'},
           {'POS': 'AUX', 'OP': '*'},
           {'POS': 'VERB', 'OP': '+'}]
    # instantiate a Matcher instance
    matcher = Matcher(nlp.vocab)
    matcher.add("Verb phrase", [pattern])
    # call the matcher to find matches 
    matches = matcher(doc)
    spans = [doc[start:end] for _, start, end in matches]
    spans_len = len(spans)
    spans_filtered = filter_spans(spans)
    spans_filtered_len = len(spans_filtered)
    odf = pd.DataFrame(spans_filtered)
    odf_len = len(odf) # odf.count()
    print(f"doc: {doc}, spans_len={spans_len}, spans_filtered_len={spans_filtered_len}, odf_len={odf_len} to {spans_filtered_len}")
    if not odf.empty:
        col = ["VerbPhrase"]
        cols = col * spans_filtered_len
        try:
            odf.columns = col
        except ValueError as ve:
            try:
                odf.columns = cols
            except ValueError as ve:
                odf.reindex(cols, axis=1)
    return odf


def tab_dep(doc):
    olist = []
    for token in doc:
        olist.append([token.text, token.dep_, token.head.text, token.head.pos_,
              [child for child in token.children]])
    odf = pd.DataFrame(olist)
    odf.columns = ["Text", "Dep", "Head text", "Head POS", "Children"]
    return odf

def get_lemmas(doc):
    lemmas = [
        token.lemma_ for token in doc
        if not token.is_punct and not token.is_space and token.lower_ not in STOP_WORDS
    ]
    return lemmas


##### exit(0)



# trs_titles_uniq = trs['General.Heading'].unique()
trs_titles_uniq = trs['txt.sum']


def map_root(word):
    if re.match(r'^[A-Z]+$', word):
        return word
    elif re.match(r'^[a-z]+$', word):
        return word.upper()
    elif re.match(r'^[A-Z]{1}[a-z]+$', word):
        return word.upper()
    elif re.match(r'^([a-z]*)([A-Z]{1}[a-z]+)+$', word):
        # print(f'EXTRACTING WORD: {word}')
        # grouped = re.search(r'^(([A-Z]{1}[a-z]+)+)$', word)
        # for i in range(0, len(grouped.groups())):
        #     group = grouped.group(i)
        #     print(f'\tEXTRACTED FRAGMENT FROM WORD: {group}')
        RE_WORDS = re.compile(r'''
            # Find words in a string. Order matters!
            [a-z]+(?=[A-Z][a-z]) |  # All lower case before a capitalized word
            [a-z]+(?=[A-Z]+)     |  # All lower case before all upper case
            [A-Z]+(?=[A-Z][a-z]) |  # All upper case before a capitalized word
            [A-Z]?[a-z]+ |  # Capitalized words / all lower case
            [A-Z]+ |  # All upper case
            \d+  # Numbers
            ''', re.VERBOSE)
        word_list = RE_WORDS.findall(word)
        ##### print(f'EXTRACTED WORDS: {word} -> {word_list}')
        return str.join(' ', word_list).upper()
    elif re.match(r'^[A-Z]*([a-z]+[A-Z]+)+[a-z]*$', word):
        ##### grouped = re.search(r'^([A-Z]*[a-z]+)(([A-Z]+[a-z]*)+)$', word)
        ##### grp1 = grouped.group(1)
        ##### grp2 = grouped.group(2)
        ##### grp3 = grouped.group(3)
        ##### print(f'INTERESTING WORD: {word} -> {grp1} {grp2} {grp3}')
        return word
    else:
        return word


##### import operator


def sort_dict_by_values_asc(d):
    return dict(sorted(d.items(), key=lambda x: x[1], reverse=False))
    ##### return dict(sorted(d.items(), key=operator.itemgetter(1), reverse=False))


def sort_dict_by_values_desc(d):
    return dict(sorted(d.items(), key=lambda x: x[1], reverse=True))
    ##### return dict(sorted(d.items(), key=operator.itemgetter(1), reverse=True))


roots_all = {}
tr_roots = []
### print("\nMost common 10 words from first 4 rows:")
### countsy = Counter()
for tr_tit in trs_titles_uniq:  # [:300]:
    tr_tit_doc = nlp(tr_tit)
    ##### print(f"TR title: {tr_tit_doc}")
    ### display(tab(tr_tit_doc))
    noun_phrases_and_roots = tab_NP(tr_tit_doc)
    ### display(noun_phrases_and_roots)
    roots = {}
    for i in range(0, len(noun_phrases_and_roots)):
        noun_phrase = noun_phrases_and_roots.iloc[i]['NounPhrase']
        root = map_root(noun_phrases_and_roots.iloc[i]['RootWord'])
        if not root in roots:
            roots[root] = 1
        else:
            roots[root] += 1
    ##### print(roots)
    roots_sorted_by_hi_freq = sort_dict_by_values_desc(roots)
    ##### print(roots_sorted_by_hi_freq)
    number_of_root_words = 0
    for most_common_root, root_freq_abs in roots_sorted_by_hi_freq.items():
        number_of_root_words += root_freq_abs
        roots_all[most_common_root] = 0
    roots_info = {}
    for most_common_root, root_freq_abs in roots_sorted_by_hi_freq.items():
        root_freq_rel = root_freq_abs / number_of_root_words
        root_freq_perc = 100 * root_freq_rel
        root_info_pkg = {
            "root_word": most_common_root,
            "freq_abs": root_freq_abs,
            "freq_rel": root_freq_rel,
            "freq_perc": root_freq_perc
        }
        ##### p(root_info_pkg)
        roots_info[most_common_root] = root_info_pkg
        roots_all[most_common_root] += root_freq_rel / len(roots_sorted_by_hi_freq)

    ### display(tab_VP(nlp, tr_tit_doc))
    ### display(tab_dep(tr_tit_doc))
    ### displacy.render(tr_tit_doc, style="dep", jupyter=True)
    ### options = {"compact": True, "bg": "#09a3d5",
    ###            "color": "white", "font": "Source Sans Pro"}
    ### displacy.render(tr_tit_doc, style="dep", jupyter=True, options=options)
    ### displacy.render(tr_tit_doc, style="ent", jupyter=True)
    ### # colors = {'GPE': 'lightblue', 'NORP':'lightgreen'}
    ### # options = {'ents': ['GPE', 'NORP'], 'colors': colors}
    ### # displacy.render(tr_tit_doc, style='ent', jupyter=True, options=options)
    ### # displacy.render(tr_tit_doc, style="span", jupyter=True)
    ### lems = get_lemmas(tr_tit_doc)
    ### countsy.update(lems)
    print()
    tr_roots.append(roots_info)
### p(countsy.most_common(10))

##### p(roots_all)

roots_all_sorted_by_prob = sort_dict_by_values_desc(roots_all)
df_roots = pd.DataFrame(columns=roots_all.keys())
##### p(roots_all_sorted_by_prob)
for i in range(0, len(tr_roots)):
    df_roots[i] = pd.Series()
    tr_roots_info = tr_roots[i]
    for j in range(0, min(10, len(tr_roots_info))):
        tr_root_info = tr_roots_info[list(tr_roots_info.keys())[j]]
        root_word = tr_root_info['root_word']
        if root_word in roots_all_sorted_by_prob:
            info_big = roots_all_sorted_by_prob[root_word]
            info_small = tr_root_info
            print(f'i: {i}')
            print(f'j: {j}')
            print(f'root_word: {root_word}')
            print(f'info_big: {info_big}')
            print(f'info_small: {info_small}')
            df_roots.at[str(i), root_word] = info_small

exit(0)

print(f"\nMost common 10 words from all {len(trs_titles_uniq)} rows:")
counts = Counter()
for tr_tit in trs_titles_uniq:
    tr_tit_doc = nlp(tr_tit)
    lems = get_lemmas(tr_tit_doc)
    counts.update(lems)
# p(counts.most_common(10))

exit(0)



# regex = r"(?u)\b\w\w+\b" # default
# regex = r"^[^\W\d_]+"
regex = r"^[^\W\d_]{4,}"

vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1,2), decode_error='ignore', strip_accents='ascii', token_pattern=regex)

def empty_corpus(s):
    if s is None:
        return True
    elif isinstance(s, int) and s == int.NaN:
        return True
    elif isinstance(s, float) and s == float.NaN:
        return True
    elif isinstance(s, bool):
        return False
    elif isinstance(s, str) and s.strip() == "N/A":
        return True
    elif isinstance(s, str) and s.match(r"[-]+"):
        return True
    elif isinstance(s, set) and len(s) == 0:
        return True
    elif isinstance(s, list) and len(s) == 0:
        return True
    elif isinstance(s, dict) and len(s.keys()) == 0:
        return True
    elif isinstance(s, pd.Series) and s.empty:
        # if pd.isna(s)
        return True
    else:
        return False


for col in all_keys_last:

    col_name = col # f"txt.{col}"
    col_corpus = MHO_FULL_DF[col_name]
    print(f"column: {col_name}")
    print(f"corpus:\n{col_corpus}")

    if not empty_corpus(col_corpus):
        if col_corpus.isna().sum() > 0:
            col_corpus.fillna('', inplace=True)
        col_X = vectorizer.fit_transform(col_corpus)
        col_X_out = vectorizer.get_feature_names_out()
        col_X_shape = col_X.shape
        print(f"Shape: {col_X_shape}")
        # print(f"Features: {col_X_out}")
        print(f"{len(col_X_out)} Features:")
        display(col_X_out)
        print(f"{len(vectorizer.get_stop_words())} Stop words:")
        display(vectorizer.stop_words_)
        display(vectorizer.get_stop_words())
        print(f"{len(vectorizer.idf_)} IDF matrix diagonal:")
        display(vectorizer.idf_)
        print(f"{len(vectorizer.vocabulary_)} Vocabulary:")
        display(vectorizer.vocabulary_)

    print()



