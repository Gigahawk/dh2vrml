from math import inf
import random
from typing import Tuple, List, Union
from dh2vrml.util import rand_color
from dh2vrml.mdl_template import TEMPLATE
import numpy as np
from scipy.spatial.transform import Rotation
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
# Keep track of last unit length for link extrusion calculations
PREV_UL = UNIT_LENGTH
UL = UNIT_LENGTH

def update_ul(new_ul: float):
    global UL, PREV_UL
    PREV_UL = UL
    UL = new_ul

def reset_ul():
    global UL
    UL = UNIT_LENGTH
    PREV_UL = UNIT_LENGTH

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

def get_link_body(idx: int, d: float, theta: float, r: float, alpha: float, offset: Tuple[float, float, float], last_offset: Tuple[float, float, float], color: Tuple[float, float, float], last_link=False) -> Transform:
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
    def get_offset_matrix(x, y, z, reverse=False):
        if reverse:
            x = -x
            y = -y
            z = -z
        return np.matrix([
            [1, 0, 0, x],
            [0, 1, 0, y],
            [0, 0, 1, z],
            [0, 0, 0, 1],
        ])

    last_offset_matrix = get_offset_matrix(*last_offset, reverse=True)
    z = get_z(d, theta)
    x = get_x(r, alpha)
    offset_matrix = get_offset_matrix(*offset)
    t = last_offset_matrix*z*x*offset_matrix
    zero_point = np.matrix([0, 0, 0, 1]).transpose()
    x_dir = np.matrix([1, 0, 0, 0]).transpose()
    final_point = t*zero_point
    final_x_dir = t*x_dir
    # Link should always appear to connect into the side of a joint
    second_last_point = final_point - UL*final_x_dir
    # Extract x, y, z from final point
    final_point = tuple(final_point[0:3].transpose().tolist()[0])
    second_last_point = tuple(second_last_point[0:3].transpose().tolist()[0])
    extrusion_spine = [
        (0, 0, 0),  # Start extrusion at center of joint
        (0, 0, 1.5*PREV_UL),  # Extrusion protrudes up in the Z axis out of joint
    ]
    if final_point[-1] <= 0:
        # Wrap link body around joint if next joint is lower
        extrusion_spine.extend([
            (PREV_UL, 0, 1.5*PREV_UL),
            (PREV_UL, 0, 0),
        ])
    # Last link connects to the end effector, not a joint
    if not last_link:
        extrusion_spine.append(second_last_point)
    extrusion_spine.append(final_point)

    return Transform(
        DEF=f'l{idx}_link_body',
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

def get_link(idx: int, d: float, theta: float, r: float, alpha: float, joint_type: JointType, last_joint_type: JointType, offset: Tuple[float, float, float], last_offset: Tuple[float, float, float], color: Union[Tuple[float, float, float], None]=None) -> Tuple[Transform, Transform]:
    if not color:
        color = rand_color()
    if joint_type == JointType.END_EFFECTOR:
        last_link = True
    else:
        last_link = False
    joint = get_joint(joint_type, color)
    link_alpha = Transform(
        DEF=f'l{idx}_alpha',
        rotation=(1, 0, 0, alpha),
        children=[
            Transform(
                DEF=f'l{idx}_offset',
                translation=offset,
                children=[
                    joint
                ]
            )
        ]
    )
    link = Transform(
        DEF=f'l{idx}_{last_joint_type.name}',
        children=[
            Transform(
                DEF=f'l{idx}_link_offset',
                translation=last_offset,
                children=[
                    get_link_body(
                        idx, d, theta, r, alpha, offset, last_offset, color,
                        last_link=last_link),
                ]
            ),
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

def get_viewpoint(
        camera_location: Tuple[float, float, float],
        camera_center: Tuple[float, float, float],
        ) -> Viewpoint:
    # From https://github.com/numpy/numpy/issues/5228
    def cart2sph(x, y, z):
        hxy = np.hypot(x, y)
        r = np.hypot(hxy, z)
        el = np.arctan2(z, hxy)
        az = np.arctan2(y, x)
        return az, el, r
    camera_location_m = np.matrix(camera_location)
    camera_center_m = np.matrix(camera_center)
    desired_orientation = camera_center_m - camera_location_m
    azimuth, inclination, _ = cart2sph(*desired_orientation.tolist()[0])

    # Default orientation is straight down, we want to:
    camera_rotvec = Rotation.from_euler(
        'XYX',
        [
            np.pi/2, # Pan camera up to point towards positive Y in the fixed frame
            (azimuth - np.pi/2), # Pan camera left towards camera center
            inclination, # Pan camera up/down towards camera center
        ]
        ).as_rotvec()
    camera_angle = np.linalg.norm(camera_rotvec)
    camera_rotvec /= camera_angle
    camera_orientation = tuple(camera_rotvec.tolist()) + (camera_angle,)

    return Viewpoint(
        position=camera_location,
        centerOfRotation=camera_center,
        orientation=camera_orientation
    )


def base_model(
        base_joint: JointType,
        base_offset: Tuple[float, float, float],
        camera_location: Tuple[float, float, float],
        camera_center: Tuple[float, float, float],
        ) -> Tuple[X3D, Transform]:
    base_color = (0.2, 0.2, 0.2)
    base = Transform(
        DEF="Base Joint Offset",
        translation=base_offset,
        children=[
            Transform(
                DEF="Base",
                translation=(0, 0, -1*UL),
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
    return X3D(
        profile="Immersive", version="3.3",
        Scene=Scene(
            children=[
                NavigationInfo(
                    DEF="ExamineMode"
                ),
                get_viewpoint(camera_location, camera_center),
                base
            ]
        )
    ), base


def build_x3d(
        params: DhParams,
        camera_location: Union[Tuple[float, float, float], None]=(10, -10, 10),
        camera_center: Union[Tuple[float, float, float], None]=(0, 0, 0)) -> X3D:
    global UL
    parameters = params.params
    scale = params.scale
    colors = params.colors
    joint_types = params.joint_types.copy()
    offsets = params.offsets.copy()
    base_joint = joint_types.pop(0)
    base_offset = offsets.pop(0)

    if scale[0] is not None:
        update_ul(scale[0])
    else:
        reset_ul()
    joint_types.append(JointType.END_EFFECTOR)
    # Assume last frame is always centered around end effector
    offsets.append((0, 0, 0))
    model, ptr = base_model(base_joint, base_offset, camera_location, camera_center)
    ptr = model.Scene

    last_joint_type = base_joint
    last_offset = base_offset
    for idx, (p, j, c, s, o) in enumerate(zip(parameters, joint_types, colors, scale, offsets)):
        if s is not None:
            update_ul(s)
        else:
            update_ul(UL)
        # link 0 is the base "link"
        link_idx = idx + 1
        link, new_ptr = get_link(link_idx, p.d, p.theta, p.r, p.alpha, j, last_joint_type, o, last_offset, c)
        ptr.children.append(link)
        ptr = new_ptr
        last_joint_type = j
        last_offset = o

    # Return UL to original length
    reset_ul()
    return model

def generate_mdl(name: str, params: DhParams) -> str:
    """Generate a Simulink .mdl file with a VR sink containing the model

    Args:
    - name: name of the .x3d model (without extension)
    - params: robot parameters

    Returns:
    Simulink model template
    """
    revolute_template = "l{j_idx}_REVOLUTE.rotation.4.1.1.double"
    prismatic_template = "l{j_idx}_PRISMATIC.translation.3.1.1.double"

    x3d_path = f"{name}.x3d"
    simulink_name = f"simulink_{name}"

    fields = []
    for idx, joint_type in enumerate(params.joint_types):
        print(joint_type)
        joint_idx = idx + 1
        if joint_type == JointType.REVOLUTE:
            fields.append(revolute_template.format(j_idx=joint_idx))
        elif joint_type == JointType.PRISMATIC:
            fields.append(prismatic_template.format(j_idx=joint_idx))
    fields = "#".join(fields)
    mdl_template = TEMPLATE.format(
        NAME=simulink_name, FIELDS=fields, X3DPATH=x3d_path)
    return mdl_template


