#!/usr/bin/env python
# coding: utf-8
import argparse
import re
from typing import Dict, List, Tuple

import frictionless as fl
import os
from tqdm.auto import tqdm
import pandas as pd





def inspect_schema_fields_per_facet(regex):
    result: Dict[str, List[Tuple[str, ...]]] = {}
    """{facet -> [(fields,)]}"""
    for facet in os.listdir(SCHEMA_PATH):
        if not os.path.isdir(facet):
            continue
        if regex and not re.search(regex, facet):
            continue
        files = [file for file in os.listdir(facet) if file.endswith('.yaml')]
        n_schemas = len(files)
        if n_schemas == 0:
            continue
        field_tuples = []
        for file in tqdm(files, total=n_schemas, desc=f"Processing {facet!r} schemas..."):
            filepath = os.path.join(facet, file)
            schema = fl.Schema(filepath)
            field_tuples.append((file,) + tuple(schema.custom.values()) + (tuple(schema.field_names)))
        if len(field_tuples) > 0:
            result[facet] = sorted(field_tuples)
    return result

def main(regex):
    facet2fields = inspect_schema_fields_per_facet(regex)
    for facet, fields in facet2fields.items():
        df = pd.DataFrame(fields)
        df.to_csv(f"{facet}.tsv", sep="\t", index=False, header=False)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Collects the fields from the frictionless schemas in the neighboring subfolders and creates '
                    'one TSV file per facet in which each row contains the field names of one schema. The first '
                    'few columns contain the schemas (custom) metadata.')
    parser.add_argument("regex", nargs="?", help="Optionally, only subpaths that match this regex will be processed.")
    args = parser.parse_args()

    SCHEMA_PATH = os.path.normpath(os.path.split(__file__)[0])
    previous_working_directory = os.getcwd()
    print(f"Entering {SCHEMA_PATH!r}...")
    os.chdir(SCHEMA_PATH)
    main(args.regex)
    if os.getcwd() != previous_working_directory:
        print(f"Returning to {previous_working_directory!r}...")
        os.chdir(previous_working_directory)



