# dh2vrml

dh2vrml is a utility for converting Denavit–Hartenberg parameters into X3D models, with a particular focus on creating outputs suitable for use as a MATLAB Simulink VR Sink.

## Installation

```
pip install dh2vrml
```

## Usage

```
dh2vrml -f <file_name>
```

### Parameters

- `type`: Joint type, either `revolute` or `prismatic`
    - This refers to the joint at index `i - 1`, (i.e. the first joint is the base joint)
- `d`, `theta`, `r`, `alpha`: DH parameters as specified on [Wikipedia](https://en.wikipedia.org/wiki/Denavit%E2%80%93Hartenberg_parameters)
- `color`: Color of the joint and link at index `i`, in RGB format
    - Values are floats ranging from 0 to 1
    - The end effector is always colored `(0, 1, 1)`, (cyan)

### Supported file types

#### YAML

```yaml
- type: revolute  
  d: 1.5
  theta: 0
  r: 3
  alpha: 0
  color: [1, 0, 0]

- type: revolute
  d: 2
  theta: 0
  r: 4
  alpha: 3.14159265359
  color: [0, 0, 1]

- type: prismatic
  d: 3
  theta: 0
  r: 0
  alpha: 0
  color: [1, 0, 1]
```

#### CSV

```csv
d ,theta ,r ,alpha        ,type     , color
2 ,0     ,0 ,1.5707963268 ,revolute , 1 0 0
0 ,0     ,2 ,0            ,revolute , 0 1 0
```

#### Python

For the sake of making calculations involving `pi` easier, Python files are supported.

> Beware: dh2vrml will blindly import and run whatever code is provided, always inspect the contents of the file before importing

```py
from math import pi

params = [
    {
        "type": "revolute",
        "d": 2,
        "theta": pi/2,
        "r": 0,
        "alpha": pi/2
    },
    {
        "type": "revolute",
        "d": 2,
        "theta": pi/2,
        "r": 0,
        "alpha": -pi/2
    },
    {
        "type": "revolute",
        "d": 2,
        "theta": pi/2,
        "r": 2,
        "alpha": 0
    },
]
```