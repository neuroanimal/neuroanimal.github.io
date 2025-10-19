import json
import requests
import yaml

import pandas as pd

from treelib import Node, Tree, node


def create_node(tree, s, counter_byref, verbose, parent_id=None):
    node_id = counter_byref[0]
    if verbose:
        print(f"tree.create_node({s}, {node_id}, parent={parent_id})")
    tree.create_node(s, node_id, parent=parent_id)
    counter_byref[0] += 1
    return node_id


def to_compact_string(o):
    if type(o) == dict:
        if len(o)>1:
            raise Exception()
        k,v =next(iter(o.items()))
        return f'{k}:{to_compact_string(v)}'
    elif type(o) == list:
        if len(o)>1:
            raise Exception()
        return f'[{to_compact_string(next(iter(o)))}]'
    else:
        return str(o)


def to_compact(tree, o, counter_byref, verbose, parent_id):
    try:
        s = to_compact_string(o)
        if verbose:
            print(f"# to_compact({o}) ==> [{s}]")
        create_node(tree, s, counter_byref, verbose, parent_id=parent_id)
        return True
    except:
        return False


def json_2_tree(o , parent_id=None, tree=None, counter_byref=[0], verbose=False, compact_single_dict=False, listsNodeSymbol='+'):
    if tree is None:
        tree = Tree()
        parent_id = create_node(tree, '+', counter_byref, verbose)
    if compact_single_dict and to_compact(tree, o, counter_byref, verbose, parent_id):
        # no need to do more, inserted as a single node
        pass
    elif type(o) == dict:
        for k,v in o.items():
            if compact_single_dict and to_compact(tree, {k:v}, counter_byref, verbose, parent_id):
                # no need to do more, inserted as a single node
                continue
            key_nd_id = create_node(tree, str(k), counter_byref, verbose, parent_id=parent_id)
            if verbose:
                print(f"# json_2_tree({v})")
            json_2_tree(v , parent_id=key_nd_id, tree=tree, counter_byref=counter_byref, verbose=verbose, listsNodeSymbol=listsNodeSymbol, compact_single_dict=compact_single_dict)
    elif type(o) == list:
        if listsNodeSymbol is not None:
            parent_id = create_node(tree, listsNodeSymbol, counter_byref, verbose, parent_id=parent_id)
        for i in o:
            if compact_single_dict and to_compact(tree, i, counter_byref, verbose, parent_id):
                # no need to do more, inserted as a single node
                continue
            if verbose:
                print(f"# json_2_tree({i})")
            json_2_tree(i , parent_id=parent_id, tree=tree, counter_byref=counter_byref, verbose=verbose,listsNodeSymbol=listsNodeSymbol, compact_single_dict=compact_single_dict)
    else: #node
        create_node(tree, str(o), counter_byref, verbose, parent_id=parent_id)
    return tree



# Inflacja CPI (kod wskaźnika w BDL: 1294)
url = "https://bdl.stat.gov.pl/api/v1/data/by-variable/1294?unit-level=2&page-size=100&lang=pl"

response = requests.get(url)
data_dict = response.json()
# data_dict = json.loads(data_json)

# json_2_tree(data_dict, compact_single_dict=True, listsNodeSymbol=None).show()
# data_yaml = yaml.dump(data_dict, sort_keys=False)
# print(data_yaml)
# exit(0)

records = []
for record in data_dict['results']:
    # print(record)
    for value in record['values']:
        records.append({
            "state_id": record['id'],
            "state_name": record['name'],
            "date": value['year'], # + "-" + str(record['values'][0]['month']).zfill(2),
            "value": value['val'],
        })
    print(records)
    # exit(0)

df_cpi = pd.DataFrame(records)
df_cpi['date'] = pd.to_datetime(df_cpi['date'])
df_cpi.set_index('date', inplace=True)
df_cpi.to_csv("data/cpi.csv")
df_cpi.head()

