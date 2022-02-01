from importlib.machinery import SourceFileLoader
from enum import Enum
import pandas as pd
from typing import List, Dict, Union, Tuple
import yaml

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
    def __init__(self, params: List[DhParam], joint_types: List[JointType], colors: Union[Tuple[float, float, float], None]=None):
        self.params = params
        self.joint_types = joint_types
        if colors:
            self.colors = colors
        else:
            self.colors = [None]*len(self.params)
        assert len(self.params) == len(self.joint_types) == len(self.colors)

    @classmethod
    def from_yaml(cls, file_name: str):
        with open(file_name, "r") as f:
            dict_list = yaml.safe_load(f)
        return cls.from_dict_list(dict_list)
    
    @classmethod
    def from_csv(cls, file_name: str):
        df = pd.read_csv(file_name)
        df = df.rename(columns=lambda x: x.strip())
        df["type"] = df["type"].str.strip()
        dict_list = df.to_dict("records")
        for d in dict_list:
            color = d.get("color")
            if color:
                color = color.strip()
                color = tuple([float(c) for c in color.split()])
                d["color"] = color
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
        return DhParams(params, joints, colors)


