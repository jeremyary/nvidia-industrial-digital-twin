"""
Add 3 security cameras to the warehouse scene.
Run this in Isaac Sim's Script Editor (Window > Script Editor).

Cameras are positioned for typical warehouse safety monitoring:
1. Overhead - wide angle view of main aisle
2. Forklift Zone - medium angle covering forklift operating area
3. Loading Dock - medium angle on staging/loading area
"""

import omni.usd
from pxr import UsdGeom, Gf, Sdf

stage = omni.usd.get_context().get_stage()

# Create a parent Xform for all cameras
cameras_path = "/World/SecurityCameras"
if not stage.GetPrimAtPath(cameras_path):
    UsdGeom.Xform.Define(stage, cameras_path)

# Camera definitions: (name, position, rotation_xyz_degrees, focal_length_mm)
cameras = [
    (
        "Camera_Overhead",
        Gf.Vec3d(0, 8, 0),          # 8m high, centered
        Gf.Vec3f(-90, 0, 0),        # pointing straight down
        18,                          # wide angle
    ),
    (
        "Camera_ForkLift",
        Gf.Vec3d(5, 5, -3),         # elevated corner position
        Gf.Vec3f(-45, 30, 0),       # angled down at forklift area
        35,                          # medium angle
    ),
    (
        "Camera_LoadingDock",
        Gf.Vec3d(-5, 5, 5),         # opposite corner
        Gf.Vec3f(-45, -30, 0),      # angled down at loading area
        35,                          # medium angle
    ),
]

for name, pos, rot, focal in cameras:
    cam_path = f"{cameras_path}/{name}"

    # Create camera prim
    cam = UsdGeom.Camera.Define(stage, cam_path)

    # Set transform
    xform = UsdGeom.Xformable(cam.GetPrim())
    xform.ClearXformOpOrder()

    translate_op = xform.AddTranslateOp()
    translate_op.Set(pos)

    rotate_op = xform.AddRotateXYZOp()
    rotate_op.Set(rot)

    # Set camera properties
    cam.GetFocalLengthAttr().Set(focal)
    cam.GetClippingRangeAttr().Set(Gf.Vec2f(0.1, 1000))

    # Set horizontal aperture for ~16:9 aspect ratio
    cam.GetHorizontalApertureAttr().Set(36.0)
    cam.GetVerticalApertureAttr().Set(20.25)

    print(f"Created camera: {cam_path}")

print("\nDone! 3 security cameras added to /World/SecurityCameras/")
print("Select a camera in the Stage panel and press Numpad-Enter to look through it.")
print("Or use: Right-click camera > Set as Active Camera")
