"""Force-create the demo forklift with correct scale. Reports position and size.
Writes output to /workspace/demo_forklift_result.txt
"""
import omni.usd
from pxr import UsdGeom, Gf, Sdf

stage = omni.usd.get_context().get_stage()
out = open("/workspace/demo_forklift_result.txt", "w")

def p(s):
    print(s)
    out.write(s + "\n")

FORKLIFT_PATH = "/World/DemoForklift"
FORKLIFT_POS = Gf.Vec3d(-52, -80, 0)
FORKLIFT_ASSET = "/simready-warehouse/Props/general/SM_Forklift_B01_Red_01/SM_Forklift_B01_Red_01_physics.usd"

# Remove if exists
prim = stage.GetPrimAtPath(FORKLIFT_PATH)
if prim.IsValid():
    stage.RemovePrim(FORKLIFT_PATH)
    p(f"Removed existing {FORKLIFT_PATH}")

# Create fresh
prim = stage.DefinePrim(FORKLIFT_PATH, "Xform")
prim.GetReferences().AddReference(FORKLIFT_ASSET)

xform = UsdGeom.Xformable(prim)
xform.ClearXformOpOrder()
xform.AddTranslateOp().Set(FORKLIFT_POS)
xform.AddRotateZOp().Set(90.0)
xform.AddScaleOp().Set(Gf.Vec3f(0.01, 0.01, 0.01))

p(f"Created {FORKLIFT_PATH}")
p(f"  Asset: {FORKLIFT_ASSET}")
p(f"  Position: {FORKLIFT_POS}")
p(f"  Scale: 0.01 (cm -> m)")

# Verify
prim = stage.GetPrimAtPath(FORKLIFT_PATH)
p(f"  Valid: {prim.IsValid()}")
p(f"  Children: {[c.GetName() for c in prim.GetChildren()]}")

# Bounding box
try:
    bbox_cache = UsdGeom.BBoxCache(0, [UsdGeom.Tokens.default_])
    bbox = bbox_cache.ComputeWorldBound(prim)
    rng = bbox.ComputeAlignedRange()
    mn = rng.GetMin()
    mx = rng.GetMax()
    sz = mx - mn
    p(f"  BBox min: ({mn[0]:.2f}, {mn[1]:.2f}, {mn[2]:.2f})")
    p(f"  BBox max: ({mx[0]:.2f}, {mx[1]:.2f}, {mx[2]:.2f})")
    p(f"  Size: ({sz[0]:.2f}, {sz[1]:.2f}, {sz[2]:.2f})")
    center = (mn + mx) * 0.5
    p(f"  Center: ({center[0]:.2f}, {center[1]:.2f}, {center[2]:.2f})")
except Exception as e:
    p(f"  BBox error: {e}")

# Compare with existing scene forklift
p("\n=== Reference: existing scene forklift ===")
ref_path = "/World/Unloading_Staging_Zone/SM_Forklift_B01_Red_02"
ref_prim = stage.GetPrimAtPath(ref_path)
if ref_prim.IsValid():
    bbox2 = bbox_cache.ComputeWorldBound(ref_prim)
    rng2 = bbox2.ComputeAlignedRange()
    mn2 = rng2.GetMin()
    mx2 = rng2.GetMax()
    sz2 = mx2 - mn2
    p(f"  Position: {UsdGeom.Xformable(ref_prim).ComputeLocalToWorldTransform(0).ExtractTranslation()}")
    p(f"  Size: ({sz2[0]:.2f}, {sz2[1]:.2f}, {sz2[2]:.2f})")

out.close()
print("Done! Output written to /workspace/demo_forklift_result.txt")
