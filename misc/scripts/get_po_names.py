import json
import os
import pandas as pd

annotation_dir = "/home/william/data-omnibus/sample-annotations"
po_map_filepath = "/home/william/data-omnibus/po_name_map.json"

po_name_map = {}
files = os.listdir(annotation_dir)
for file in files:
    filepath = f"{annotation_dir}/{file}"
    df = pd.read_csv(filepath, sep="\t")
    df = df.dropna(axis=0, subset=["PO"])
    name_series = df.groupby("PO")["Name"].first()
    for po_term, name in name_series.items():
        if po_name_map.get(po_term) is None:
            po_name_map[po_term] = name
        else:
            assert po_name_map[po_term] == name

with open(po_map_filepath, "w") as file:
    file.write(json.dumps(po_name_map, indent=2) + "\n")
