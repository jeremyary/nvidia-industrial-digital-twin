"""Set a security camera to match the current viewport position/orientation.

Usage:
  1. Navigate the viewport to where you want the camera to look
  2. Change CAMERA_TO_UPDATE below to the camera you want to move
  3. Run this script
"""
import omni.usd
import omni.kit.viewport.utility as vp_utils
from pxr import UsdGeom, Gf

# ---- CHANGE THIS to the camera you want to update ----
# Options: "Camera_Overhead", "Camera_ForkLift", "Camera_LoadingDock"
CAMERA_TO_UPDATE = "Camera_Overhead"
# -------------------------------------------------------

stage = omni.usd.get_context().get_stage()
viewport_api = vp_utils.get_active_viewport()

# Get current viewport camera transform
view_cam_path = viewport_api.camera_path
view_cam_prim = stage.GetPrimAtPath(view_cam_path)
view_xform = UsdGeom.Xformable(view_cam_prim)
world_transform = view_xform.ComputeLocalToWorldTransform(0)

pos = world_transform.ExtractTranslation()
print(f"\nCurrent viewport position: ({pos[0]:.2f}, {pos[1]:.2f}, {pos[2]:.2f})")

# Apply to target camera
target_path = f"/World/SecurityCameras/{CAMERA_TO_UPDATE}"
target_prim = stage.GetPrimAtPath(target_path)
if not target_prim.IsValid():
    print(f"ERROR: {target_path} not found")
else:
    target_xform = UsdGeom.Xformable(target_prim)
    target_xform.ClearXformOpOrder()
    target_xform.AddTransformOp().Set(world_transform)
    print(f"Updated {CAMERA_TO_UPDATE} to current viewport position")
    print(f"  Position: ({pos[0]:.2f}, {pos[1]:.2f}, {pos[2]:.2f})")
