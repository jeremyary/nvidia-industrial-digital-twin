"""Inspect the warehouse scene to find bounds and key prim locations."""

import omni.usd
from pxr import UsdGeom, Gf

stage = omni.usd.get_context().get_stage()

# Get the bounding box of the entire World prim
world_prim = stage.GetPrimAtPath("/World")
if world_prim:
    bbox_cache = UsdGeom.BBoxCache(0, ["default", "render"])
    world_bbox = bbox_cache.ComputeWorldBound(world_prim)
    bbox_range = world_bbox.ComputeAlignedRange()
    min_pt = bbox_range.GetMin()
    max_pt = bbox_range.GetMax()
    center = (min_pt + max_pt) / 2
    size = max_pt - min_pt

    print(f"=== WORLD BOUNDING BOX ===")
    print(f"Min:    ({min_pt[0]:.1f}, {min_pt[1]:.1f}, {min_pt[2]:.1f})")
    print(f"Max:    ({max_pt[0]:.1f}, {max_pt[1]:.1f}, {max_pt[2]:.1f})")
    print(f"Center: ({center[0]:.1f}, {center[1]:.1f}, {center[2]:.1f})")
    print(f"Size:   ({size[0]:.1f}, {size[1]:.1f}, {size[2]:.1f})")

# Find key areas and their positions
print(f"\n=== KEY AREAS ===")
for prim in stage.GetPrimAtPath("/World").GetChildren():
    name = prim.GetName()
    if prim.IsA(UsdGeom.Xformable):
        xformable = UsdGeom.Xformable(prim)
        transform = xformable.ComputeLocalToWorldTransform(0)
        pos = transform.ExtractTranslation()

        bbox = bbox_cache.ComputeWorldBound(prim)
        area_range = bbox.ComputeAlignedRange()
        area_min = area_range.GetMin()
        area_max = area_range.GetMax()
        area_center = (area_min + area_max) / 2

        print(f"{name:30s} pos=({pos[0]:.1f}, {pos[1]:.1f}, {pos[2]:.1f})  "
              f"bounds=({area_min[0]:.1f},{area_min[1]:.1f},{area_min[2]:.1f}) "
              f"to ({area_max[0]:.1f},{area_max[1]:.1f},{area_max[2]:.1f})")

# Check up axis
up_axis = UsdGeom.GetStageUpAxis(stage)
meters_per_unit = UsdGeom.GetStageMetersPerUnit(stage)
print(f"\n=== STAGE INFO ===")
print(f"Up axis: {up_axis}")
print(f"Meters per unit: {meters_per_unit}")
