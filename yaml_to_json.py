"""
Simple YAML -> JSON converter.

Usage examples (Windows):
  python yaml_to_json.py input.yaml                  # prints JSON to stdout
  python yaml_to_json.py input.yaml -o out.json      # write to out.json
  python yaml_to_json.py a.yaml b.yaml -o out.json   # combine files into array and write to out.json
  python yaml_to_json.py input.yaml -p 2             # pretty-print with indent=2

This script supports multiple documents in a single YAML file and multiple input files.
"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
import yaml

def load_yaml_file(path: Path):
    with path.open("r", encoding="utf-8") as f:
        docs = list(yaml.safe_load_all(f))
    # If a file contains a single document, return that document, otherwise return list of docs
    if len(docs) == 0:
        return None
    if len(docs) == 1:
        return docs[0]
    return docs

def main(argv=None):
    p = argparse.ArgumentParser(description="Convert YAML to JSON")
    p.add_argument("inputs", nargs="+", help="YAML file(s) to convert")
    p.add_argument("-o", "--output", help="Output JSON file (default: stdout)")
    p.add_argument("-p", "--pretty", type=int, nargs="?", const=2, default=None,
                   help="Pretty-print JSON with given indent (default: compact). Use -p or -p 2")
    p.add_argument("--allow-empty", action="store_true",
                   help="Allow empty YAML -> produce 'null' instead of error")
    args = p.parse_args(argv)

    objs = []
    for inp in args.inputs:
        path = Path(inp)
        if not path.exists():
            print(f"Error: file not found: {path}", file=sys.stderr)
            return 2
        objs.append(load_yaml_file(path))

    # If single input file, keep its structure (single doc -> single JSON, multi-doc -> list)
    if len(objs) == 1:
        out_obj = objs[0]
    else:
        # multiple files -> produce array of each file's loaded object
        out_obj = objs

    if out_obj is None and not args.allow_empty:
        print("Error: YAML produced no document (use --allow-empty to permit null output)", file=sys.stderr)
        return 3

    print(out_obj)

    indent = args.pretty
    try:
        json_text = json.dumps(out_obj, ensure_ascii=False, indent=indent)
    except TypeError:
        # fallback: convert non-serializable types (e.g., pathlib) by re-dumping via str
        def _default(o):
            return str(o)
        json_text = json.dumps(out_obj, ensure_ascii=False, indent=indent, default=_default)

    if args.output:
        out_path = Path(args.output)
        out_path.write_text(json_text + "\n", encoding="utf-8")
    else:
        sys.stdout.write(json_text + "\n")
    return 0

if __name__ == "__main__":
    # raise SystemExit(main())

    import json
    with open('data.json') as f:
        json_str = f.read()
    data = json.loads(json_str)
    print(data)

# python yaml_to_json.py container1.yaml -o data.json