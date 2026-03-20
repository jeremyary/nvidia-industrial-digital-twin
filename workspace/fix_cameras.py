"""Reposition security cameras based on actual scene bounds.
Scene: Z-up, 1m per unit, bounds (-61,-101,-1.3) to (14.9,-37.9,11.0)
"""

import omni.usd
from pxr import UsdGeom, Gf

stage = omni.usd.get_context().get_stage()

# Camera definitions: (name, position, rotation_xyz_degrees, focal_length_mm)
# Z is up, scene center is roughly (-23, -70, 0)
cameras = [
    (
        "Camera_Overhead",
        Gf.Vec3d(-23, -70, 10),       # centered over warehouse, near ceiling (10m up)
        Gf.Vec3f(0, 0, 0),            # Z-up: looking straight down means no rotation needed
        18,                            # wide angle
    ),
    (
        "Camera_ForkLift",
        Gf.Vec3d(-50, -75, 8),        # elevated corner near Transporter/Sorting area
        Gf.Vec3f(60, 0, -50),         # angled down and rotated toward center
        28,                            # medium-wide angle
    ),
    (
        "Camera_LoadingDock",
        Gf.Vec3d(-20, -45, 8),        # near Loading_Zone, elevated
        Gf.Vec3f(60, 0, 150),         # angled down, facing back into warehouse
        28,                            # medium-wide angle
    ),
]

for name, pos, rot, focal in cameras:
    cam_path = f"/World/SecurityCameras/{name}"
    prim = stage.GetPrimAtPath(cam_path)

    if not prim.IsValid():
        print(f"Camera not found: {cam_path}")
        continue

    xform = UsdGeom.Xformable(prim)
    xform.ClearXformOpOrder()

    translate_op = xform.AddTranslateOp()
    translate_op.Set(pos)

    rotate_op = xform.AddRotateXYZOp()
    rotate_op.Set(rot)

    cam = UsdGeom.Camera(prim)
    cam.GetFocalLengthAttr().Set(focal)
    cam.GetClippingRangeAttr().Set(Gf.Vec2f(0.1, 1000))
    cam.GetHorizontalApertureAttr().Set(36.0)
    cam.GetVerticalApertureAttr().Set(20.25)

    print(f"Repositioned: {cam_path} at ({pos[0]}, {pos[1]}, {pos[2]})")

# Fix overhead camera to look straight down (Z-up means rotate 0 around all axes
# but the camera default looks down -Z, so we need no rotation for a Z-up downward view)
# Actually in USD, cameras look down -Z in their local space.
# For Z-up scene, to look straight down we need to NOT rotate (camera -Z = world -Z = down)
# But wait - that would look into the ground. We need to flip it.
# Camera looks along its local -Z. To look DOWN in a Z-up world,
# we need local -Z to point in world -Z direction. That means no rotation.
# Hmm, but -Z in world is "down" which is what we want for overhead.

# Let me just set the overhead to a known good orientation:
overhead_path = "/World/SecurityCameras/Camera_Overhead"
prim = stage.GetPrimAtPath(overhead_path)
xform = UsdGeom.Xformable(prim)
xform.ClearXformOpOrder()

translate_op = xform.AddTranslateOp()
translate_op.Set(Gf.Vec3d(-23, -70, 10))

# Camera looks down -Z locally. In Z-up world, -Z is already "down".
# So identity rotation = looking straight down. Perfect.
# No rotate op needed for straight down.

cam = UsdGeom.Camera(prim)
cam.GetFocalLengthAttr().Set(14)  # extra wide for overhead
print(f"\nOverhead camera: straight down, 14mm wide angle")

print("\nDone! Switch viewport to each camera to check views.")
print("Use the camera dropdown at top-left of viewport (where it says 'Perspective').")
