from math import inf
import random
from typing import Tuple, List, Union
from dh2vrml.util import rand_color
import numpy as np
from x3d.x3d import (
    X3D,
    Scene, Viewpoint, NavigationInfo,
    Shape, Transform,
    Appearance, Material,
    Box, Cylinder, Extrusion,
    _X3DChildNode
)

from dh2vrml.dhparams import DhParams, JointType


UNIT_LENGTH = 1
UL = UNIT_LENGTH

def revolute_joint(color : Tuple[float, float, float]) -> Transform:
    """Return a cylinder axial along the Z axis

    By default the x3d cylinder primitive is axial along the Y axis.
    By wrapping the primitive in a rotation 90 degrees about the X axis
    we get the desired orientation.
    """
    return Transform(
        rotation=(UL, 0, 0, np.pi/2),
        children=[
            Shape(
                geometry=Cylinder(
                    height=2*UL,
                    radius=0.5*UL
                ),
                appearance=Appearance(
                    material=Material(
                        diffuseColor=color
                    )
                )
            )
        ]
    )

def prismatic_joint(color : Tuple[float, float, float]) -> Shape: 
    return Shape(
        geometry=Box(
            size=(UL, UL, 2*UL)
        ),
        appearance=Appearance(
            material=Material(
                diffuseColor=color
            )
        )
    )

def link_cross_section() -> List[Tuple[float, float]]:
    radius = 0.1*UL
    segments = 30
    cross_section = []
    for i in range(segments):
        theta = (2*np.pi/segments)*i
        cross_section.append(
            (radius*np.cos(theta), radius*np.sin(theta),)
        )
    # Final point to close cross section profile
    cross_section.append((radius*np.cos(0), radius*np.sin(0),))
    return cross_section

def end_effector(color : Tuple[float, float, float]) -> Shape: 
    shaft_length = 1.5*UL
    gripper_width = 0.7*UL
    gripper_length = 0.7*UL
    shaft_spine = [(0, 0, 0), (0, 0, shaft_length)]
    left_spine = shaft_spine + [
        (-gripper_width/2, 0, shaft_length),
        (-gripper_width/2, 0, shaft_length + gripper_length),
    ]
    right_spine = shaft_spine + [
        (gripper_width/2, 0, shaft_length),
        (gripper_width/2, 0, shaft_length + gripper_length),
    ]

    return Transform(
        DEF=f'end_effector',
        children=[
            Shape(
                geometry=Extrusion(
                    crossSection=link_cross_section(),
                    spine=left_spine,
                    scale=[(1, 1)]*len(left_spine),
                    creaseAngle=100
                ),
                appearance=Appearance(
                    material=Material(
                        diffuseColor=color
                    )
                )
            ),
            Shape(
                geometry=Extrusion(
                    crossSection=link_cross_section(),
                    spine=right_spine,
                    scale=[(1, 1)]*len(right_spine),
                    creaseAngle=100
                ),
                appearance=Appearance(
                    material=Material(
                        diffuseColor=color
                    )
                )
            ),
        ]
    )

def get_link_body(idx: int, d: float, theta: float, r: float, alpha: float, color: Tuple[float, float, float]) -> Transform:
    def get_z(d, theta):
        return np.matrix([
            [np.cos(theta), -np.sin(theta), 0, 0],
            [np.sin(theta),  np.cos(theta), 0, 0],
            [0            ,  0            , 1, d],
            [0            ,  0            , 0, 1]
        ])

    def get_x(r, alpha):
        return np.matrix([
            [1, 0            ,  0            , r],
            [0, np.cos(alpha), -np.sin(alpha), 0],
            [0, np.sin(alpha),  np.cos(alpha), 0],
            [0, 0            ,  0            , 1]
        ])

    # Assume zero rotation in actuator, wrap geometry in a Transform frame with
    # rotation at the end for simplicity
    z = get_z(d, 0)
    x = get_x(r, alpha)
    t = z*x
    zero_point = np.matrix([0, 0, 0, 1]).transpose()
    final_point = t*zero_point
    # Extract x, y, z from final point
    final_point = tuple(final_point[0:3].transpose().tolist()[0])
    extrusion_spine = [
        (0, 0, 0),  # Start extrusion at center of joint
        (0, 0, 1.5*UL),  # Extrusion protrudes up in the Z axis out of joint
    ]
    if final_point[-1] <= 0:
        # Wrap link body around joint if next joint is lower
        extrusion_spine.extend([
            (UL, 0, 1.5*UL),
            (UL, 0, 0),
        ])
    extrusion_spine.append(final_point)

    return Transform(
        DEF=f'l{idx}_link_body',
        rotation=(0, 0, 1, theta),
        children=[
            Shape(
                geometry=Extrusion(
                    crossSection=link_cross_section(),
                    spine=extrusion_spine,
                    scale=[(1, 1)]*len(extrusion_spine),
                    creaseAngle=100
                ),
                appearance=Appearance(
                    material=Material(
                        diffuseColor=color
                    )
                )
            ),
        ]
    )

def get_joint(type: JointType, color: Tuple[float, float, float]) -> _X3DChildNode:
    if type == JointType.REVOLUTE:
        return revolute_joint(color)
    if type == JointType.PRISMATIC:
        return prismatic_joint(color)
    if type == JointType.END_EFFECTOR:
        # End effector should always be cyan
        return end_effector((0, 1, 1))

def get_link(idx: int, d: float, theta: float, r: float, alpha: float, joint_type: JointType, last_joint_type: JointType, color: Union[Tuple[float, float, float], None]=None) -> Tuple[Transform, Transform]:
    if not color:
        color = rand_color()
    joint = get_joint(joint_type, color)
    link_alpha = Transform(
        DEF=f'l{idx}_alpha',
        rotation=(1, 0, 0, alpha),
        children=[
            joint
        ]
    )
    link = Transform(
        DEF=f'l{idx}_{last_joint_type.name}',
        children=[
            get_link_body(idx, d, theta, r, alpha, color),
            Transform(
                DEF=f'l{idx}_d',
                translation=(0, 0, d),
                children=[
                    Transform(
                        DEF=f'l{idx}_theta',
                        rotation=(0, 0, 1, theta),
                        children=[
                            Transform(
                                DEF=f'l{idx}_r',
                                translation=(r, 0, 0),
                                children=[
                                    link_alpha
                                ]
                            )
                        ]
                    )
                ]
            )
        ]
    )
    return link, link_alpha


def base_model(base_joint : JointType) -> X3D:
    base_color = (0.2, 0.2, 0.2)
    return X3D(
        profile="Immersive", version="3.3",
        Scene=Scene(
            children=[
                NavigationInfo(
                    DEF="ExamineMode"
                ),
                Viewpoint(
                    orientation=(-1, 0, 0, 0.2),
                    position=(0, 5, 15),
                ),
                Transform(
                    DEF="Base",
                    translation=(0, 0, -1),
                    children=[
                        Shape(
                            geometry=Box(
                                size=(10, 10, 0.1)
                            ),
                            appearance=Appearance(
                                material=Material(
                                    diffuseColor=base_color
                                )
                            )
                        ),
                    ]
                ),
                get_joint(base_joint, base_color)
            ]
        )
    )


def build_x3d(params : DhParams) -> X3D:
    parameters = params.params
    colors = params.colors
    joint_types = params.joint_types
    base_joint = joint_types.pop(0)
    joint_types.append(JointType.END_EFFECTOR)
    model = base_model(base_joint)
    ptr = model.Scene

    last_joint_type = base_joint
    for idx, (p, j, c) in enumerate(zip(parameters, joint_types, colors)):
        # link 0 is the base "link"
        link_idx = idx + 1
        link, new_ptr = get_link(link_idx, p.d, p.theta, p.r, p.alpha, j, last_joint_type, c)
        ptr.children.append(link)
        ptr = new_ptr
        last_joint_type = j
    return model