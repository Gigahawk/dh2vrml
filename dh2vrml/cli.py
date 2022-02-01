from typing import Tuple
import os
import click

from dh2vrml.dhparams import DhParams
from dh2vrml.exporter import build_x3d

@click.command()
@click.option(
    '-f', '--file', default=None, multiple=True,
    help='DH Parameter file (.yaml, .csv)'
)
def main(file : Tuple[str, ...]):
    for f in file:
        print(f"Opening {f}")
        file_name = os.path.basename(f)
        name, ext = os.path.splitext(file_name)
        if ext.lower() == ".yaml":
            print("Parsing YAML file")
            params = DhParams.from_yaml(f)
        elif ext.lower() == ".csv":
            print("Parsing CSV file")
            params = DhParams.from_csv(f)
        elif ext.lower() == ".py":
            print("Importing Python file")
            params = DhParams.from_py(f)
        else:
            print(f"Error: unrecognized file extension {ext}")
            exit(1)
        model = build_x3d(params)

        print("Checking XML serialization...")
        modelXML= model.XML()
        model.XMLvalidate()
        out_name = f"{name}.x3d"
        print(f"Writing output to {out_name}")
        with open(out_name, "w") as f:
            f.write(modelXML)


if __name__ == '__main__':
    main()