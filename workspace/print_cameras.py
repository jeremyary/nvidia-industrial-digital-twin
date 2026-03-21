"""Print current position and orientation of all security cameras.
Writes output to /workspace/camera_positions.txt
"""
import omni.usd
from pxr import UsdGeom, Gf

stage = omni.usd.get_context().get_stage()
out = open("/workspace/camera_positions.txt", "w")

def p(s):
    print(s)
    out.write(s + "\n")

for cam_name in ["Camera_Overhead", "Camera_ForkLift", "Camera_LoadingDock"]:
    path = f"/World/SecurityCameras/{cam_name}"
    prim = stage.GetPrimAtPath(path)
    if not prim.IsValid():
        p(f"{cam_name}: NOT FOUND")
        continue

    xformable = UsdGeom.Xformable(prim)
    world_transform = xformable.ComputeLocalToWorldTransform(0)
    translation = world_transform.ExtractTranslation()

    # Get the full 4x4 matrix values for exact restore
    p(f"\n{cam_name}:")
    p(f"  Position: ({translation[0]:.4f}, {translation[1]:.4f}, {translation[2]:.4f})")
    p(f"  Matrix:")
    for row in range(4):
        vals = [f"{world_transform[row][col]:.6f}" for col in range(4)]
        p(f"    [{', '.join(vals)}]")

out.close()
print("\nDone! Output written to /workspace/camera_positions.txt")
