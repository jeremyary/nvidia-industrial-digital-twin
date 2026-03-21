"""Remove all alert prims so they can be recreated cleanly."""
import omni.usd

stage = omni.usd.get_context().get_stage()
alerts_prim = stage.GetPrimAtPath("/World/Alerts")
if alerts_prim.IsValid():
    stage.RemovePrim("/World/Alerts")
    print("Removed /World/Alerts")
else:
    print("/World/Alerts not found")

# Also remove any leftover demo worker
worker_prim = stage.GetPrimAtPath("/World/DemoWorker")
if worker_prim.IsValid():
    stage.RemovePrim("/World/DemoWorker")
    print("Removed /World/DemoWorker")

print("Done. Now run create_alerts.py to recreate with fixed positions.")
