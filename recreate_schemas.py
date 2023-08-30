#!/usr/bin/env python
# coding: utf-8
import argparse
import re

import frictionless as fl
import os
import ms3
from tqdm.auto import tqdm


def main(regex: str = None):
    for facet in os.listdir(schema_path):
        if not os.path.isdir(facet):
            continue
        if regex and not re.search(regex, facet):
            continue
        files = os.listdir(facet)
        n_schemas = len(files)
        for file in tqdm(files, total=n_schemas, desc=f"Processing {facet!r} schemas..."):
            if not file.endswith('.yaml'):
                continue
            filepath = os.path.join(facet, file)
            recreate_schema(filepath, facet)


def recreate_schema(
        filepath: str,
        facet: str,
):
    schema = fl.Schema(filepath)
    column_names = schema.field_names
    schema_identifier = ms3.get_truncated_hash(column_names)
    schema_filename = f"{schema_identifier}.schema.yaml"
    schema_filepath = f"{facet}/{schema_filename}"  # for URL & uniform filepath
    descriptor = ms3.make_frictionless_schema_descriptor(
        column_names=column_names,
        primary_key=schema.primary_key,
        # the rest is custom data added to the schema descriptor
        facet=facet,
        identifier=schema_identifier,
        filepath=schema_filepath,
    )
    new_filepath = os.path.join(facet, schema_filename)
    fl.Schema(descriptor).to_yaml(new_filepath)
    if new_filepath != filepath:
        os.remove(filepath)
        print(f"{filepath} replaced with {new_filepath}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Re-generates the frictionless schemas in the neighboring subfolders.')
    parser.add_argument("regex", nargs="?", help="Optionally, only subpaths that match this regex will be processed.")
    args = parser.parse_args()

    schema_path = os.path.normpath(os.path.split(__file__)[0])
    previous_working_directory = os.getcwd()
    print(f"Entering {schema_path!r}...")
    os.chdir(schema_path)
    main(args.regex)
    if os.getcwd() != previous_working_directory:
        print(f"Returning to {previous_working_directory!r}...")
        os.chdir(previous_working_directory)


