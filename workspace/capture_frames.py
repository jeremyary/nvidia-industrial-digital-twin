"""
Capture a single frame from each security camera and save to /workspace/camera_feeds/.
Run this in Isaac Sim's Script Editor.

Uses Omniverse Replicator to render each camera at 1280x720 and write PNGs.
"""

import asyncio
import omni.replicator.core as rep

# Camera prim paths
cameras = {
    "overhead": "/World/SecurityCameras/Camera_Overhead",
    "forklift": "/World/SecurityCameras/Camera_ForkLift",
    "loading_dock": "/World/SecurityCameras/Camera_LoadingDock",
}

# Create render products for each camera
render_products = []
for name, cam_path in cameras.items():
    rp = rep.create.render_product(cam_path, (1280, 720))
    render_products.append(rp)
    print(f"Created render product for {name}: {cam_path}")

# Set up writer to save RGB frames
writer = rep.WriterRegistry.get("BasicWriter")
writer.initialize(
    output_dir="/workspace/camera_feeds",
    rgb=True,
)
writer.attach(render_products)


async def capture():
    await rep.orchestrator.step_async()
    print("\nFrame capture complete! Check /workspace/camera_feeds/ for output.")


asyncio.ensure_future(capture())
print("Capture scheduled...")
