from importlib.machinery import SourceFileLoader
from enum import Enum
import pandas as pd
from typing import List, Dict, Union, Tuple
import yaml
from math import pi

class JointType(Enum):
    REVOLUTE = 1
    PRISMATIC = 2
    END_EFFECTOR = 3

class DhParam:
    def __init__(self, d, theta, r, alpha):
        self.d = d
        self.theta = theta
        self.r = r
        self.alpha = alpha

class DhParams:
    def __init__(self,
                 params: List[DhParam],
                 joint_types: List[JointType],
                 colors: Union[List[Union[Tuple[float, float, float], None]], None]=None,
                 scale: Union[List[Union[float, None]], None]=None,
                 offsets: Union[List[Tuple[float, float, float]], None]=None, ):
        self.params = params
        self.joint_types = joint_types
        if colors:
            self.colors = colors
        else:
            self.colors = [None]*len(self.params)
        if scale:
            self.scale = scale
        else:
            self.scale = [1]*len(self.params)

        if offsets:
            self.offsets = offsets
        else:
            self.offsets = [(0, 0, 0)]*len(self.params)

        if not(
                len(self.params) == len(self.joint_types)
                == len(self.colors) == len(self.scale) == len(self.offsets)):
            raise ValueError("All parameter lists must be the same length")

        for idx, (jt, (x, y, z)) in enumerate(zip(self.joint_types, self.offsets)):
            if jt == JointType.REVOLUTE and (x != 0 or y != 0):
                raise ValueError(
                    f"Joint {idx} is revolute but has a non zero x or y offset")

    @classmethod
    def from_yaml(cls, file_name: str):
        with open(file_name, "r") as f:
            dict_list = yaml.safe_load(f)
        return cls.from_dict_list(dict_list)

    @classmethod
    def from_csv(cls, file_name: str):
        df = pd.read_csv(file_name, sep="\s*[,]\s*", engine="python")
        df.fillna("", inplace=True)
        dict_list = df.to_dict("records")
        for d in dict_list:
            color = d.get("color")
            if color:
                color = color.strip()
                color = tuple([float(c) for c in color.split()])
                d["color"] = color
            else:
                d["color"] = None

            offset = d.get("offset")
            if offset:
                offset = offset.strip()
                offset = tuple([float(c) for c in offset.split()])
                d["offset"] = offset
            else:
                d["offset"] = None

            scale = d.get("scale")
            if not scale:
                d["scale"] = None

        return cls.from_dict_list(dict_list)

    @classmethod
    def from_py(cls, file_name: str):
        module = SourceFileLoader("m_dhparams", file_name).load_module()
        try:
            dict_list = module.params
        except AttributeError:
            print(f"Error: could not find `params` variable in {file_name}")
            exit(1)
        return cls.from_dict_list(dict_list)

    @classmethod
    def from_dict_list(cls, param_list : List[Dict[str, Union[str, int, float]]]):
        for p in param_list:
            if "theta_deg" in p.keys():
                p["theta"] = p["theta_deg"] * pi/180
            if "alpha_deg" in p.keys():
                p["alpha"] = p["alpha_deg"] * pi/180
        params = [
            DhParam(
                p["d"], p["theta"], p["r"], p["alpha"])
            for  p in param_list
        ]
        joints = [
            JointType[p["type"].upper()] if p.get("type") else JointType.REVOLUTE
            for p in param_list
        ]
        colors = [
            tuple(p["color"]) if p.get("color") else None
            for p in param_list
        ]
        scale = [p.get("scale") for p in param_list]
        offsets = [
            tuple(p["offset"]) if p.get("offset") else (0, 0, 0)
            for p in param_list
        ]
        return DhParams(params, joints, colors, scale, offsets)


