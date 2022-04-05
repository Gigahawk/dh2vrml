import uuid
import sys
import tempfile
from typing import Tuple, Union, List
import os
import click
from pathlib import Path

from dh2vrml.dhparams import DhParams
from dh2vrml.exporter import build_x3d
from dh2vrml.exporter import generate_mdl as _generate_mdl

def get_params_from_stdin(file_ext: str) -> DhParams:
    with tempfile.TemporaryDirectory() as tmp_name:
        name = str(uuid.uuid1())
        file_path = os.path.join(tmp_name, f"{name}.{file_ext}")
        with open(file_path, "w") as f:
            f.writelines(sys.stdin)
        print(f"Wrote tempfile to {file_path}")
        return get_params_from_file(file_path)


def get_params_from_file(f: str) -> DhParams:
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
    return params

def write_x3d_file(
        file_name: str,
        params: DhParams,
        camera_location: Tuple[float, float, float],
        camera_center: Tuple[float, float, float],
        validate: bool=True) -> str:
    file_name = os.path.basename(file_name)
    name, ext = os.path.splitext(file_name)
    model = build_x3d(params, camera_location, camera_center)
    modelXML= model.XML()
    if validate:
        print("Checking XML serialization...")
        model.XMLvalidate()
    else:
        print("Skipping model validation")
    out_name = f"{name}.x3d"
    print(f"Writing output to {out_name}")
    with open(out_name, "w") as f:
        f.write(modelXML)
    return modelXML


def write_mdl_file(name: str, params: DhParams):
    mdl_path = f"simulink_{name}.mdl"
    print(f"Generating {mdl_path}")
    mdl_content = _generate_mdl(name, params)
    with open(mdl_path, "w") as f:
        f.write(mdl_content)
    return mdl_content


@click.command()
@click.option(
    '-f', '--file', default=None, multiple=True,
    help='DH Parameter file (.yaml, .csv, .py)'
)
@click.option(
    '-s', '--stdin', default=None,
    help='Read input from stdin, specify filetype to parse as (yaml, csv, py)'
)
@click.option(
    '--validate/--no-validate', default=True,
    help='Enable/disable validation of X3D output, (requires internet)'
)
@click.option(
    '--generate-mdl/--no-generate-mdl', default=False,
    help='Enable/disable generation of Simulink .mdl file with VR Sink already setup'
)
@click.option(
    '--camera-location', nargs=3, type=float, default=(10, -10, 10), show_default=True,
    help='Location of the camera'
)
@click.option(
    '--camera-center', nargs=3, type=float, default=(0, 0, 0), show_default=True,
    help='Location the camera is pointed at'
)
def main(
        file: Union[Tuple[str, ...], None],
        stdin: Union[str, None],
        validate: bool,
        generate_mdl: bool,
        camera_location: Tuple[float, float, float],
        camera_center: Tuple[float, float, float]
        ) -> List[str]:
    out = []
    if stdin:
        name = str(uuid.uuid1())
        params = get_params_from_stdin(stdin)
        out.append(write_x3d_file(name, params, camera_location, camera_center, validate))
        if generate_mdl:
            mdl_content = write_mdl_file(name, params)
            out.append(mdl_content)

    for f in file:
        params = get_params_from_file(f)
        modelXML = write_x3d_file(f, params, camera_location, camera_center, validate)
        out.append(modelXML)
        if generate_mdl:
            name = Path(f).stem
            mdl_content = write_mdl_file(name, params)
            out.append(mdl_content)

    return out


if __name__ == '__main__':
    main()
